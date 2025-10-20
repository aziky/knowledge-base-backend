import os
import time
import logging
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

class SQSListener:
    def __init__(self, queue_url=None):
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

                    # Xử lý xong → xóa message
                    self.sqs.delete_message(
                        QueueUrl=self.queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    self.logger.info("Deleted message from queue.")

            except ClientError as e:
                self.logger.error(f"AWS ClientError: {e}")
                time.sleep(5)
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                time.sleep(5)
