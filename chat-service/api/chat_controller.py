from flask_restx import Resource, fields
from flask import request
from config.token_config import token_required
from services.chat_service import ChatService


def chat_controller(api):
    # Initialize ChatService once for the entire controller (lazy initialization)
    chat_service = ChatService()
    chat_ns = api.namespace('Chat', 
                            description='RAG-powered Chat API with Vector Search and Gemini Integration', 
                            path='/api/chat')
    
    # Request models
    chat_request_model = chat_ns.model('ChatRequest', {
        'document_ids': fields.List(fields.String, required=False, description='List of document IDs for filtering (optional)'),
        'video_ids': fields.List(fields.String, required=False, description='List of video IDs for filtering (optional)'),
        'question': fields.String(required=True, description='User question to be answered'),
        'conversation_id': fields.String(required=False, description='Conversation ID for maintaining chat context (optional)')
    })
    
    # Response models
    source_model = chat_ns.model('Source', {
        'chunk_id': fields.String(description='ID of the source document chunk'),
        'similarity': fields.Float(description='Similarity score (0-1)'),
        'content_preview': fields.String(description='Preview of the source content')
    })
    
    metadata_model = chat_ns.model('Metadata', {
        'query': fields.String(description='Original user query'),
        'chunks_found': fields.Integer(description='Number of relevant chunks found'),
        'gemini_status': fields.String(description='Status of Gemini API call'),
        'project_id': fields.String(description='Project ID'),
        'document_ids': fields.List(fields.String, description='Document IDs used for filtering'),
        'video_ids': fields.List(fields.String, description='Video IDs used for filtering'),
        'conversation_message_count': fields.Integer(description='Total messages in conversation'),
        'has_conversation_history': fields.Boolean(description='Whether conversation has previous context')
    })
    
    chat_response_model = chat_ns.model('ChatResponse', {
        'answer': fields.String(description='AI-generated answer to the user question'),
        'conversation_id': fields.String(description='Conversation ID for maintaining chat context'),
        'sources': fields.List(fields.Nested(source_model), description='Source documents used for the answer'),
        'metadata': fields.Nested(metadata_model, description='Additional metadata about the query')
    })

    @chat_ns.route('')
    class ChatResource(Resource):

        @chat_ns.expect(chat_request_model)
        @chat_ns.marshal_with(chat_response_model)
        @token_required
        def post(self):
            """
            Process a chat query using RAG (Retrieval-Augmented Generation) with conversation memory
            
            This endpoint:
            1. Maintains conversation context using LangChain memory
            2. Converts user question to embedding vector
            3. Searches for similar document chunks in vector database
            4. Combines retrieved content with user question and conversation history
            5. Sends enhanced prompt to Gemini for answer generation
            6. Returns AI answer with source references and conversation ID
            """
            try:
                # Get request data
                data = request.get_json()
                
                if not data:
                    return {'error': 'Request body is required'}, 400
                
                user_question = data.get('question', '').strip()
                document_ids = data.get('document_ids', [])
                video_ids = data.get('video_ids', [])
                project_id = data.get('project_id', None)
                conversation_id = data.get('conversation_id', None)
                
                # Validate required fields
                if not user_question:
                    return {'error': 'Question is required'}, 400
                
                # Ensure document_ids is a list
                if document_ids and not isinstance(document_ids, list):
                    document_ids = [document_ids]
                
                if video_ids and not isinstance(video_ids, list):
                    video_ids = [video_ids]
                
                # Process the chat query with conversation context
                response = chat_service.process_chat_query(
                    user_question=user_question,
                    project_id=project_id,
                    document_ids=document_ids,
                    video_ids=video_ids,
                    conversation_id=conversation_id
                )
                
                return response, 200
                
            except Exception as e:
                return {
                    'error': 'Internal server error',
                    'message': str(e)
                }, 500


    return chat_ns