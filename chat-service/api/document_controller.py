from flask_restx import Resource, fields, Namespace
from flask import current_app

from services.document_service import DocumentService


def document_controller(api):
    
    document_ns = api.namespace('Document', 
                                description='Quản lý các tài liệu kiến thức', 
                                path='/api/documents')
    
    document_model = document_ns.model('Document', {
        'document_id': fields.String(description='Document ID'),
        'name': fields.String(description='Document name'),
        'uploaded_by': fields.String(description='Người upload'),
        'uploaded_at': fields.DateTime(description='Upload time')
    })


    @document_ns.route('/') 
    # @document_ns.marshal_list_with(document_model)
    class DocumentResource(Resource):
        def get(self):
            # Create document service instance with current app context
            document_service = DocumentService(current_app)
            documents = document_service.get_all_documents()
            result = []
            for doc in documents:
                result.append({
                    'document_id': str(doc.document_id),
                    'name': doc.name,
                    'uploaded_by': doc.uploaded_by,
                    'uploaded_at': doc.uploaded_at.isoformat() if doc.uploaded_at else None
                })
            return result, 200
    
    return document_ns

