from flask_restx import Resource, fields, Namespace


def chat_controller(api):


    chat_ns = api.namespace('Chat', 
                            description='Các API liên quan đến chức năng Chat', 
                            path='/api/chat')
    
    chat_model = chat_ns.model('ChatMessage', {
        'user_id': fields.String(required=True),
        'project_id': fields.String(required=True),
        'message': fields.String(required=True)
    })

    @chat_ns.route('/')
    class ChatResource(Resource):
        def get(self):
            return {'status': 'Chat service is running'}, 200

    @chat_ns.route('/<string:chat_id>')
    class ChatDetailResource(Resource):
        def get(self, chat_id):
            return {'chat_id': chat_id, 'status': 'Chat service is running'}, 200
    
    return chat_ns