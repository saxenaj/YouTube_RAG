import yt_dlp
from pathlib import Path
from typing import Tuple, Optional
import re
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class DownloadService:
    def __init__(self):
        self.audio_dir = settings.AUDIO_DIR
        self.audio_dir.mkdir(exist_ok=True)
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def get_video_info(self, url: str) -> dict:
        """Get video metadata without downloading"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'duration': info.get('duration'),  # in seconds
                    'description': info.get('description'),
                    'uploader': info.get('uploader'),
                }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise
    
    async def download_audio(self, url: str, video_id: str = None) -> Tuple[str, dict]:
        """
        Download audio from YouTube video
        Returns: (audio_file_path, video_info)
        """
        if not video_id:
            video_id = self.extract_video_id(url)
        
        output_path = self.audio_dir / f"{video_id}.mp3"
        
        # Check if already downloaded
        if output_path.exists():
            logger.info(f"Audio already exists for {video_id}")
            info = self.get_video_info(url)
            return str(output_path), info
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': str(self.audio_dir / f'{video_id}.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading audio for {video_id}")
                info = ydl.extract_info(url, download=True)
                
                video_info = {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'description': info.get('description'),
                    'uploader': info.get('uploader'),
                }
                
                # Check duration limit
                if video_info['duration'] and video_info['duration'] > settings.MAX_VIDEO_DURATION:
                    self.cleanup_audio(video_id)
                    raise ValueError(
                        f"Video duration ({video_info['duration']}s) exceeds maximum "
                        f"allowed duration ({settings.MAX_VIDEO_DURATION}s)"
                    )
                
                logger.info(f"Audio downloaded successfully: {output_path}")
                return str(output_path), video_info
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Download error for {video_id}: {e}")
            raise ValueError(f"Failed to download video: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error downloading {video_id}: {e}")
            raise
    
    def cleanup_audio(self, video_id: str) -> None:
        """Delete audio file"""
        audio_path = self.audio_dir / f"{video_id}.mp3"
        if audio_path.exists():
            audio_path.unlink()
            logger.info(f"Cleaned up audio file: {audio_path}")
    
    def get_audio_path(self, video_id: str) -> Optional[str]:
        """Get path to audio file if it exists"""
        audio_path = self.audio_dir / f"{video_id}.mp3"
        return str(audio_path) if audio_path.exists() else None


# Global service instance
download_service = DownloadService()