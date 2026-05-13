from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Project paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    AUDIO_DIR: Path = DATA_DIR / "audio"
    CHROMA_DB_PATH: Path = DATA_DIR / "chroma_db"
    SQLITE_DB_PATH: Path = DATA_DIR / "metadata.db"
    
    # Model settings
    WHISPER_MODEL: str = "base"  # tiny, base, small, medium, large-v2
    WHISPER_DEVICE: str = "cpu"  # cpu or cuda
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    LLM_MODEL: str = "llama3.1:8b"
    
    # Ollama settings
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 120
    
    # Chunking settings
    CHUNK_SIZE: int = 500  # tokens
    CHUNK_OVERLAP: int = 50  # tokens
    
    # Retrieval settings
    TOP_K_CHUNKS: int = 5
    SIMILARITY_THRESHOLD: float = 0.5
    
    # Processing settings
    MAX_CONCURRENT_JOBS: int = 2
    CLEANUP_AUDIO_AFTER_PROCESSING: bool = True
    MAX_VIDEO_DURATION: int = 7200  # 2 hours in seconds
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "YouTube RAG System"
    VERSION: str = "1.0.0"
    
    # ChromaDB settings
    CHROMA_COLLECTION_NAME: str = "youtube_transcripts"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        self.DATA_DIR.mkdir(exist_ok=True)
        self.AUDIO_DIR.mkdir(exist_ok=True)
        self.CHROMA_DB_PATH.mkdir(exist_ok=True)


settings = Settings()
settings.create_directories()