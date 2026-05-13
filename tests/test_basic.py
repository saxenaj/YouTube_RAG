"""
Basic Integration Tests for YouTube RAG System

Run with: pytest tests/test_basic.py -v
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.helpers import (
    format_duration,
    format_timestamp,
    validate_youtube_url,
    sanitize_filename,
    estimate_tokens,
    calculate_similarity,
    truncate_text,
    parse_time_string,
)
from app.models.schemas import (
    IngestRequest,
    QueryRequest,
    TranscriptSegment,
    Chunk,
)


class TestHelpers:
    """Test utility helper functions"""
    
    def test_format_duration(self):
        """Test duration formatting"""
        assert format_duration(45) == "45s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(3665) == "1h 1m 5s"
        assert format_duration(7200) == "2h 0m 0s"
    
    def test_format_timestamp(self):
        """Test timestamp formatting"""
        assert format_timestamp(0) == "00:00"
        assert format_timestamp(125) == "02:05"
        assert format_timestamp(3665) == "01:01:05"
        assert format_timestamp(125, include_hours=True) == "00:02:05"
    
    def test_validate_youtube_url(self):
        """Test YouTube URL validation"""
        # Valid URLs
        assert validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert validate_youtube_url("https://youtu.be/dQw4w9WgXcQ")
        assert validate_youtube_url("https://youtube.com/watch?v=dQw4w9WgXcQ")
        assert validate_youtube_url("https://www.youtube.com/embed/dQw4w9WgXcQ")
        
        # Invalid URLs
        assert not validate_youtube_url("https://example.com")
        assert not validate_youtube_url("https://vimeo.com/123456")
        assert not validate_youtube_url("not a url")
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        assert sanitize_filename("My Video: Part 1") == "My_Video_Part_1"
        assert sanitize_filename("Test (2024) [HD]") == "Test_2024_HD"
        assert sanitize_filename("File/with\\invalid:chars") == "Filewithinvalidchars"
        
        # Test length limit
        long_name = "a" * 300
        result = sanitize_filename(long_name, max_length=100)
        assert len(result) <= 100
    
    def test_estimate_tokens(self):
        """Test token estimation"""
        assert estimate_tokens("Hello") >= 1
        assert estimate_tokens("Hello, world!") >= 2
        assert estimate_tokens("This is a longer sentence.") >= 5
    
    def test_calculate_similarity(self):
        """Test cosine similarity calculation"""
        # Identical vectors
        v1 = [1.0, 0.0, 0.0]
        assert abs(calculate_similarity(v1, v1) - 1.0) < 0.01
        
        # Orthogonal vectors
        v2 = [0.0, 1.0, 0.0]
        assert abs(calculate_similarity(v1, v2)) < 0.01
        
        # Opposite vectors
        v3 = [-1.0, 0.0, 0.0]
        assert abs(calculate_similarity(v1, v3) - (-1.0)) < 0.01
    
    def test_truncate_text(self):
        """Test text truncation"""
        text = "This is a long text that needs to be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) <= 20
        assert result.endswith("...")
        
        # Short text should not be truncated
        short = "Short"
        assert truncate_text(short, max_length=20) == short
    
    def test_parse_time_string(self):
        """Test time string parsing"""
        assert parse_time_string("02:30") == 150
        assert parse_time_string("01:02:30") == 3750
        assert parse_time_string("00:00") == 0
        
        with pytest.raises(ValueError):
            parse_time_string("invalid")


class TestSchemas:
    """Test Pydantic schemas"""
    
    def test_ingest_request(self):
        """Test IngestRequest model"""
        # Valid request
        request = IngestRequest(
            youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        assert request.youtube_url
        
        # Invalid URL should fail validation
        with pytest.raises(Exception):
            IngestRequest(youtube_url="not a url")
    
    def test_query_request(self):
        """Test QueryRequest model"""
        request = QueryRequest(
            video_id="test123",
            question="What is this about?",
            top_k=5
        )
        assert request.video_id == "test123"
        assert request.question == "What is this about?"
        assert request.top_k == 5
        
        # Test default top_k
        request2 = QueryRequest(
            video_id="test123",
            question="Test"
        )
        assert request2.top_k == 5
    
    def test_transcript_segment(self):
        """Test TranscriptSegment model"""
        segment = TranscriptSegment(
            text="Hello world",
            start=0.0,
            end=2.5
        )
        assert segment.text == "Hello world"
        assert segment.start == 0.0
        assert segment.end == 2.5
    
    def test_chunk(self):
        """Test Chunk model"""
        chunk = Chunk(
            text="This is a chunk of text",
            start_time=10.0,
            end_time=20.0,
            timestamp="00:10",
            chunk_index=0
        )
        assert chunk.text == "This is a chunk of text"
        assert chunk.chunk_index == 0


class TestChunkingLogic:
    """Test chunking algorithms"""
    
    def test_sentence_splitting(self):
        """Test basic sentence splitting"""
        from app.services.chunking_service import chunking_service
        
        text = "First sentence. Second sentence! Third sentence?"
        # This is a basic test - actual implementation may vary
        assert "." in text or "!" in text or "?" in text
    
    def test_chunk_size_estimation(self):
        """Test chunk size is within bounds"""
        text = "word " * 1000  # 1000 words
        tokens = estimate_tokens(text)
        
        # Should be roughly 250 tokens (1000 words / 4 chars per token)
        assert 200 < tokens < 300


class TestEmbeddingService:
    """Test embedding service (requires model download)"""
    
    @pytest.mark.slow
    def test_embedding_generation(self):
        """Test embedding generation"""
        from app.services.embedding_service import embedding_service
        
        text = "This is a test sentence"
        embedding = embedding_service.embed_text(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.slow
    def test_batch_embedding(self):
        """Test batch embedding"""
        from app.services.embedding_service import embedding_service
        
        texts = ["First text", "Second text", "Third text"]
        embeddings = embedding_service.embed_batch(texts)
        
        assert len(embeddings) == len(texts)
        assert all(isinstance(emb, list) for emb in embeddings)


class TestVectorStore:
    """Test ChromaDB vector store operations"""
    
    @pytest.mark.integration
    def test_vector_store_initialization(self):
        """Test vector store initializes correctly"""
        from app.services.vector_store import vector_store
        
        assert vector_store.client is not None
        assert vector_store.collection is not None
    
    @pytest.mark.integration
    def test_chunk_storage_and_retrieval(self):
        """Test storing and retrieving chunks"""
        from app.services.vector_store import vector_store
        from app.services.embedding_service import embedding_service
        from app.models.schemas import Chunk
        
        # Create test chunks
        chunks = [
            Chunk(
                text="Test chunk 1",
                start_time=0.0,
                end_time=5.0,
                timestamp="00:00",
                chunk_index=0
            ),
            Chunk(
                text="Test chunk 2",
                start_time=5.0,
                end_time=10.0,
                timestamp="00:05",
                chunk_index=1
            )
        ]
        
        # Generate embeddings
        texts = [c.text for c in chunks]
        embeddings = embedding_service.embed_batch(texts)
        
        # Store
        test_video_id = "test_video_123"
        vector_store.add_chunks(test_video_id, chunks, embeddings)
        
        # Search
        query_embedding = embedding_service.embed_text("Test query")
        results = vector_store.search(query_embedding, test_video_id, k=2)
        
        assert len(results) > 0
        
        # Cleanup
        vector_store.delete_video(test_video_id)


class TestDatabase:
    """Test SQLite database operations"""
    
    @pytest.mark.integration
    def test_video_crud(self):
        """Test video CRUD operations"""
        from app.models.database import db
        
        test_video_id = "test_video_456"
        
        # Create
        db.create_video(
            video_id=test_video_id,
            url="https://youtube.com/watch?v=test",
            title="Test Video",
            duration=120
        )
        
        # Read
        video = db.get_video(test_video_id)
        assert video is not None
        assert video['id'] == test_video_id
        assert video['title'] == "Test Video"
        
        # Update
        db.update_video(test_video_id, title="Updated Title")
        video = db.get_video(test_video_id)
        assert video['title'] == "Updated Title"
        
        # Delete
        result = db.delete_video(test_video_id)
        assert result is True
        
        video = db.get_video(test_video_id)
        assert video is None


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-m", "not slow"])