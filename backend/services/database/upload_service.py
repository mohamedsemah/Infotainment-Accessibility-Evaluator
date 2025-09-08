"""
Upload service for managing upload data.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta

from database.models import Upload, UploadStatus
from database.session import get_db
from models.schemas import UploadResult

class UploadService:
    """Service for managing upload data."""
    
    def __init__(self, db: Session = None):
        self.db = db
    
    def create_upload(self, upload_data: Dict[str, Any]) -> Upload:
        """Create a new upload record."""
        upload = Upload(
            id=upload_data['id'],
            filename=upload_data['filename'],
            file_size=upload_data['file_size'],
            file_count=upload_data['file_count'],
            upload_path=upload_data['upload_path'],
            status=UploadStatus.PENDING
        )
        
        self.db.add(upload)
        self.db.commit()
        self.db.refresh(upload)
        
        return upload
    
    def get_upload(self, upload_id: str) -> Optional[Upload]:
        """Get upload by ID."""
        return self.db.query(Upload).filter(Upload.id == upload_id).first()
    
    def get_upload_by_path(self, upload_path: str) -> Optional[Upload]:
        """Get upload by path."""
        return self.db.query(Upload).filter(Upload.upload_path == upload_path).first()
    
    def update_upload_status(self, upload_id: str, status: UploadStatus) -> Optional[Upload]:
        """Update upload status."""
        upload = self.get_upload(upload_id)
        if upload:
            upload.status = status
            if status == UploadStatus.COMPLETED:
                upload.completed_at = datetime.utcnow()
            upload.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(upload)
        return upload
    
    def get_uploads(self, limit: int = 100, offset: int = 0) -> List[Upload]:
        """Get list of uploads."""
        return self.db.query(Upload).order_by(desc(Upload.created_at)).offset(offset).limit(limit).all()
    
    def get_uploads_by_status(self, status: UploadStatus, limit: int = 100) -> List[Upload]:
        """Get uploads by status."""
        return self.db.query(Upload).filter(Upload.status == status).order_by(desc(Upload.created_at)).limit(limit).all()
    
    def delete_upload(self, upload_id: str) -> bool:
        """Delete upload and all related data."""
        upload = self.get_upload(upload_id)
        if upload:
            self.db.delete(upload)
            self.db.commit()
            return True
        return False
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """Get upload statistics."""
        total_uploads = self.db.query(Upload).count()
        pending_uploads = self.db.query(Upload).filter(Upload.status == UploadStatus.PENDING).count()
        processing_uploads = self.db.query(Upload).filter(Upload.status == UploadStatus.PROCESSING).count()
        completed_uploads = self.db.query(Upload).filter(Upload.status == UploadStatus.COMPLETED).count()
        failed_uploads = self.db.query(Upload).filter(Upload.status == UploadStatus.FAILED).count()
        
        # Get average processing time
        avg_processing_time = self.db.query(func.avg(
            func.extract('epoch', Upload.completed_at - Upload.created_at)
        )).filter(Upload.status == UploadStatus.COMPLETED).scalar()
        
        return {
            "total_uploads": total_uploads,
            "pending_uploads": pending_uploads,
            "processing_uploads": processing_uploads,
            "completed_uploads": completed_uploads,
            "failed_uploads": failed_uploads,
            "average_processing_time": avg_processing_time or 0
        }
    
    def cleanup_old_uploads(self, days_old: int = 30) -> int:
        """Clean up old uploads."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        old_uploads = self.db.query(Upload).filter(
            Upload.created_at < cutoff_date,
            Upload.status.in_([UploadStatus.COMPLETED, UploadStatus.FAILED])
        ).all()
        
        count = len(old_uploads)
        for upload in old_uploads:
            self.db.delete(upload)
        
        self.db.commit()
        return count
    
    def get_upload_summary(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """Get upload summary with related data counts."""
        upload = self.get_upload(upload_id)
        if not upload:
            return None
        
        # Get counts of related data
        findings_count = len(upload.findings)
        clusters_count = len(upload.clusters)
        patches_count = len(upload.patches)
        reports_count = len(upload.reports)
        
        return {
            "upload": upload,
            "findings_count": findings_count,
            "clusters_count": clusters_count,
            "patches_count": patches_count,
            "reports_count": reports_count
        }
