import asyncio
from typing import Optional
import uuid
from app.config import settings
from app.models.database import db
from app.models.schemas import JobStatus
from app.services.download_service import download_service
from app.services.transcription_service import transcription_service
from app.services.chunking_service import chunking_service
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
import logging

logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Main orchestrator for video processing pipeline
    Handles the entire flow from download to storage
    """
    
    def __init__(self):
        self.active_jobs = {}  # Track active processing jobs
    
    async def process_video(self, youtube_url: str, job_id: str = None) -> str:
        """
        Process a YouTube video through the entire pipeline
        
        Pipeline:
        1. Download audio
        2. Transcribe
        3. Chunk text
        4. Generate embeddings
        5. Store in vector DB
        
        Returns: video_id
        """
        # Generate job ID if not provided
        if not job_id:
            job_id = str(uuid.uuid4())
        
        video_id = None
        
        try:
            # Step 1: Extract video ID and get info
            logger.info(f"[Job {job_id}] Starting video processing")
            video_id = download_service.extract_video_id(str(youtube_url))
            
            # Create video and job records
            db.create_video(
                video_id=video_id,
                url=str(youtube_url),
                title="Processing..."
            )
            db.create_job(job_id=job_id, video_id=video_id)
            
            # Update job status
            db.update_job(
                job_id=job_id,
                status=JobStatus.DOWNLOADING,
                progress=10,
                current_step="Downloading audio"
            )
            
            # Step 2: Download audio
            audio_path, video_info = await download_service.download_audio(
                str(youtube_url), 
                video_id
            )
            
            # Update video info
            db.update_video(
                video_id=video_id,
                title=video_info.get('title'),
                duration=video_info.get('duration')
            )
            
            logger.info(f"[Job {job_id}] Audio downloaded: {audio_path}")
            
            # Step 3: Transcribe
            db.update_job(
                job_id=job_id,
                status=JobStatus.TRANSCRIBING,
                progress=30,
                current_step="Transcribing audio"
            )
            
            transcript_segments = await transcription_service.transcribe(audio_path)
            logger.info(f"[Job {job_id}] Transcription complete: {len(transcript_segments)} segments")
            
            # Step 4: Chunk transcript
            db.update_job(
                job_id=job_id,
                status=JobStatus.CHUNKING,
                progress=50,
                current_step="Chunking text"
            )
            
            chunks = chunking_service.chunk_transcript(transcript_segments)
            logger.info(f"[Job {job_id}] Chunking complete: {len(chunks)} chunks")
            
            # Step 5: Generate embeddings
            db.update_job(
                job_id=job_id,
                status=JobStatus.EMBEDDING,
                progress=70,
                current_step="Generating embeddings"
            )
            
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = embedding_service.embed_batch(chunk_texts)
            logger.info(f"[Job {job_id}] Embeddings generated")
            
            # Step 6: Store in vector DB
            db.update_job(
                job_id=job_id,
                status=JobStatus.STORING,
                progress=90,
                current_step="Storing in database"
            )
            
            vector_store.add_chunks(video_id, chunks, embeddings)
            logger.info(f"[Job {job_id}] Chunks stored in vector database")
            
            # Update final status
            db.update_video(
                video_id=video_id,
                status=JobStatus.COMPLETED.value,
                chunk_count=len(chunks)
            )
            
            db.update_job(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                progress=100,
                current_step="Completed"
            )
            
            # Cleanup audio file if configured
            if settings.CLEANUP_AUDIO_AFTER_PROCESSING:
                download_service.cleanup_audio(video_id)
                logger.info(f"[Job {job_id}] Audio file cleaned up")
            
            logger.info(f"[Job {job_id}] Video processing completed successfully")
            return video_id
            
        except Exception as e:
            logger.error(f"[Job {job_id}] Error processing video: {e}", exc_info=True)
            
            # Update job and video status as failed
            if video_id:
                db.update_video(video_id=video_id, status=JobStatus.FAILED.value)
            
            db.update_job(
                job_id=job_id,
                status=JobStatus.FAILED,
                error_message=str(e),
                current_step="Failed"
            )
            
            # Cleanup on failure
            if video_id:
                download_service.cleanup_audio(video_id)
            
            raise
    
    def start_processing_background(self, youtube_url: str) -> tuple[str, str]:
        """
        Start video processing in background
        Returns: (job_id, video_id)
        """
        job_id = str(uuid.uuid4())
        video_id = download_service.extract_video_id(str(youtube_url))
        
        # Start processing in background
        asyncio.create_task(self.process_video(youtube_url, job_id))
        
        return job_id, video_id
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get current status of a processing job"""
        return db.get_job(job_id)
    
    def get_video_info(self, video_id: str) -> Optional[dict]:
        """Get video information"""
        return db.get_video(video_id)
    
    async def delete_video(self, video_id: str) -> bool:
        """
        Delete video and all associated data
        - Remove from vector store
        - Delete audio file
        - Remove from database
        """
        try:
            # Delete from vector store
            vector_store.delete_video(video_id)
            
            # Delete audio file
            download_service.cleanup_audio(video_id)
            
            # Delete from database
            db.delete_video(video_id)
            
            logger.info(f"Successfully deleted video {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting video {video_id}: {e}")
            return False


# Global service instance
video_processor = VideoProcessor()