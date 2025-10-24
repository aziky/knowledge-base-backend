import json
import uuid
from datetime import datetime
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.config import db  # Assuming you already import db from your config
from flask import current_app
from sqlalchemy import text as sql_text
import logging


class EmbeddingService:
    def __init__(self, app=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        
        self.app = app  # Store Flask app instance

        # Load embedding model once at startup
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.logger.info("Embedding model loaded successfully") 

    def chunk_and_embed(self, document_id, text, chunk_size=1000, chunk_overlap=200):
        """
        Split text into chunks, generate embeddings, and store them in DB.
        """
        if not text:
            self.logger.warning(f"No text provided for document {document_id}")
            raise Exception(f"No text provided for document {document_id}")

        # Step 1. Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", " "]
        )
        chunks = splitter.split_text(text)
        self.logger.info(f"Document {document_id} split into {len(chunks)} chunks")

        # Step 2. Embed all chunks
        embeddings = self.model.encode(chunks, show_progress_bar=True)
        self.logger.info(f"Generated embeddings for {len(embeddings)} chunks")

        # Step 3. Save to PostgreSQL
        inserted_count = 0
        
        def _save_to_db():
            """Internal function to save chunks to database"""
            nonlocal inserted_count
            for idx, (chunk_text, embedding_vector) in enumerate(zip(chunks, embeddings)):
                try:
                    chunk_id = str(uuid.uuid4())
                    metadata = {
                        "length": len(chunk_text),
                        "created_at": datetime.utcnow().isoformat()
                    }

                    embedding_list = embedding_vector.tolist()  # convert numpy array to Python list

                    db.session.execute(sql_text(
                        "INSERT INTO kb_chat.document_chunks (chunk_id, document_id, content, embedding, chunk_index, metadata) "
                        "VALUES (:chunk_id, :document_id, :content, :embedding, :chunk_index, :metadata)"
                    ), {
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "content": chunk_text.strip(),
                        "embedding": embedding_list,
                        "chunk_index": idx,
                        "metadata": json.dumps(metadata)
                    })
                    inserted_count += 1
                    
                except Exception as chunk_error:
                    self.logger.error(f"Error processing chunk {idx}: {chunk_error}")
                    raise  # Re-raise to be caught by outer exception handler

            db.session.commit()
            self.logger.info(f"Saved {inserted_count} chunks for document {document_id}")
        
        try:
            if self.app:
                # If we have a Flask app instance, create application context
                with self.app.app_context():
                    _save_to_db()
            else:
                # Try to use current_app if available (when called from Flask request context)
                try:
                    with current_app.app_context():
                        _save_to_db()
                except RuntimeError:
                    # If no application context is available, just try without it
                    # This might fail, but it's better than not trying at all
                    _save_to_db()

        except Exception as e:
            try:
                if self.app:
                    with self.app.app_context():
                        db.session.rollback()
                else:
                    try:
                        with current_app.app_context():
                            db.session.rollback()
                    except RuntimeError:
                        db.session.rollback()
            except:
                pass  # If rollback fails, we can't do much about it
            self.logger.error(f"Failed to insert chunks for document {document_id}: {e}")
            raise

        return inserted_count

    def chunk_and_embed_video(self, video_id, transcript, chunk_size=1000, chunk_overlap=200):
        """
        Split video transcript into chunks, generate embeddings, and store them in video_chunks table.
        
        Args:
            video_id (str): Video ID
            transcript (str): Video transcript text
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

        # Step 1. Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", " "]
        )
        chunks = splitter.split_text(transcript)
        self.logger.info(f"Video {video_id} transcript split into {len(chunks)} chunks")

        # Step 2. Embed all chunks
        embeddings = self.model.encode(chunks, show_progress_bar=True)
        self.logger.info(f"Generated embeddings for {len(embeddings)} video chunks")

        # Step 3. Save to PostgreSQL video_chunks table
        inserted_count = 0
        
        def _save_to_db():
            """Internal function to save video chunks to database"""
            nonlocal inserted_count
            for idx, (chunk_text, embedding_vector) in enumerate(zip(chunks, embeddings)):
                try:
                    chunk_id = str(uuid.uuid4())
                    metadata = {
                        "length": len(chunk_text),
                        "created_at": datetime.utcnow().isoformat()
                    }

                    embedding_list = embedding_vector.tolist()  # convert numpy array to Python list

                    db.session.execute(sql_text(
                        "INSERT INTO kb_chat.video_chunks (chunk_id, video_id, transcript_chunk, embedding, chunk_index, metadata) "
                        "VALUES (:chunk_id, :video_id, :transcript_chunk, :embedding, :chunk_index, :metadata)"
                    ), {
                        "chunk_id": chunk_id,
                        "video_id": video_id,
                        "transcript_chunk": chunk_text.strip(),
                        "embedding": embedding_list,
                        "chunk_index": idx,
                        "metadata": json.dumps(metadata)
                    })
                    inserted_count += 1
                    
                except Exception as chunk_error:
                    self.logger.error(f"Error processing video chunk {idx}: {chunk_error}")
                    raise  # Re-raise to be caught by outer exception handler

            db.session.commit()
            self.logger.info(f"Saved {inserted_count} video chunks for video {video_id}")
        
        try:
            if self.app:
                with self.app.app_context():
                    _save_to_db()
            else:
                try:
                    with current_app.app_context():
                        _save_to_db()
                except RuntimeError:
                    _save_to_db()

        except Exception as e:
            try:
                if self.app:
                    with self.app.app_context():
                        db.session.rollback()
                else:
                    try:
                        with current_app.app_context():
                            db.session.rollback()
                    except RuntimeError:
                        db.session.rollback()
            except:
                pass
            self.logger.error(f"Failed to insert video chunks for video {video_id}: {e}")
            raise

        return inserted_count
