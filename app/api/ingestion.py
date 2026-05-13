from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import IngestRequest, IngestResponse, JobStatus
from app.services.video_processor import video_processor
from app.services.download_service import download_service
from app.models.database import db
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=IngestResponse)
async def ingest_video(
    request: IngestRequest,
    background_tasks: BackgroundTasks
):
    """
    Start processing a YouTube video
    
    This endpoint:
    1. Validates the YouTube URL
    2. Creates a processing job
    3. Starts background processing
    4. Returns job ID for status tracking
    """
    try:
        # Extract and validate video ID
        video_id = download_service.extract_video_id(str(request.youtube_url))
        
        # Check if video already exists and is completed
        existing_video = db.get_video(video_id)
        if existing_video and existing_video['status'] == JobStatus.COMPLETED.value:
            logger.info(f"Video {video_id} already processed")
            return IngestResponse(
                job_id="",
                video_id=video_id,
                status=JobStatus.COMPLETED,
                message="Video already processed. You can query it directly."
            )
        
        # Check if video is currently being processed
        if existing_video and existing_video['status'] in [
            JobStatus.PENDING.value,
            JobStatus.DOWNLOADING.value,
            JobStatus.TRANSCRIBING.value,
            JobStatus.CHUNKING.value,
            JobStatus.EMBEDDING.value,
            JobStatus.STORING.value
        ]:
            # Get the active job for this video
            jobs = db.get_jobs_by_video(video_id)
            if jobs:
                active_job = jobs[0]
                return IngestResponse(
                    job_id=active_job['job_id'],
                    video_id=video_id,
                    status=JobStatus(active_job['status']),
                    message="Video is currently being processed"
                )
        
        # Create new job
        job_id = str(uuid.uuid4())
        
        # Start processing in background
        background_tasks.add_task(
            video_processor.process_video,
            str(request.youtube_url),
            job_id
        )
        
        logger.info(f"Started processing job {job_id} for video {video_id}")
        
        return IngestResponse(
            job_id=job_id,
            video_id=video_id,
            status=JobStatus.PENDING,
            message="Video processing started. Check /status/{job_id} for progress."
        )
        
    except ValueError as e:
        logger.error(f"Invalid YouTube URL: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting ingestion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of a processing job
    """
    try:
        job = db.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job['job_id'],
            "video_id": job['video_id'],
            "status": job['status'],
            "progress": job['progress'],
            "current_step": job['current_step'],
            "error_message": job.get('error_message'),
            "created_at": job['created_at'],
            "updated_at": job['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))