"""
Models Package

Data models and database operations:
- schemas: Pydantic models for API validation
- database: SQLite database operations
"""

from app.models.database import db
from app.models.schemas import (
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    VideoInfo,
    VideoListResponse,
    JobStatus,
    JobStatusResponse,
    Source,
    Chunk,
    TranscriptSegment,
    DeleteResponse,
)

__all__ = [
    "db",
    "IngestRequest",
    "IngestResponse",
    "QueryRequest",
    "QueryResponse",
    "VideoInfo",
    "VideoListResponse",
    "JobStatus",
    "JobStatusResponse",
    "Source",
    "Chunk",
    "TranscriptSegment",
    "DeleteResponse",
]