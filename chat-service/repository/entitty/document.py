from config.config import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid


class Document(db.Model):
    __tablename__ = "documents"
    __table_args__ = {"schema": "kb_project"}  # <-- thêm dòng này

    document_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uploaded_by = db.Column(db.String(255), nullable=True)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey("kb_project.projects.project_id"), nullable=False)
    folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey("kb_project.folders.folder_id"), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.Text, nullable=True)
    file_type = db.Column(db.String(20), nullable=True)
    doc_metadata = db.Column("metadata", JSONB, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Document {self.name} ({self.document_id})>"
