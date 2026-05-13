from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import QueryRequest, QueryResponse, JobStatus
from app.services.retrieval_service import retrieval_service
from app.models.database import db
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def query_video(request: QueryRequest):
    """
    Ask a question about a video
    
    This endpoint:
    1. Validates the video exists and is processed
    2. Retrieves relevant chunks from vector store
    3. Generates answer using LLM
    4. Returns answer with source references
    """
    try:
        # Check if video exists and is completed
        video = db.get_video(request.video_id)
        
        if not video:
            raise HTTPException(
                status_code=404,
                detail=f"Video {request.video_id} not found. Please ingest it first."
            )
        
        if video['status'] != JobStatus.COMPLETED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Video is not ready for queries. Current status: {video['status']}"
            )
        
        # Process query
        logger.info(f"Processing query for video {request.video_id}: {request.question}")
        
        response = await retrieval_service.query(
            question=request.question,
            video_id=request.video_id,
            top_k=request.top_k
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")


@router.post("/stream")
async def query_video_stream(request: QueryRequest):
    """
    Ask a question with streaming response
    
    Returns Server-Sent Events (SSE) stream with:
    - Sources
    - Answer chunks (streamed as they're generated)
    - Completion signal
    """
    try:
        # Validate video
        video = db.get_video(request.video_id)
        
        if not video:
            raise HTTPException(
                status_code=404,
                detail=f"Video {request.video_id} not found"
            )
        
        if video['status'] != JobStatus.COMPLETED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Video not ready. Status: {video['status']}"
            )
        
        # Create streaming generator
        async def event_generator():
            try:
                async for event in retrieval_service.query_streaming(
                    question=request.question,
                    video_id=request.video_id,
                    top_k=request.top_k
                ):
                    # Format as SSE
                    yield f"data: {json.dumps(event)}\n\n"
                    
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                error_event = {
                    "type": "error",
                    "data": str(e)
                }
                yield f"data: {json.dumps(error_event)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))