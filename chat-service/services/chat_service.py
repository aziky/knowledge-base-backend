import logging
import google.generativeai as genai
from langchain_postgres import PGVector
from langchain_core.documents import Document
import os
from dotenv import load_dotenv
import json
import requests
from flask import request
from services.embedding_service import SentenceTransformerEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
import uuid
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from config.config import db
from repository.entitty.conversation import Conversation
from repository.entitty.message import Message


class ChatService:
    def __init__(self):
        load_dotenv()

        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

        # Initialize embedding model (same as EmbeddingService for consistency)
        self.embedding_model = SentenceTransformerEmbeddings("sentence-transformers/all-MiniLM-L6-v2")
        self.logger.info("Embedding model loaded for chat service")

        # Initialize vector stores (will be created when needed)
        self.document_vectorstore = None
        self.video_vectorstore = None
        self.connection_string = os.getenv("DATABASE_URL")

        # Initialize Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        self.logger.info("Gemini model initialized")

        # Project Service configuration
        self.project_service_url = os.getenv("PROJECT_SERVICE_URL", "http://localhost:7072/api")
        self.api_secret = os.getenv("INTERNAL_API_SECRET")
        
        # Conversation memory storage
        # In production, consider using Redis or database for persistence
        self.conversations = {}  # conversation_id -> memory object
        self.conversation_metadata = {}  # conversation_id -> metadata
        self.conversation_timeout = timedelta(hours=24)  # Conversations expire after 24 hours
    
    def _get_document_vectorstore(self):
        """Get or create the document vector store"""
        if self.document_vectorstore is None:
            self.document_vectorstore = PGVector(
                embeddings=self.embedding_model,
                connection=self.connection_string,
                collection_name="document_chunks",
                use_jsonb=True,
            )
        return self.document_vectorstore
    
    def _get_video_vectorstore(self):
        """Get or create the video vector store"""
        if self.video_vectorstore is None:
            self.video_vectorstore = PGVector(
                embeddings=self.embedding_model,
                connection=self.connection_string,
                collection_name="video_chunks",
                use_jsonb=True,
            )
        return self.video_vectorstore

    def create_conversation(self, project_id=None):
        """
        Create a new conversation session.
        
        Args:
            project_id (str, optional): Project ID to associate with the conversation
            
        Returns:
            str: Unique conversation ID
        """
        conversation_id = str(uuid.uuid4())
        
        # Initialize memory with a window of last 10 exchanges (20 messages total)
        memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True,
            memory_key="chat_history"
        )
        
        self.conversations[conversation_id] = memory
        self.conversation_metadata[conversation_id] = {
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
            "project_id": project_id,
            "message_count": 0
        }
        
        self.logger.info(f"Created conversation {conversation_id} for project {project_id}")
        return conversation_id

    def get_conversation_memory(self, conversation_id):
        """
        Get memory object for a conversation, cleaning up expired conversations.
        
        Args:
            conversation_id (str): Conversation ID
            
        Returns:
            ConversationBufferWindowMemory or None: Memory object if found and valid
        """
        self._cleanup_expired_conversations()
        
        if conversation_id not in self.conversations:
            self.logger.warning(f"Conversation {conversation_id} not found")
            return None
            
        # Update last accessed time
        self.conversation_metadata[conversation_id]["last_accessed"] = datetime.utcnow()
        
        return self.conversations[conversation_id]

    def _cleanup_expired_conversations(self):
        """Remove expired conversations to prevent memory leaks."""
        current_time = datetime.utcnow()
        expired_conversations = []
        
        for conv_id, metadata in self.conversation_metadata.items():
            if current_time - metadata["last_accessed"] > self.conversation_timeout:
                expired_conversations.append(conv_id)
        
        for conv_id in expired_conversations:
            del self.conversations[conv_id]
            del self.conversation_metadata[conv_id]
            
        if expired_conversations:
            self.logger.info(f"Cleaned up {len(expired_conversations)} expired conversations")

    def get_conversation_history(self, conversation_id):
        """
        Get formatted conversation history.
        
        Args:
            conversation_id (str): Conversation ID
            
        Returns:
            str: Formatted conversation history
        """
        memory = self.get_conversation_memory(conversation_id)
        if not memory:
            return ""
            
        try:
            messages = memory.chat_memory.messages
            if not messages:
                return ""
                
            history_parts = []
            for message in messages:
                if isinstance(message, HumanMessage):
                    history_parts.append(f"Human: {message.content}")
                elif isinstance(message, AIMessage):
                    history_parts.append(f"Assistant: {message.content}")
                    
            return "\n".join(history_parts)
            
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {e}")
            return ""

    def store_conversation_to_database(self, conversation_id, user_id, user_question, bot_answer, 
                                      title=None, gemini_metadata=None):
        """
        Store a chat conversation exchange (user question + bot response) to the database.
        Creates a new conversation record if it doesn't exist, then adds both messages.
        
        Args:
            conversation_id (str): Unique conversation ID
            user_id (str): UUID of the user
            user_question (str): User's question/message
            bot_answer (str): Bot's response
            title (str, optional): Conversation title (auto-generated if not provided)
            gemini_metadata (dict, optional): Metadata about the Gemini response (model, tokens, etc.)
            
        Returns:
            dict: Result with success status and stored message IDs
        """
        try:
            # Check if conversation exists
            conversation = Conversation.query.filter_by(id=conversation_id).first()
            
            if not conversation:
                # Create new conversation
                conversation = Conversation(
                    id=conversation_id,
                    user_id=user_id,
                    title=title,
                    status='ACTIVE',
                    started_at=datetime.utcnow()
                )
                db.session.add(conversation)
                self.logger.info(f"Created new conversation {conversation_id} for user {user_id}")
            
            # Store user message
            user_message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                sender_type='USER',
                content=user_question,
                created_at=datetime.utcnow(),
                message_metadata=None
            )
            db.session.add(user_message)
            
            # Store bot message
            bot_message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                sender_type='BOT',
                content=bot_answer,
                created_at=datetime.utcnow(),
                message_metadata=gemini_metadata
            )
            db.session.add(bot_message)
            
            # Commit all changes
            db.session.commit()
            
            self.logger.info(f"Stored conversation exchange for {conversation_id}: "
                           f"user_msg={user_message.id}, bot_msg={bot_message.id}")
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'user_message_id': user_message.id,
                'bot_message_id': bot_message.id,
                'message': 'Conversation stored successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error storing conversation to database: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'conversation_id': conversation_id
            }

    def get_conversation_from_database(self, conversation_id):
        """
        Retrieve a conversation and all its messages from the database.
        
        Args:
            conversation_id (str): Conversation ID to retrieve
            
        Returns:
            dict: Conversation data with messages and raw objects for memory loading, or None if not found
        """
        try:
            # Build query
            query = Conversation.query.filter_by(id=conversation_id)
            
            conversation = query.first()
            
            if not conversation:
                self.logger.warning(f"Conversation {conversation_id} not found in database")
                return None
            
            # Get all messages for this conversation, ordered by creation time
            messages = Message.query.filter_by(
                conversation_id=conversation_id
            ).order_by(Message.created_at.asc()).all()
            
            return {
                'conversation': {
                    'id': str(conversation.id) if conversation.id else None,
                    'user_id': str(conversation.user_id) if conversation.user_id else None,
                    'title': conversation.title,
                    'status': conversation.status,
                    'started_at': conversation.started_at.isoformat() if conversation.started_at else None,
                    'ended_at': conversation.ended_at.isoformat() if conversation.ended_at else None
                },
                'messages': [msg.to_dict() for msg in messages],
                'message_count': len(messages)
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving conversation from database: {str(e)}")
            return None

    def get_user_conversations(self, user_id, status='ACTIVE', limit=20, offset=0):
        """
        Get all conversations for a specific user.
        
        Args:
            user_id (str): User ID
            status (str, optional): Filter by status (ACTIVE, CLOSED, ARCHIVED)
            limit (int): Maximum number of conversations to return
            offset (int): Number of conversations to skip (for pagination)
            
        Returns:
            dict: List of conversations with message counts
        """
        try:
            query = Conversation.query.filter_by(user_id=user_id, status=status)
            query = query.order_by(Conversation.started_at.desc())
            
            # Apply pagination
            total_count = query.count()
            conversations = query.limit(limit).offset(offset).all()
            
            result = []
            for conv in conversations:
                
                customer_conv = {
                    'conversation_id': str(conv.id) if conv.id else None,
                    'title': conv.title,
                    'status': conv.status,
                    'created_at': conv.started_at.isoformat() if conv.started_at else None
                }
                result.append(customer_conv)

            return {
                'conversations': result,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving user conversations: {str(e)}")
            return {
                'conversations': [],
                'total_count': 0,
                'error': str(e)
            }

    def summarize_conversation(self, conversation_id):
        """
        Summarize a conversation using Gemini AI and store the summary in the database.
        
        Args:
            conversation_id (str): Conversation ID to summarize
            
        Returns:
            dict: Response with summary status and data
        """
        try:
            self.logger.info(f"Starting conversation summary for {conversation_id}")
            
            # Get conversation memory and validate
            memory = self.get_conversation_memory(conversation_id)
            if not memory:
                return {
                    "success": False,
                    "error": "Conversation not found or expired",
                    "conversation_id": conversation_id
                }
            
            # Get conversation metadata
            metadata = self.conversation_metadata.get(conversation_id, {})
            if metadata.get("message_count", 0) < 2:
                return {
                    "success": False,
                    "error": "Conversation too short to summarize (needs at least 1 exchange)",
                    "conversation_id": conversation_id
                }
            
            # Get full conversation history
            conversation_history = self.get_conversation_history(conversation_id)
            if not conversation_history:
                return {
                    "success": False,
                    "error": "No conversation history found",
                    "conversation_id": conversation_id
                }
            
            # Create summary prompt for Gemini
            summary_prompt = self._create_summary_prompt(conversation_history)
            
            # Get summary from Gemini
            summary_response = self._get_conversation_summary_from_gemini(summary_prompt)
            
            if summary_response["status"] != "success":
                return {
                    "success": False,
                    "error": f"Failed to generate summary: {summary_response.get('error', 'Unknown error')}",
                    "conversation_id": conversation_id
                }
            
            # Store summary in database
            summary_id = self._store_conversation_summary(
                conversation_id=conversation_id,
                summary_text=summary_response["summary"],
                project_id=metadata.get("project_id"),
                message_count=metadata.get("message_count", 0),
                created_at=metadata.get("created_at"),
                summarized_at=datetime.utcnow()
            )
            
            self.logger.info(f"Conversation {conversation_id} summarized successfully with ID {summary_id}")
            
            return {
                "success": True,
                "summary_id": summary_id,
                "conversation_id": conversation_id,
                "summary": summary_response["summary"],
                "message_count": metadata.get("message_count", 0),
                "project_id": metadata.get("project_id")
            }
            
        except Exception as e:
            self.logger.error(f"Error summarizing conversation {conversation_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }

    def _create_summary_prompt(self, conversation_history):
        """
        Create a prompt for Gemini to summarize the conversation.
        
        Args:
            conversation_history (str): Full conversation history
            
        Returns:
            str: Summary prompt for Gemini
        """
        prompt = f"""Please provide a comprehensive summary of this conversation between a human and an AI assistant. 

CONVERSATION HISTORY:
{conversation_history}

SUMMARY REQUIREMENTS:
• Capture the main topics discussed and key questions asked
• Include important information or insights that were shared
• Note any specific documents, videos, or resources that were referenced
• Highlight key decisions, conclusions, or action items if any
• Keep the summary concise but comprehensive (2-4 paragraphs)
• Use a professional, informative tone
• Focus on the substantive content rather than conversational pleasantries

Please provide only the summary without any preamble or additional commentary."""

        return prompt

    def _get_conversation_summary_from_gemini(self, summary_prompt):
        """
        Get conversation summary from Gemini AI.
        
        Args:
            summary_prompt (str): Prompt for generating summary
            
        Returns:
            dict: Response with summary and status
        """
        try:
            self.logger.info("Requesting conversation summary from Gemini...")
            
            response = self.gemini_model.generate_content(summary_prompt)
            
            if response.candidates and response.candidates[0].content:
                summary = response.candidates[0].content.parts[0].text.strip()
                self.logger.info(f"Gemini summary generated ({len(summary)} chars)")
                
                return {
                    "summary": summary,
                    "status": "success",
                    "model": "gemini-2.5-flash"
                }
            else:
                self.logger.warning("Empty summary response from Gemini")
                return {
                    "summary": "",
                    "status": "empty_response",
                    "error": "No summary generated"
                }
                
        except Exception as e:
            self.logger.error(f"Gemini summary error: {str(e)}")
            return {
                "summary": "",
                "status": "error",
                "error": str(e)
            }

    def _store_conversation_summary(self, conversation_id, summary_text, project_id=None, 
                                  message_count=0, created_at=None, summarized_at=None):
        """
        Store conversation summary in the database.
        
        Args:
            conversation_id (str): Conversation ID
            summary_text (str): Generated summary
            project_id (str, optional): Associated project ID
            message_count (int): Number of messages in conversation
            created_at (datetime, optional): When conversation was created
            summarized_at (datetime, optional): When summary was generated
            
        Returns:
            str: Summary ID from database
        """
        try:
            # Create database connection
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Create table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS conversation_summaries (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                conversation_id VARCHAR(255) UNIQUE NOT NULL,
                project_id VARCHAR(255),
                summary_text TEXT NOT NULL,
                message_count INTEGER DEFAULT 0,
                conversation_created_at TIMESTAMP,
                summarized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_conversation_summaries_conversation_id 
            ON conversation_summaries(conversation_id);
            
            CREATE INDEX IF NOT EXISTS idx_conversation_summaries_project_id 
            ON conversation_summaries(project_id);
            """
            
            cursor.execute(create_table_query)
            
            # Insert or update summary
            upsert_query = """
            INSERT INTO conversation_summaries 
            (conversation_id, project_id, summary_text, message_count, conversation_created_at, summarized_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (conversation_id) 
            DO UPDATE SET 
                summary_text = EXCLUDED.summary_text,
                message_count = EXCLUDED.message_count,
                summarized_at = EXCLUDED.summarized_at,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id;
            """
            
            cursor.execute(upsert_query, (
                conversation_id,
                project_id,
                summary_text,
                message_count,
                created_at,
                summarized_at or datetime.utcnow()
            ))
            
            summary_id = cursor.fetchone()['id']
            
            # Commit changes
            conn.commit()
            cursor.close()
            conn.close()
            
            self.logger.info(f"Stored conversation summary with ID: {summary_id}")
            return str(summary_id)
            
        except Exception as e:
            self.logger.error(f"Error storing conversation summary: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
            raise

    def get_conversation_summary(self, conversation_id):
        """
        Retrieve stored conversation summary from database.
        
        Args:
            conversation_id (str): Conversation ID
            
        Returns:
            dict: Summary data or None if not found
        """
        try:
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT id, conversation_id, project_id, summary_text, message_count,
                   conversation_created_at, summarized_at, created_at, updated_at
            FROM conversation_summaries 
            WHERE conversation_id = %s
            """
            
            cursor.execute(query, (conversation_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                return dict(result)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving conversation summary: {str(e)}")
            if 'conn' in locals():
                cursor.close()
                conn.close()
            return None

    def _get_project_details(self, project_id):
        """
        Call Project Service API to get project details including document and video IDs.
        
        Args:
            project_id (str): Project UUID
            
        Returns:
            dict: Project details with document_ids and video_ids lists
            
        Raises:
            Exception: If API call fails
        """
        user_headers = getattr(request, 'user_headers', {})
        api_url = f"{self.project_service_url}/project/{project_id}"
        headers = {
            # "X-Internal-Secret": self.api_secret,
            "Accept": "application/json",
            **user_headers
        }

        self.logger.info(f"Fetching project details from: {api_url}")

        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()

            api_data = response.json()
            project_data = api_data.get('data', {})

            # Extract document IDs from documents list (only COMPLETED status)
            documents = project_data.get('documents', [])
            document_ids = [
                doc['id'] for doc in documents 
                if doc.get('status') == 'COMPLETED'
            ]

            # Extract video IDs from videos list (only COMPLETED status)
            videos = project_data.get('videos', [])
            video_ids = [
                video['id'] for video in videos 
                if video.get('status') == 'COMPLETED'
            ]

            self.logger.info(
                f"Project {project_id}: {len(document_ids)} documents, {len(video_ids)} videos"
            )

            return {
                "document_ids": document_ids,
                "video_ids": video_ids,
                "project_name": project_data.get('projectName'),
                "description": project_data.get('description')
            }

        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"HTTP error fetching project details: {http_err}")
            raise

        except requests.exceptions.RequestException as req_err:
            self.logger.error(f"Error fetching project details: {req_err}")
            raise

    def _search_similar_chunks(self, query, document_ids=None, video_ids=None, limit=5, similarity_threshold=0.2):
        """
        Search for similar chunks in both document_chunks and video_chunks using LangChain vector stores.
        
        Args:
            query (str): User's question
            document_ids (list, optional): Filter by list of document IDs if available
            video_ids (list, optional): Filter by list of video IDs if available
            limit (int): Maximum number of chunks to return
            similarity_threshold (float): Minimum similarity score (0-1)
            
        Returns:
            list: List of similar chunks (both documents and videos) with content and metadata
        """
        try:
            self.logger.info(f"Searching: '{query}' | Threshold: {similarity_threshold} | Documents: {len(document_ids) if document_ids else 'ALL'} | Videos: {len(video_ids) if video_ids else 'ALL'}")

            all_chunks = []

            # Search document chunks
            if document_ids:
                self.logger.info(f"Searching document chunks...")
                doc_vectorstore = self._get_document_vectorstore()
                
                # Build filter for document IDs
                doc_filter = None
                if document_ids and len(document_ids) > 0:
                    doc_filter = {"document_id": {"$in": document_ids}}
                
                # Perform similarity search
                doc_results = doc_vectorstore.similarity_search_with_score(
                    query=query,
                    k=limit,
                    filter=doc_filter
                )
                
                for doc, score in doc_results:
                    # Convert distance to similarity (higher is better)
                    similarity = 1.0 - score if score <= 1.0 else 0.0
                    
                    if similarity >= similarity_threshold:
                        chunk_data = {
                            "source_id": doc.metadata.get("document_id"),
                            "source_type": "document",
                            "content": doc.page_content,
                            "chunk_index": doc.metadata.get("chunk_index", 0),
                            "metadata": doc.metadata,
                            "similarity": similarity
                        }
                        all_chunks.append(chunk_data)

            # Search video chunks
            if video_ids:
                self.logger.info(f"Searching video chunks...")
                video_vectorstore = self._get_video_vectorstore()
                
                # Build filter for video IDs
                video_filter = None
                if video_ids and len(video_ids) > 0:
                    video_filter = {"video_id": {"$in": video_ids}}
                
                # Perform similarity search
                video_results = video_vectorstore.similarity_search_with_score(
                    query=query,
                    k=limit,
                    filter=video_filter
                )
                
                for doc, score in video_results:
                    # Convert distance to similarity (higher is better)
                    similarity = 1.0 - score if score <= 1.0 else 0.0
                    
                    if similarity >= similarity_threshold:
                        chunk_data = {
                            "source_id": doc.metadata.get("video_id"),
                            "source_type": "video",
                            "content": doc.page_content,
                            "chunk_index": doc.metadata.get("chunk_index", 0),
                            "metadata": doc.metadata,
                            "similarity": similarity
                        }
                        all_chunks.append(chunk_data)

            # Sort all chunks by similarity and take top N
            all_chunks.sort(key=lambda x: x['similarity'], reverse=True)
            all_chunks = all_chunks[:limit]

            # Summary logging
            if all_chunks:
                doc_count = sum(1 for c in all_chunks if c['source_type'] == 'document')
                video_count = sum(1 for c in all_chunks if c['source_type'] == 'video')
                self.logger.info(f"Found {len(all_chunks)} chunks ({doc_count} docs, {video_count} videos) | similarity: {all_chunks[0]['similarity']:.3f} - {all_chunks[-1]['similarity']:.3f}")
            else:
                self.logger.info(f"No chunks passed threshold {similarity_threshold}")
            
            return all_chunks

        except Exception as e:
            self.logger.error(f"Error searching chunks: {str(e)}")
            return []

    def _generate_context_from_chunks(self, chunks):
        """
        Combine content from similar chunks into a coherent context.
        
        Args:
            chunks (list): List of chunk dictionaries
            
        Returns:
            str: Combined context text
        """
        if not chunks:
            return "No relevant information found in the knowledge base."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            similarity_score = chunk.get('similarity', 0)
            source_type = chunk.get('source_type', 'document')
            content = chunk['content'].strip()
            source_label = "Video Transcript" if source_type == 'video' else "Document"
            context_parts.append(f"[{source_label} {i}] (Relevance: {similarity_score:.2f})\n{content}")

        combined_context = "\n\n".join(context_parts)
        self.logger.info(f"Generated context: {len(chunks)} chunks, {len(combined_context)} chars")

        return combined_context

    def _create_enhanced_prompt(self, user_question, context, conversation_history=""):
        """
        Create an enhanced prompt combining user question with retrieved context and conversation history.
        
        Args:
            user_question (str): Original user question
            context (str): Retrieved context from similar chunks
            conversation_history (str): Previous conversation context
            
        Returns:
            str: Enhanced prompt for Gemini
        """
        prompt_parts = [
            "You are a knowledgeable assistant with access to a knowledge base. Answer the user's question based on the provided context information and previous conversation."
        ]
        
        if conversation_history:
            prompt_parts.extend([
                "\nPrevious Conversation:",
                conversation_history,
                "\n" + "="*50
            ])
            
        prompt_parts.extend([
            "\nRelevant Information:",
            context,
            f"\nUser Question: {user_question}",
            "\nResponse Guidelines:",
            "• Answer naturally and conversationally - avoid starting with phrases like 'Based on the provided context' or 'According to the information'",
            "• Speak directly about the topic as if you're an expert explaining it to a colleague",
            "• Use the conversation history to build upon previous exchanges naturally",
            "• When referencing information from documents or videos, weave it seamlessly into your explanation",
            "• If information is incomplete, say what you know and then mention what's missing",
            "• Use a confident, helpful tone while being honest about limitations",
            "• Structure your response clearly with paragraphs and lists when helpful",
            "• Make it feel like a natural conversation, not a formal report",
            "\nProvide a helpful, direct response:"
        ])

        return "\n".join(prompt_parts)

    def _chat_with_gemini(self, enhanced_prompt):
        """
        Send enhanced prompt to Gemini and get response.
        
        Args:
            enhanced_prompt (str): Prompt with context and question
            
        Returns:
            dict: Response with answer and metadata
        """
        try:
            self.logger.info("Calling Gemini AI...")
 
            response = self.gemini_model.generate_content(enhanced_prompt)

            if response.candidates and response.candidates[0].content:
                answer = response.candidates[0].content.parts[0].text
                self.logger.info(f"Gemini response received ({len(answer)} chars)")

                return {
                    "answer": answer,
                    "status": "success",
                    "model": "gemini-2.5-flash"
                }
            else:
                self.logger.warning("Empty response from Gemini")
                return {
                    "answer": "I couldn't generate a response. Please try rephrasing your question.",
                    "status": "empty_response",
                    "model": "gemini-2.5-flash"
                }

        except Exception as e:
            self.logger.error(f"Gemini error: {str(e)}")
            return {
                "answer": "I'm experiencing technical difficulties. Please try again later.",
                "status": "error",
                "error": str(e),
                "model": "gemini-2.5-flash"
            }

    def process_chat_query(self, user_question, user_id, project_id=None, document_ids=None, video_ids=None, conversation_id=None):
        """
        Main method to process a chat query with RAG (Retrieval-Augmented Generation) and conversation memory.
        
        Args:
            user_question (str): User's question
            user_id (str): User ID from JWT token
            project_id (str): Project ID (required to fetch documents and videos)
            document_ids (list, optional): Override document IDs (if not provided, fetched from project)
            video_ids (list, optional): Override video IDs (if not provided, fetched from project)
            conversation_id (str, optional): Conversation ID for maintaining context
            
        Returns:
            dict: Complete response with answer, sources, metadata, and conversation_id
        """
        try:
            self.logger.info(f"Chat Query: '{user_question[:100]}...' | Project: {project_id} | Conversation: {conversation_id}")

            # Create new conversation if not provided
            if not conversation_id:
                conversation_id = self.create_conversation(project_id)
                self.logger.info(f"Created new conversation: {conversation_id}")

            # Get conversation memory (check in-memory first)
            memory = self.get_conversation_memory(conversation_id)
            
            if not memory:
                # Memory not in cache - check if conversation exists in database
                self.logger.info(f"Conversation {conversation_id} not in memory, checking database...")
                db_conversation = self.get_conversation_from_database(conversation_id)
                
                if db_conversation:
                    # Conversation exists in database - load it into memory
                    self.logger.info(f"Found conversation {conversation_id} in database, loading into memory...")
                    
                    # Create new memory for this conversation
                    memory = ConversationBufferWindowMemory(
                        k=10,  # Keep last 10 exchanges
                        return_messages=True,
                        memory_key="chat_history"
                    )
                    
                    # Load messages from database into memory
                    messages = db_conversation.get('messages', [])
                    for msg in messages:
                        if msg['sender_type'] == 'USER':
                            memory.chat_memory.add_user_message(msg['content'])
                        elif msg['sender_type'] == 'BOT':
                            memory.chat_memory.add_ai_message(msg['content'])
                    
                    # Store in memory cache
                    self.conversations[conversation_id] = memory
                    self.conversation_metadata[conversation_id] = {
                        "created_at": db_conversation['conversation'].get('started_at'),
                        "last_accessed": datetime.utcnow(),
                        "project_id": project_id,
                        "message_count": db_conversation.get('message_count', 0)
                    }
                    
                    self.logger.info(f"Loaded {db_conversation.get('message_count', 0)} messages into memory for conversation {conversation_id}")
                else:
                    # Conversation doesn't exist in database either - create new one
                    self.logger.info(f"Conversation {conversation_id} not found in database, creating new one...")
                    conversation_id = self.create_conversation(project_id)
                    memory = self.get_conversation_memory(conversation_id)

            # Get conversation history for context
            conversation_history = self.get_conversation_history(conversation_id)

            # Fetch project details if document_ids or video_ids not provided
            if project_id:
                self.logger.info(f"Fetching project details for project_id: {project_id}")
                project_details = self._get_project_details(project_id)
                document_ids =  project_details.get("document_ids", [])
                video_ids = project_details.get("video_ids", [])
            
            self.logger.info(f"[DEBUG] After project lookup: document_ids={document_ids}, video_ids={video_ids}")

            # Step 1: Search for similar chunks (both documents and videos)
            similar_chunks = self._search_similar_chunks(
                query=user_question,
                document_ids=document_ids,
                video_ids=video_ids,
                limit=5,
                similarity_threshold=0.2
            )

            # Step 2: Generate context from chunks
            context = self._generate_context_from_chunks(similar_chunks)

            # Step 3: Create enhanced prompt with conversation history
            enhanced_prompt = self._create_enhanced_prompt(user_question, context, conversation_history)

            # Step 4: Get response from Gemini
            gemini_response = self._chat_with_gemini(enhanced_prompt)

            # Step 5: Save conversation to memory
            memory.chat_memory.add_user_message(user_question)
            memory.chat_memory.add_ai_message(gemini_response["answer"])
            
            # Update conversation metadata
            self.conversation_metadata[conversation_id]["message_count"] += 2
            self.conversation_metadata[conversation_id]["last_accessed"] = datetime.utcnow()

            # Step 5.5: Store conversation in database
            gemini_metadata = {
                "model": gemini_response.get("model", "gemini-2.5-flash"),
                "status": gemini_response.get("status"),
                "chunks_used": len(similar_chunks),
                "project_id": project_id
            }
            
            storage_result = self.store_conversation_to_database(
                conversation_id=conversation_id,
                user_id=user_id,
                user_question=user_question,
                bot_answer=gemini_response["answer"],
                title=f"{user_question[:50]}..." if len(user_question) > 50 else user_question,
                gemini_metadata=gemini_metadata
            )
            
            if not storage_result.get('success'):
                self.logger.warning(f"Failed to store conversation to database: {storage_result.get('error')}")

            # Step 6: Prepare final response
            response = {
                "answer": gemini_response["answer"],
                "conversation_id": conversation_id,
                "sources": [
                    {
                        "source_id": chunk["source_id"],
                        "source_type": chunk["source_type"],
                        "similarity": chunk["similarity"],
                        "content_preview": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"]
                    }
                    for chunk in similar_chunks
                ],
                "metadata": {
                    "query": user_question,
                    "chunks_found": len(similar_chunks),
                    "gemini_status": gemini_response["status"],
                    "project_id": project_id,
                    "document_ids": document_ids,
                    "video_ids": video_ids,
                    "conversation_message_count": self.conversation_metadata[conversation_id]["message_count"],
                    "has_conversation_history": bool(conversation_history)
                }
            }

            self.logger.info(f"Query processed successfully with conversation context")
            return response

        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "conversation_id": conversation_id if 'conversation_id' in locals() else None,
                "sources": [],
                "metadata": {
                    "error": str(e),
                    "status": "error"
                }              
            }               
