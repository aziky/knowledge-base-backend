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
                
                # Get user_id from JWT token
                user_id = getattr(request, 'user', {}).get('sub', None)
                if not user_id:
                    return {'error': 'User authentication required'}, 401
                
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
                    user_id=user_id,
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
        
        @chat_ns.marshal_with(chat_ns.model('UserConversations', {
            'conversations': fields.List(fields.Raw, description='List of user conversations'),
            'total_count': fields.Integer(description='Total number of conversations'),
            'limit': fields.Integer(description='Number of items per page'),
            'offset': fields.Integer(description='Number of items skipped'),
            'has_more': fields.Boolean(description='Whether there are more conversations available')
        }))
        @token_required
        def get(self):
            """
            Get all conversations for the authenticated user
            
            Query parameters:
            - status: Filter by status (ACTIVE, CLOSED, ARCHIVED) - default: ACTIVE
            - limit: Maximum number of conversations to return - default: 20
            - offset: Number of conversations to skip (for pagination) - default: 0
            
            Returns paginated list of user's conversations with message counts.
            """
            try:
                # Get user_id from JWT token
                user_id = getattr(request, 'user', {}).get('sub', None)
                if not user_id:
                    return {'error': 'User authentication required'}, 401
                
                # Get query parameters
                status = request.args.get('status', 'ACTIVE')
                limit = int(request.args.get('limit', 20))
                offset = int(request.args.get('offset', 0))
                
                # Validate parameters
                if limit < 1 or limit > 100:
                    limit = 20
                if offset < 0:
                    offset = 0
                
                # Get user conversations
                result = chat_service.get_user_conversations(
                    user_id=user_id,
                    status=status,
                    limit=limit,
                    offset=offset
                )
                
                return result, 200
                    
            except Exception as e:
                return {
                    'error': 'Internal server error',
                    'message': str(e)
                }, 500

    @chat_ns.route('/summarize/<string:conversation_id>')
    class ConversationSummaryResource(Resource):
        
        @chat_ns.marshal_with(chat_ns.model('SummaryResponse', {
            'success': fields.Boolean(description='Whether summary was successful'),
            'summary_id': fields.String(description='Database ID of the stored summary'),
            'conversation_id': fields.String(description='Conversation ID that was summarized'),
            'summary': fields.String(description='Generated conversation summary'),
            'message_count': fields.Integer(description='Number of messages in conversation'),
            'project_id': fields.String(description='Associated project ID'),
            'error': fields.String(description='Error message if failed')
        }))
        @token_required
        def post(self, conversation_id):
            """
            Generate and store a summary of the conversation using Gemini AI
            
            This endpoint:
            1. Retrieves the full conversation history for the given conversation_id
            2. Sends the conversation to Gemini AI for summarization
            3. Stores the generated summary in the database
            4. Returns the summary along with metadata
            
            The conversation must have at least one exchange (2 messages) to be summarized.
            """
            try:
                if not conversation_id or not conversation_id.strip():
                    return {
                        'success': False,
                        'error': 'Conversation ID is required'
                    }, 400
                
                # Generate and store summary
                result = chat_service.summarize_conversation(conversation_id.strip())
                
                if result["success"]:
                    return result, 200
                else:
                    return result, 400
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': 'Internal server error',
                    'message': str(e),
                    'conversation_id': conversation_id
                }, 500

        @chat_ns.marshal_with(chat_ns.model('StoredSummary', {
            'id': fields.String(description='Summary database ID'),
            'conversation_id': fields.String(description='Conversation ID'),
            'project_id': fields.String(description='Associated project ID'),
            'summary_text': fields.String(description='Stored summary text'),
            'message_count': fields.Integer(description='Number of messages in conversation'),
            'conversation_created_at': fields.DateTime(description='When conversation was created'),
            'summarized_at': fields.DateTime(description='When summary was generated'),
            'created_at': fields.DateTime(description='When summary was stored'),
            'updated_at': fields.DateTime(description='Last update time')
        }))
        @token_required
        def get(self, conversation_id):
            """
            Retrieve stored conversation summary from database
            
            Returns the previously generated summary for the given conversation_id.
            If no summary exists, returns 404.
            """
            try:
                if not conversation_id or not conversation_id.strip():
                    return {'error': 'Conversation ID is required'}, 400
                
                # Get stored summary
                summary = chat_service.get_conversation_summary(conversation_id.strip())
                
                if summary:
                    return summary, 200
                else:
                    return {'error': 'Summary not found for this conversation'}, 404
                    
            except Exception as e:
                return {
                    'error': 'Internal server error',
                    'message': str(e)
                }, 500

    @chat_ns.route('/<string:conversation_id>')
    class ConversationHistoryResource(Resource):
        
        @chat_ns.marshal_with(chat_ns.model('ConversationHistory', {
            'conversation': fields.Raw(description='Conversation metadata'),
            'messages': fields.List(fields.Raw, description='List of messages in chronological order'),
            'message_count': fields.Integer(description='Total number of messages')
        }))
        @token_required
        def get(self, conversation_id):
            """
            Retrieve full conversation history from database
            
            Returns the complete conversation with all messages in chronological order.
            Only the conversation owner can access their conversation history.
            """
            try:
                if not conversation_id or not conversation_id.strip():
                    return {'error': 'Conversation ID is required'}, 400
                
                # Get user_id from JWT token for authorization
                user_id = getattr(request, 'user', {}).get('sub', None)
                if not user_id:
                    return {'error': 'User authentication required'}, 401
                
                # Get conversation from database
                conversation_data = chat_service.get_conversation_from_database(
                    conversation_id=conversation_id.strip()                
                )
                
                if conversation_data:
                    return conversation_data, 200
                else:
                    return {'error': 'Conversation not found or access denied'}, 404
                    
            except Exception as e:
                return {
                    'error': 'Internal server error',
                    'message': str(e)
                }, 500


    return chat_ns