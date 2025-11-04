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

    def _create_enhanced_prompt(self, user_question, context):
        """
        Create an enhanced prompt combining user question with retrieved context.
        
        Args:
            user_question (str): Original user question
            context (str): Retrieved context from similar chunks
            
        Returns:
            str: Enhanced prompt for Gemini
        """
        prompt = f"""You are a knowledgeable assistant with access to a knowledge base. Answer the user's question based on the provided context information.
Context Information:
{context}
User Question: {user_question}
Instructions:
1. Answer based primarily on the provided context
2. If the context doesn't contain enough information, clearly state what information is missing
3. Be concise but comprehensive
4. Include relevant details from the context
5. If you're unsure about something, indicate your uncertainty
6. Format your response clearly with proper paragraphs and structure
7. Use bullet points or numbered lists when appropriate for better readability
Answer:"""

        return prompt

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

    def process_chat_query(self, user_question, project_id=None, document_ids=None, video_ids=None):
        """
        Main method to process a chat query with RAG (Retrieval-Augmented Generation).
        
        Args:
            user_question (str): User's question
            project_id (str): Project ID (required to fetch documents and videos)
            document_ids (list, optional): Override document IDs (if not provided, fetched from project)
            video_ids (list, optional): Override video IDs (if not provided, fetched from project)
            
        Returns:
            dict: Complete response with answer, sources, and metadata
        """
        try:
            self.logger.info(f"Chat Query: '{user_question[:100]}...' | Project: {project_id}")

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

            # Step 3: Create enhanced prompt
            enhanced_prompt = self._create_enhanced_prompt(user_question, context)

            # Step 4: Get response from Gemini
            gemini_response = self._chat_with_gemini(enhanced_prompt)

            # Step 5: Prepare final response
            response = {
                "answer": gemini_response["answer"],
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
                    "video_ids": video_ids
                }
            }

            self.logger.info(f"Query processed successfully")
            return response

        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "sources": [],
                "metadata": {
                    "error": str(e),
                    "status": "error"


                }              
            }               
