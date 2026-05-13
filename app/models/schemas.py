from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    STORING = "storing"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestRequest(BaseModel):
    youtube_url: HttpUrl
    
    class Config:
        json_schema_extra = {
            "example": {
                "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        }


class IngestResponse(BaseModel):
    job_id: str
    video_id: str
    status: JobStatus
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    video_id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    current_step: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class QueryRequest(BaseModel):
    video_id: str
    question: str
    top_k: int = Field(default=5, ge=1, le=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "question": "What is the main topic discussed?",
                "top_k": 5
            }
        }


class Source(BaseModel):
    chunk_text: str
    timestamp: str
    similarity_score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    video_id: str


class VideoInfo(BaseModel):
    id: str
    url: str
    title: str
    duration: int  # in seconds
    status: JobStatus
    chunk_count: int
    created_at: datetime
    completed_at: Optional[datetime] = None


class VideoListResponse(BaseModel):
    videos: List[VideoInfo]
    total: int


class TranscriptSegment(BaseModel):
    text: str
    start: float  # seconds
    end: float  # seconds


class Chunk(BaseModel):
    text: str
    start_time: float
    end_time: float
    timestamp: str  # formatted as "MM:SS"
    chunk_index: int


class DeleteResponse(BaseModel):
    success: bool
    message: str
    video_id: str