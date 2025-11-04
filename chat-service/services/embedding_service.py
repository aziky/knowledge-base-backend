import os
import logging
from datetime import datetime

from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class SentenceTransformerEmbeddings(Embeddings):
    """Wrapper to make SentenceTransformer compatible with LangChain's Embeddings interface"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents"""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return [embedding.tolist() for embedding in embeddings]
    
    def embed_query(self, text: str) -> list[float]:
        """Embed a single query text"""
        embedding = self.model.encode([text])
        return embedding[0].tolist()


class EmbeddingService:
    def __init__(self, app=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        
        self.app = app  # Store Flask app instance

        # Initialize embedding model
        self.embedding_model = SentenceTransformerEmbeddings("sentence-transformers/all-MiniLM-L6-v2")
        self.logger.info("Embedding model loaded successfully")
        
        # Initialize vector stores (will be created when needed)
        self.document_vectorstore = None
        self.video_vectorstore = None

    def _get_connection_string(self):
        """Get the database connection string from environment"""
        return os.getenv("DATABASE_URL")
    
    def _get_document_vectorstore(self):
        """Get or create the document vector store"""
        if self.document_vectorstore is None:
            # PGVector creates its own table structure, not compatible with existing kb_chat tables
            # We need to use a different approach or revert to manual SQL
            self.document_vectorstore = PGVector(
                embeddings=self.embedding_model,
                connection=self._get_connection_string(),
                collection_name="document_chunks",  # Different table name to avoid conflicts
                use_jsonb=True,
            )
        return self.document_vectorstore
    
    def _get_video_vectorstore(self):
        """Get or create the video vector store"""
        if self.video_vectorstore is None:
            self.logger.warning("PGVector creates its own table structure, not compatible with existing kb_chat.video_chunks")
            self.video_vectorstore = PGVector(
                embeddings=self.embedding_model,
                connection=self._get_connection_string(),
                collection_name="video_chunks",  # Different table name to avoid conflicts
                use_jsonb=True,
            )
        return self.video_vectorstore 


    def chunk_and_embed(self, document_id, text, project_id, chunk_size=1000, chunk_overlap=200):
        """
        Split text into chunks, generate embeddings, and store them using LangChain PGVector.
        
        Args:
            document_id (str): Document ID
            text (str): Text content to chunk and embed
            project_id (str): Project ID that contains this document
            chunk_size (int): Size of each chunk
            chunk_overlap (int): Overlap between chunks
        """
        if not text:
            self.logger.warning(f"No text provided for document {document_id}")
            raise Exception(f"No text provided for document {document_id}")

        try:
            # Step 1. Split into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ".", "!", "?", " "]
            )
            chunks = splitter.split_text(text)
            self.logger.info(f"Document {document_id} split into {len(chunks)} chunks")

            # Step 2. Create Document objects with metadata
            documents = []
            for idx, chunk_text in enumerate(chunks):
                
                metadata = {
                    "document_id": document_id,
                    "video_id": None,  # No video_id for documents
                    "project_id": project_id,
                    "chunk_index": idx,
                    "length": len(chunk_text),
                    "source_type": "document",
                    "created_at": datetime.utcnow().isoformat()
                }
                doc = Document(page_content=chunk_text.strip(), metadata=metadata)
                documents.append(doc)

            # Step 3. Save to vector store using LangChain
            vectorstore = self._get_document_vectorstore()
            
            # Add documents to vector store (this handles embedding and storage)
            vectorstore.add_documents(documents)
            
            self.logger.info(f"Successfully saved {len(documents)} chunks for document {document_id} in project {project_id}")
            return len(documents)
            
        except Exception as e:
            self.logger.error(f"Failed to process document {document_id}: {e}")
            raise

    def chunk_and_embed_video(self, video_id, transcript, project_id, chunk_size=1000, chunk_overlap=200):
        """
        Split video transcript into chunks, generate embeddings, and store them using LangChain PGVector.
        
        Args:
            video_id (str): Video ID
            transcript (str): Video transcript text
            project_id (str): Project ID that contains this video
            chunk_size (int): Size of each chunk
            chunk_overlap (int): Overlap between chunks
            
        Returns:
            int: Number of chunks created
            
        Raises:
            Exception: If chunking or embedding fails
        """
        if not transcript:
            self.logger.warning(f"No transcript provided for video {video_id}")
            raise Exception(f"No transcript provided for video {video_id}")

        try:
            # Step 1. Split into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ".", "!", "?", " "]
            )
            chunks = splitter.split_text(transcript)
            self.logger.info(f"Video {video_id} transcript split into {len(chunks)} chunks")

            # Step 2. Create Document objects with metadata
            documents = []
            for idx, chunk_text in enumerate(chunks):
                
                metadata = {
                    "document_id": None,  # No document_id for videos
                    "video_id": video_id,
                    "project_id": project_id,
                    "chunk_index": idx,
                    "length": len(chunk_text),
                    "source_type": "video",
                    "created_at": datetime.utcnow().isoformat()
                }
                doc = Document(page_content=chunk_text.strip(), metadata=metadata)
                documents.append(doc)

            # Step 3. Save to vector store using LangChain
            vectorstore = self._get_video_vectorstore()
            
            # Add documents to vector store (this handles embedding and storage)
            vectorstore.add_documents(documents)
            
            self.logger.info(f"Successfully saved {len(documents)} video chunks for video {video_id} in project {project_id}")
            return len(documents)
            
        except Exception as e:
            self.logger.error(f"Failed to process video {video_id}: {e}")
            raise