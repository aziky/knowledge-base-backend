import threading
import os
from dotenv import load_dotenv
from flask import app
from config.config import create_app
from services.sqs_listener import SQSListener
from api.chat_controller import chat_controller
from api.document_controller import document_controller

def start_listeners():
    load_dotenv()
    document_queue_url= os.getenv("SQS_DOCUMENT_QUEUE_URL")
    video_queue_url= os.getenv("SQS_VIDEO_QUEUE_URL")
    
    document_listener = SQSListener(queue_url=document_queue_url)
    video_listener = SQSListener(queue_url=video_queue_url)

    document_thread = threading.Thread(target=document_listener.listen)
    video_thread = threading.Thread(target=video_listener.listen)

    document_thread.start()
    video_thread.start()
    
    print("SQS listeners started in background...")


def main():
    load_dotenv()
    
    app, api = create_app()
    
    chat_namespace = chat_controller(api)
    api.add_namespace(chat_namespace)
    
    document_name = document_controller(api)
    api.add_namespace(document_name)
    
    # api.add_namespace(document_controller(api)) 
    
    start_listeners()

    port = int(os.getenv("API_PORT", 7075))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
    
if __name__ == "__main__":
    main()
