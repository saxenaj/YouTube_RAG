from typing import List
from app.config import settings
from app.models.schemas import TranscriptSegment, Chunk
import logging
import re

logger = logging.getLogger(__name__)


class ChunkingService:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE  # tokens
        self.chunk_overlap = settings.CHUNK_OVERLAP  # tokens
        # Rough estimate: 1 token ≈ 4 characters
        self.chars_per_token = 4
    
    def chunk_transcript(self, segments: List[TranscriptSegment]) -> List[Chunk]:
        """
        Chunk transcript segments into overlapping chunks
        Strategy:
        1. Combine segments into sentences
        2. Group sentences into chunks of ~chunk_size tokens
        3. Add overlap between chunks
        4. Preserve timestamps
        """
        logger.info(f"Chunking {len(segments)} transcript segments")
        
        # First, combine segments and split into sentences
        sentences = self._split_into_sentences(segments)
        
        # Group sentences into chunks
        chunks = self._create_chunks(sentences)
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _split_into_sentences(self, segments: List[TranscriptSegment]) -> List[dict]:
        """Split segments into sentence-like units with timestamps"""
        sentences = []
        
        for segment in segments:
            # Split text on sentence boundaries
            text_sentences = re.split(r'[.!?]+\s+', segment.text.strip())
            
            # Estimate timestamp for each sentence within the segment
            segment_duration = segment.end - segment.start
            num_sentences = len(text_sentences)
            
            for i, sent in enumerate(text_sentences):
                if not sent.strip():
                    continue
                
                # Proportional timestamp estimation
                start_time = segment.start + (i * segment_duration / num_sentences)
                end_time = segment.start + ((i + 1) * segment_duration / num_sentences)
                
                sentences.append({
                    'text': sent.strip(),
                    'start': start_time,
                    'end': end_time
                })
        
        return sentences
    
    def _create_chunks(self, sentences: List[dict]) -> List[Chunk]:
        """Group sentences into chunks with overlap"""
        chunks = []
        current_chunk_text = []
        current_chunk_tokens = 0
        chunk_start_time = None
        chunk_end_time = None
        chunk_index = 0
        
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            sentence_tokens = len(sentence['text']) // self.chars_per_token
            
            # Start new chunk if empty
            if not current_chunk_text:
                chunk_start_time = sentence['start']
            
            # Check if adding this sentence exceeds chunk size
            if current_chunk_tokens + sentence_tokens > self.chunk_size and current_chunk_text:
                # Save current chunk
                chunk_end_time = sentences[i-1]['end']
                chunks.append(self._create_chunk(
                    current_chunk_text,
                    chunk_start_time,
                    chunk_end_time,
                    chunk_index
                ))
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_tokens = 0
                overlap_start = i - 1
                
                # Go back to include overlap
                while overlap_start >= 0 and overlap_tokens < self.chunk_overlap:
                    overlap_sentence = sentences[overlap_start]
                    overlap_tokens += len(overlap_sentence['text']) // self.chars_per_token
                    overlap_start -= 1
                
                # Reset for new chunk with overlap
                overlap_start = max(0, overlap_start + 1)
                current_chunk_text = [s['text'] for s in sentences[overlap_start:i]]
                current_chunk_tokens = sum(
                    len(s['text']) // self.chars_per_token 
                    for s in sentences[overlap_start:i]
                )
                chunk_start_time = sentences[overlap_start]['start']
                continue
            
            # Add sentence to current chunk
            current_chunk_text.append(sentence['text'])
            current_chunk_tokens += sentence_tokens
            chunk_end_time = sentence['end']
            i += 1
        
        # Don't forget the last chunk
        if current_chunk_text:
            chunks.append(self._create_chunk(
                current_chunk_text,
                chunk_start_time,
                chunk_end_time,
                chunk_index
            ))
        
        return chunks
    
    def _create_chunk(self, texts: List[str], start_time: float, 
                     end_time: float, chunk_index: int) -> Chunk:
        """Create a Chunk object"""
        return Chunk(
            text=" ".join(texts),
            start_time=start_time,
            end_time=end_time,
            timestamp=self._format_timestamp(start_time),
            chunk_index=chunk_index
        )
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


# Global service instance
chunking_service = ChunkingService()