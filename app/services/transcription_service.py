from faster_whisper import WhisperModel
from typing import List
from app.config import settings
from app.models.schemas import TranscriptSegment
import logging

logger = logging.getLogger(__name__)


class TranscriptionService:
    def __init__(self):
        self.model = None
        self.model_size = settings.WHISPER_MODEL
        self.device = settings.WHISPER_DEVICE
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model (lazy loading)"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="int8" if self.device == "cpu" else "float16"
            )
            logger.info("Whisper model loaded successfully")
    
    async def transcribe(self, audio_path: str) -> List[TranscriptSegment]:
        """
        Transcribe audio file to text with timestamps
        Returns list of TranscriptSegment objects
        """
        logger.info(f"Starting transcription for: {audio_path}")
        
        try:
            # Transcribe with word-level timestamps
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=5,
                word_timestamps=False,  # Set to True for word-level
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(
                    min_silence_duration_ms=500
                )
            )
            
            logger.info(
                f"Detected language: {info.language} "
                f"(probability: {info.language_probability:.2f})"
            )
            
            # Convert to TranscriptSegment objects
            transcript_segments = []
            for segment in segments:
                transcript_segments.append(
                    TranscriptSegment(
                        text=segment.text.strip(),
                        start=segment.start,
                        end=segment.end
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