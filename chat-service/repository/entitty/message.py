from config.config import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class Message(db.Model):
    __tablename__ = 'messages'
    __table_args__ = {"schema": "kb_chat"}  
    
    
    id = db.Column(PG_UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(PG_UUID(as_uuid=False), db.ForeignKey('kb_chat.conversations.id', ondelete='CASCADE'), nullable=False)
    sender_type = db.Column(db.String(10), nullable=False)  # 'USER' or 'BOT'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    message_metadata = db.Column('metadata', db.JSON, nullable=True)
    
    def to_dict(self):
        return {
            'id': str(self.id) if self.id else None,
            'conversation_id': str(self.conversation_id) if self.conversation_id else None,
            'sender_type': self.sender_type,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.message_metadata
        }
