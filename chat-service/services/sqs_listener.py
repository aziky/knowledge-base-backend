import os
import time
import logging
import json
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from services.document_service import DocumentService
from services.video_service import VideoService
from config.config import create_app

class SQSListener:
    def __init__(self, queue_url):
        # Load environment variables
        load_dotenv()

        self.queue_url = queue_url
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "ap-southeast-1")

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        self.logger = logging.getLogger(__name__)

        # Connect to SQS
        self.sqs = boto3.client(
            "sqs",
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        
        # Initialize appropriate service based on queue URL
        if "document" in self.queue_url.lower():
            # Create Flask app instance for database context
            app, _ = create_app()
            self.document_service = DocumentService(app)
            self.service_type = "document"
            self.logger.info("Initialized DocumentService for document queue")
            
        elif "video" in self.queue_url.lower():
            # Create Flask app instance for database context
            app, _ = create_app()
            self.video_service = VideoService(app)
            self.service_type = "video"
            self.logger.info("Initialized VideoService for video queue")
        else:
            self.service_type = None
            self.logger.warning("Unknown queue type, no service initialized")
        
        self.logger.info(f"SQSListener initialized for queue: {self.queue_url}")

    def listen(self):
        self.logger.info("Start listening to SQS queue...")
        while True:
            try:
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20
                )
                messages = response.get("Messages", [])
                if not messages:
                    continue

                for message in messages:
                    self.logger.info(f"Received message: {message['Body']}")
                    
                    try:
                        event_json = json.loads(message['Body'])
                        
                        # Route to appropriate service based on queue type
                        if self.service_type == "document":
                            self.document_service.process_s3_event(event_json)
                        elif self.service_type == "video":
                            self.video_service.process_s3_event(event_json)
                        else:
                            self.logger.error(f"Unknown service type: {self.service_type}")
                            continue
                        
                        # Delete message after successful processing
                        self.sqs.delete_message(
                            QueueUrl=self.queue_url,
                            ReceiptHandle=message['ReceiptHandle']
                        )
                        self.logger.info("Message processed and deleted from queue")
                        
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")


            except ClientError as e:
                self.logger.error(f"AWS ClientError: {e}")
                time.sleep(5)
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                time.sleep(5)
