from dotenv import load_dotenv
from repository.entitty.document import Document
import json
import tempfile
import logging
import boto3
from botocore.exceptions import ClientError
from repository.entitty.document import Document
from config.config import db
import os
from PyPDF2 import PdfReader as PdfReader
from docx import Document as DocxDocument
import urllib.parse


class DocumentService:
    def __init__(self):
        
        load_dotenv()
        
        self.s3 = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION", "ap-southeast-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")    
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    def get_all_documents(self):
        try:
            return Document.query.all()
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []
        
    
    def process_s3_event(self, json):
            """
            event: dict JSON từ message SQS (S3 event)
            """
            try:
                for record in json.get("Records", []):
                    s3_info = record.get("s3", {})
                    bucket = s3_info.get("bucket", {}).get("name")
                    key = s3_info.get("object", {}).get("key")
                    self.logger.info(f"Received S3 object: s3://{bucket}/{key}")

                    # # Tải file từ S3 nếu cần
                    content = self.download_file(bucket, key)
                    if not content:
                        continue
                    
                    extracted_text = self.extract_text_from_document(key, content)
                    if extracted_text:
                        self.logger.info(f"Extracted text from {key}:\n{extracted_text}")
                    else:
                        self.logger.warning(f"No text extracted from document: s3://{bucket}/{key}")
                    

                    # Lưu thông tin file vào DB (ví dụ)
                    # self.save_document(bucket, key, content)

            except Exception as e:
                self.logger.error(f"Error processing S3 event: {e}")

    def download_file(self, bucket, key):
        try:
            decoded_key = urllib.parse.unquote_plus(key)
            response = self.s3.get_object(Bucket=bucket, Key=decoded_key)
            content = response["Body"].read()
            self.logger.info(f"Downloaded file size: {len(content)} bytes")
            return content
        except ClientError as e:
            self.logger.error(f"Failed to download s3://{bucket}/{key}: {e}")
            return None
    
    
    def extract_text_from_document(self, key, content):
        self.logger.info(f"Extracting text from document: {key}")
        try:
            _, ext = os.path.splitext(key)
            ext = ext.lower()

            # Write content to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name

            text = ""

            if ext == ".pdf":
                reader = PdfReader(tmp_path)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            elif ext == ".docx":
                doc = DocxDocument(tmp_path)
                for para in doc.paragraphs:
                    if para.text:
                        text += para.text + "\n"

            else:
                self.logger.warning(f"File {key} is not a supported document type. Skipping extraction.")
                os.remove(tmp_path)
                return None

            # Clean up temp file
            os.remove(tmp_path)

            self.logger.info(f"Extracted {len(text)} characters from {key}")
            return text.strip() if text else None

        except Exception as e:
            self.logger.error(f"Error extracting text from document {key}: {e}")
            return None