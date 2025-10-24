from dotenv import load_dotenv
import requests
import tempfile
import logging
import boto3
from botocore.exceptions import ClientError
import os
import urllib.parse
from services.embedding_service import EmbeddingService
import whisper


class VideoService:
    def __init__(self, app=None):
        load_dotenv()

        self.embedding_service = EmbeddingService(app)
        self.s3 = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION", "ap-southeast-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")    
        )
        
        self.project_service_url = os.getenv("PROJECT_SERVICE_URL", "http://localhost:7072/api")
        self.api_secret = os.getenv("INTERNAL_API_SECRET")
        
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        
        self.whisper_model = whisper.load_model("base")
        self.logger.info(f"Whisper model loaded successfully")

    def _call_project_service_get_video_id(self, path, type):
        """
        Calls the /project/path endpoint on the Project Service to get video metadata.
        
        Returns:
            dict: The 'data' payload if successful
            
        Raises:
            Exception: If API call fails
        """
        api_url = self.project_service_url + "/project/path"
        headers = {
            "X-Internal-Secret": self.api_secret,
            "Accept": "application/json"
        }

        decoded_path = urllib.parse.unquote_plus(path)

        params = {
            "path": decoded_path,
            "type": type
        }

        self.logger.info(f"Calling Project Service API: {api_url}")
        
        try:
            api_response = requests.get(api_url, headers=headers, timeout=10, params=params)
            api_response.raise_for_status()
            
            api_data = api_response.json()
            
            response_code = api_data.get('code')
            response_message = api_data.get('message')
            response_payload = api_data.get('data')
            
            self.logger.info(f"Project Service Response - Code: {response_code}, Message: {response_message}")
            self.logger.info(f"VideoId: {response_payload.get('videoId') if response_payload else 'N/A'}")
            
            return response_payload
            
        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"HTTP error: {http_err}")
            raise

        except requests.exceptions.JSONDecodeError as json_err:
            self.logger.error(f"JSON decode error: {json_err}")
            raise

        except requests.exceptions.RequestException as req_err:
            self.logger.error(f"Connection error: {req_err}")
            raise

    def process_s3_event(self, json_data):
        """
        Process S3 event for video files from SQS message.
        
        Args:
            json_data: dict JSON from SQS message (S3 event)
        """
        try:
            for record in json_data.get("Records", []):
                s3_info = record.get("s3", {})
                bucket = s3_info.get("bucket", {}).get("name")
                key = s3_info.get("object", {}).get("key")
                
                self.logger.info(f"Processing video from S3: s3://{bucket}/{key}")

                # Download video file from S3
                video_content = self.download_file(bucket, key)
                
                # Transcribe video using Whisper
                transcript = self.extract_and_transcribe_video(key, video_content)
                
                self.logger.info(f"Transcription successful for {key} ({len(transcript)} chars)")
                
                # Get video metadata from Project Service
                video_data = self._call_project_service_get_video_id(key, "video")
                
                video_id = video_data.get("videoId")
                
                # Chunk and embed the transcript
                self.chunk_video_transcript(video_id, transcript)
                
                # Update video status to COMPLETED
                self._update_video_status(video_id, status="COMPLETED")

        except Exception as e:
            self.logger.error(f"Error processing S3 video event: {e}")
            raise

    def download_file(self, bucket, key):
        """
        Download video file from S3.
        
        Args:
            bucket (str): S3 bucket name
            key (str): S3 object key
            
        Returns:
            bytes: File content
            
        Raises:
            ClientError: If S3 download fails
        """
        try:
            decoded_key = urllib.parse.unquote_plus(key)
            response = self.s3.get_object(Bucket=bucket, Key=decoded_key)
            content = response["Body"].read()
            self.logger.info(f"Downloaded video file: {len(content)} bytes")
            return content
        except ClientError as e:
            self.logger.error(f"Failed to download s3://{bucket}/{key}: {e}")
            raise

    def extract_and_transcribe_video(self, key, content):
        """
        Transcribe video using local Whisper model (FREE).
        
        Args:
            key (str): Original S3 key (filename)
            content (bytes): Video file content
            
        Returns:
            str: Transcribed text or None if failed
        """
        self.logger.info(f"Processing video: {key}")
        
        try:
            _, ext = os.path.splitext(key)
            ext = ext.lower()
            
            # Supported video formats
            supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
            if ext not in supported_formats:
                self.logger.warning(f"Unsupported video format: {ext}")
                raise ValueError(f"Unsupported video format: {ext}")

            # Save video to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_video:
                tmp_video.write(content)
                video_path = tmp_video.name

            # Transcribe using local Whisper
            self.logger.info(f"Transcribing video with Whisper (this may take a while)...")
            transcript = self._transcribe_with_whisper(video_path)

            # Clean up temporary file
            os.remove(video_path)

            return transcript

        except Exception as e:
            self.logger.error(f"Error processing video {key}: {e}")
            raise

    def _transcribe_with_whisper(self, video_path):
        """
        Transcribe video using local Whisper model.
        
        Whisper automatically extracts audio from video files.
        
        Args:
            video_path (str): Path to video file
            
        Returns:
            str: Transcribed text
            
        Raises:
            Exception: If transcription fails or returns empty transcript
        """
        try:
            # Whisper automatically handles video files and extracts audio
            result = self.whisper_model.transcribe(
                video_path,
                language=None,  # Auto-detect language (or set to "en", "vi", etc.)
                verbose=True,  # Prints detailed progress
                fp16=False  # Set to True if you have a GPU
            )
            
            transcript = result["text"].strip()
            
            if transcript:
                self.logger.info(f"Whisper transcription complete: {len(transcript)} chars")
                return transcript
            else:
                self.logger.error("Empty transcript from Whisper")
                raise Exception("Empty transcript from Whisper")
            
        except Exception as e:
            self.logger.error(f"Whisper transcription error: {e}")
            raise

    def chunk_video_transcript(self, video_id, transcript):
        """
        Chunk and embed video transcript using EmbeddingService.
        
        Args:
            video_id (str): Video ID from Project Service
            transcript (str): Transcribed text from video
            
        Returns:
            int: Number of chunks created
            
        Raises:
            Exception: If embedding fails
        """
        try:
            num_chunks = self.embedding_service.chunk_and_embed_video(video_id, transcript)
            self.logger.info(f"Video {video_id}: {num_chunks} transcript chunks embedded")
            return num_chunks
        except Exception as e:
            self.logger.error(f"Error embedding video transcript {video_id}: {e}")
            raise

    def _update_video_status(self, video_id, status="COMPLETED"):
        """
        Update video status in Project Service after processing.
        
        Args:
            video_id (str): Video ID
            status (str): New status (COMPLETED, FAILED, etc.)
            
        Returns:
            bool: True if update succeeded
            
        Raises:
            Exception: If status update fails
        """
        api_url = f"{self.project_service_url}/video/{video_id}/status"
        headers = {
            "X-Internal-Secret": self.api_secret,
        }

        params = {
            "status": status
        }

        try:
            self.logger.info(f"Updating video status: {video_id} -> {status}")
            response = requests.patch(api_url, headers=headers, params=params, timeout=5)
            response.raise_for_status()

            response_data = response.json()
            self.logger.info(
                f"Video status update - Code: {response_data.get('code')}, "
                f"Message: {response_data.get('message')}"
            )
            return True

        except requests.exceptions.RequestException as err:
            self.logger.error(f"Error updating video status: {err}")
            raise