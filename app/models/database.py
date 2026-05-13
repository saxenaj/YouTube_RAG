import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from app.config import settings
from app.models.schemas import JobStatus, VideoInfo


class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(settings.SQLITE_DB_PATH)
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Videos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    title TEXT,
                    duration INTEGER,
                    status TEXT NOT NULL,
                    chunk_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP
                )
            """)
            
            # Processing jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_jobs (
                    job_id TEXT PRIMARY KEY,
                    video_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress INTEGER DEFAULT 0,
                    current_step TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (video_id) REFERENCES videos(id)
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_videos_status 
                ON videos(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_video_id 
                ON processing_jobs(video_id)
            """)
    
    # Video operations
    def create_video(self, video_id: str, url: str, title: str = None, 
                     duration: int = None) -> None:
        """Create a new video record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO videos (id, url, title, duration, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (video_id, url, title, duration, JobStatus.PENDING.value, 
                  datetime.now()))
    
    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_video(self, video_id: str, **kwargs) -> None:
        """Update video fields"""
        if not kwargs:
            return
        
        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [video_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE videos SET {fields} WHERE id = ?
            """, values)
    
    def list_videos(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all videos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM videos 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_video(self, video_id: str) -> bool:
        """Delete video record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
            return cursor.rowcount > 0
    
    def get_video_count(self) -> int:
        """Get total video count"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM videos")
            return cursor.fetchone()[0]
    
    # Job operations
    def create_job(self, job_id: str, video_id: str) -> None:
        """Create a new processing job"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute("""
                INSERT INTO processing_jobs 
                (job_id, video_id, status, progress, current_step, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (job_id, video_id, JobStatus.PENDING.value, 0, 
                  "Initializing", now, now))
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM processing_jobs WHERE job_id = ?", 
                         (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_job(self, job_id: str, status: JobStatus = None, 
                   progress: int = None, current_step: str = None,
                   error_message: str = None) -> None:
        """Update job status"""
        updates = {}
        if status:
            updates['status'] = status.value
        if progress is not None:
            updates['progress'] = progress
        if current_step:
            updates['current_step'] = current_step
        if error_message:
            updates['error_message'] = error_message
        
        updates['updated_at'] = datetime.now()
        
        if not updates:
            return
        
        fields = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [job_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE processing_jobs SET {fields} WHERE job_id = ?
            """, values)
    
    def get_jobs_by_video(self, video_id: str) -> List[Dict[str, Any]]:
        """Get all jobs for a video"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM processing_jobs 
                WHERE video_id = ? 
                ORDER BY created_at DESC
            """, (video_id,))
            return [dict(row) for row in cursor.fetchall()]


# Global database instance
db = Database()