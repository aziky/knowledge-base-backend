import threading
import os
from dotenv import load_dotenv
from services.sqs_listener import SQSListener

def main():
    load_dotenv()
    document_queue_url= os.getenv("SQS_DOCUMENT_QUEUE_URL")
    video_queue_url= os.getenv("SQS_VIDEO_QUEUE_URL")
    
    document_listener = SQSListener(queue_url=document_queue_url)
    video_listener = SQSListener(queue_url=video_queue_url)

    document_thread = threading.Thread(target=document_listener.listen)
    video_thread = threading.Thread(target=video_listener.listen)

    document_thread.start()
    video_thread.start()
    
    document_thread.join()
    video_thread.join() 
    
if __name__ == "__main__":
    main()
