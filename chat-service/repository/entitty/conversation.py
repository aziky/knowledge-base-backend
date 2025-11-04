from config.config import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class Conversation(db.Model):
    __tablename__ = 'conversations'
    __table_args__ = {"schema": "kb_chat"}  
    
    id = db.Column(PG_UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(PG_UUID(as_uuid=False), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='ACTIVE')
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship to messages
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id) if self.id else None,
            'user_id': str(self.user_id) if self.user_id else None,
            'title': self.title,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None
        }


