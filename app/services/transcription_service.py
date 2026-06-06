import whisper
from typing import List
from app.config import settings
from app.models.schemas import TranscriptSegment
import logging

logger = logging.getLogger(__name__)


class TranscriptionService:
    def __init__(self):
        self.model = None
        self.model_size = settings.WHISPER_MODEL
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
    
    async def transcribe(self, audio_path: str) -> List[TranscriptSegment]:
        """
        Transcribe audio file to text with timestamps
        Returns list of TranscriptSegment objects
        """
        logger.info(f"Starting transcription for: {audio_path}")
        
        try:
            # Transcribe with timestamps
            result = self.model.transcribe(
                audio_path,
                language="en",
                verbose=False
            )
            
            logger.info(f"Detected language: {result.get('language', 'unknown')}")
            
            # Convert to TranscriptSegment objects
            transcript_segments = []
            for segment in result['segments']:
                transcript_segments.append(
                    TranscriptSegment(
                        text=segment['text'].strip(),
                        start=segment['start'],
                        end=segment['end']
                    )
                )
            
            logger.info(f"Transcription completed: {len(transcript_segments)} segments")
            return transcript_segments
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
    
    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def get_full_transcript(self, segments: List[TranscriptSegment]) -> str:
        """Combine all segments into single text"""
        return " ".join(segment.text for segment in segments)


# Global service instance
transcription_service = TranscriptionService()