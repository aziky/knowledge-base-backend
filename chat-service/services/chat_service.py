import logging
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from config.config import db
from sqlalchemy import text as sql_text
import os
from dotenv import load_dotenv
import json


class ChatService:
    def __init__(self):
        load_dotenv()
        
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        
        # Initialize embedding model (same as EmbeddingService for consistency)
        self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.logger.info("Embedding model loaded for chat service")
        
        # Initialize Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        self.logger.info("Gemini model initialized")

    def _search_similar_chunks(self, query, project_id=None, limit=5, similarity_threshold=0.7):
        """
        Search for similar document chunks based on query vector similarity.
        
        Args:
            query (str): User's question
            project_id (str, optional): Filter by project ID if available
            limit (int): Maximum number of chunks to return
            similarity_threshold (float): Minimum similarity score (0-1)
            
        Returns:
            list: List of similar document chunks with content and metadata
        """
        try:
            # Step 1: Convert query to embedding vector
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            self.logger.info(f"Generated query embedding vector (length: {len(query_embedding)})")
            
            # Step 2: Perform vector similarity search using PostgreSQL pgvector
            similarity_query = sql_text("""
                SELECT 
                    chunk_id,
                    document_id,
                    content,
                    chunk_index,
                    metadata,
                    (1 - (embedding <=> CAST(:query_vector AS vector))) as similarity
                FROM kb_chat.document_chunks
                WHERE (1 - (embedding <=> CAST(:query_vector AS vector))) > :threshold
                ORDER BY embedding <=> CAST(:query_vector AS vector)
                LIMIT :limit
            """)
            
            def _search_chunks():
                # Convert embedding to PostgreSQL vector format
                vector_str = '[' + ','.join(map(str, query_embedding)) + ']'
                
                result = db.session.execute(similarity_query, {
                    "query_vector": vector_str,
                    "threshold": similarity_threshold,
                    "limit": limit
                })
                
                chunks = []
                for row in result:
                    chunk_data = {
                        "chunk_id": str(row.chunk_id),
                        "document_id": str(row.document_id),
                        "content": row.content,
                        "chunk_index": row.chunk_index,
                        "metadata": json.loads(row.metadata) if row.metadata else {},
                        "similarity": float(row.similarity)
                    }
                    chunks.append(chunk_data)
                
                return chunks
            
            # Execute search (assuming we're in Flask request context)
            chunks = _search_chunks()
            
            self.logger.info(f"Found {len(chunks)} similar chunks for query")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error searching similar chunks: {e}")
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
            content = chunk['content'].strip()
            
            # Add chunk with similarity info
            context_parts.append(f"[Document {i}] (Relevance: {similarity_score:.2f})\n{content}")
        
        combined_context = "\n\n".join(context_parts)
        self.logger.info(f"Generated context from {len(chunks)} chunks (total length: {len(combined_context)} chars)")
        
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
            self.logger.info("Sending request to Gemini...")
            
            response = self.gemini_model.generate_content(enhanced_prompt)
            
            if response.candidates and response.candidates[0].content:
                answer = response.candidates[0].content.parts[0].text
                self.logger.info(f"Received response from Gemini (length: {len(answer)} chars)")
                
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
            self.logger.error(f"Error calling Gemini: {e}")
            return {
                "answer": "I'm experiencing technical difficulties. Please try again later.",
                "status": "error",
                "error": str(e),
                "model": "gemini-2.5-flash"
            }

    def process_chat_query(self, user_question, project_id=None, user_id=None):
        """
        Main method to process a chat query with RAG (Retrieval-Augmented Generation).
        
        Args:
            user_question (str): User's question
            project_id (str, optional): Project ID for filtering
            user_id (str, optional): User ID for logging
            
        Returns:
            dict: Complete response with answer, sources, and metadata
        """
        try:
            self.logger.info(f"Processing chat query from user: {user_question[:100]}...")
            
            # Step 1: Search for similar chunks
            similar_chunks = self._search_similar_chunks(
                query=user_question,
                project_id=project_id,
                limit=5,
                similarity_threshold=0.6
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
                        "chunk_id": chunk["chunk_id"],
                        "document_id": chunk["document_id"],
                        "similarity": chunk["similarity"],
                        "content_preview": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"]
                    }
                    for chunk in similar_chunks
                ],
                "metadata": {
                    "query": user_question,
                    "chunks_found": len(similar_chunks),
                    "gemini_status": gemini_response["status"],
                    "user_id": user_id,
                    "project_id": project_id
                }
            }
            
            self.logger.info(f"Chat query processed successfully for user {user_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing chat query: {e}")
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "sources": [],
                "metadata": {
                    "error": str(e),
                    "status": "error"
                }
            }