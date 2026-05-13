from fastapi import APIRouter, HTTPException
from app.models.schemas import VideoListResponse, VideoInfo, DeleteResponse
from app.models.database import db
from app.services.video_processor import video_processor
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=VideoListResponse)
async def list_videos(limit: int = 100, offset: int = 0):
    """
    List all processed videos
    
    Args:
        limit: Maximum number of videos to return
        offset: Number of videos to skip (for pagination)
    """
    try:
        videos = db.list_videos(limit=limit, offset=offset)
        total = db.get_video_count()
        
        video_list = [
            VideoInfo(
                id=v['id'],
                url=v['url'],
                title=v['title'] or "Unknown",
                duration=v['duration'] or 0,
                status=v['status'],
                chunk_count=v['chunk_count'] or 0,
                created_at=v['created_at'],
                completed_at=v.get('completed_at')
            )
            for v in videos
        ]
        
        return VideoListResponse(
            videos=video_list,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}", response_model=VideoInfo)
async def get_video(video_id: str):
    """
    Get detailed information about a specific video
    """
    try:
        video = db.get_video(video_id)
        
        if not video:
            raise HTTPException(
                status_code=404,
                detail=f"Video {video_id} not found"
            )
        
        return VideoInfo(
            id=video['id'],
            url=video['url'],
            title=video['title'] or "Unknown",
            duration=video['duration'] or 0,
            status=video['status'],
            chunk_count=video['chunk_count'] or 0,
            created_at=video['created_at'],
            completed_at=video.get('completed_at')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{video_id}", response_model=DeleteResponse)
async def delete_video(video_id: str):
    """
    Delete a video and all associated data
    
    This will:
    - Remove chunks from vector store
    - Delete audio file
    - Remove database records
    """
    try:
        # Check if video exists
        video = db.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=404,
                detail=f"Video {video_id} not found"
            )
        
        # Delete video
        success = await video_processor.delete_video(video_id)
        
        if success:
            return DeleteResponse(
                success=True,
                message=f"Video {video_id} deleted successfully",
                video_id=video_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete video"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/chunks")
async def get_video_chunks(video_id: str, limit: int = 10):
    """
    Get sample chunks from a video (for debugging/inspection)
    """
    try:
        from app.services.vector_store import vector_store
        
        # Check if video exists
        video = db.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=404,
                detail=f"Video {video_id} not found"
            )
        
        # Get chunks (we'll use a dummy query to retrieve some)
        results = vector_store.collection.get(
            where={"video_id": video_id},
            limit=limit,
            include=["documents", "metadatas"]
        )
        
        chunks = []
        if results['ids']:
            for i in range(len(results['ids'])):
                chunks.append({
                    "id": results['ids'][i],
                    "text": results['documents'][i],
                    "metadata": results['metadatas'][i]
                })
        
        return {
            "video_id": video_id,
            "total_chunks": video['chunk_count'],
            "sample_chunks": chunks
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))