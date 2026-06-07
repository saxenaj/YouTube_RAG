# 🎥 YouTube RAG System

A local-first RAG (Retrieval Augmented Generation) system that allows you to ask questions about YouTube videos using AI. Built with FastAPI, Whisper, ChromaDB, and Ollama.

## 🌟 Features

- **📥 Video Ingestion**: Automatically download and process YouTube videos
- **🎯 Accurate Transcription**: Using faster-whisper for efficient speech-to-text
- **🔍 Semantic Search**: Find relevant content using vector embeddings
- **💬 Interactive Q&A**: Ask questions and get AI-powered answers with source references
- **🖥️ User-Friendly UI**: Beautiful Streamlit interface
- **🐳 Easy Deployment**: One-command Docker setup
- **💾 Persistent Storage**: ChromaDB for vector storage, SQLite for metadata
- **🆓 100% Free**: No API costs, runs entirely on your machine

## 🏗️ Architecture

```
User Input → Download (yt-dlp) → Transcribe (Whisper) 
→ Chunk → Embed (sentence-transformers) → Store (ChromaDB)
→ Query → Retrieve → Answer (Ollama)
```

## 📋 Prerequisites

### Hardware Requirements

**Minimum:**
- 8GB RAM
- 10GB free disk space
- CPU only (slower transcription)

**Recommended:**
- 16GB RAM
- 20GB free disk space
- NVIDIA GPU with 6GB+ VRAM (10x faster transcription)

### Software Requirements

- Docker & Docker Compose
- (Optional) NVIDIA Docker runtime for GPU support

## 🚀 Quick Start

### 🐳 Option 1: Docker Pull (Fastest - Recommended)

No build required! Pull the pre-built image directly:

```bash
# Step 1: Pull the pre-built image
docker pull jatins08/youtube-rag:1.0

# Step 2: Pull Ollama image
docker pull ollama/ollama:latest

# Step 3: Clone repo (only for docker-compose.yml)
git clone https://github.com/saxenaj/YouTube_RAG.git
cd YouTube_RAG

# Step 4: Start everything
docker-compose up -d

# Step 5: Open browser
open http://localhost:8501
```

---

### 🔨 Option 2: Build from Source

Build the image yourself from source code:

```bash

### 1. Clone the Repository

```bash
git clone <repository-url>
cd youtube-rag
```

### 2. Start with Docker Compose

```bash
docker-compose up -d
```

This will:
- Pull Ollama container
- Build the application
- Download the Llama 3.1 8B model
- Start FastAPI server on `http://localhost:8000`
- Start Streamlit UI on `http://localhost:8501`

### 3. Access the UI

Open your browser and go to:
```
http://localhost:8501
```

### 4. Process Your First Video

1. Go to the "Add Video" tab
2. Paste a YouTube URL
3. Click "Process Video"
4. Wait for processing to complete (2-5 minutes for a 10-minute video)
5. Start asking questions!

## 📁 Project Structure

```
youtube-rag/
├── app/
│   ├── main.py                     # FastAPI application
│   ├── config.py                   # Configuration
│   ├── api/
│   │   ├── ingestion.py            # Video ingestion endpoints
│   │   ├── query.py                # Query endpoints
│   │   └── videos.py               # Video management
│   ├── services/
│   │   ├── download_service.py     # YouTube download
│   │   ├── transcription_service.py # Whisper transcription
│   │   ├── chunking_service.py     # Text chunking
│   │   ├── embedding_service.py    # Embeddings generation
│   │   ├── vector_store.py         # ChromaDB operations
│   │   ├── llm_service.py          # Ollama LLM
│   │   ├── video_processor.py      # Main orchestrator
│   │   └── retrieval_service.py    # Query & retrieval
│   └── models/
│       ├── schemas.py              # Pydantic models
│       └── database.py             # SQLite operations
├── data/
│   ├── audio/                      # Downloaded audio files
│   ├── chroma_db/                  # Vector database
│   └── metadata.db                 # SQLite database
├── streamlit_app.py                # Streamlit UI
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🎯 API Endpoints

### Ingestion

**POST** `/api/v1/ingest/`
- Submit a YouTube video for processing
- Body: `{"youtube_url": "https://..."}`

**GET** `/api/v1/ingest/status/{job_id}`
- Check processing status

### Query

**POST** `/api/v1/query/`
- Ask a question about a video
- Body: `{"video_id": "...", "question": "...", "top_k": 5}`

**POST** `/api/v1/query/stream`
- Stream answer generation (SSE)

### Videos

**GET** `/api/v1/videos/`
- List all videos

**GET** `/api/v1/videos/{video_id}`
- Get video details

**DELETE** `/api/v1/videos/{video_id}`
- Delete a video

## ⚙️ Configuration

Edit `.env` or `app/config.py`:

```python
# Models
WHISPER_MODEL = "base"  # tiny, base, small, medium, large-v2
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama3.1:8b"

# Chunking
CHUNK_SIZE = 500  # tokens
CHUNK_OVERLAP = 50

# Retrieval
TOP_K_CHUNKS = 5
SIMILARITY_THRESHOLD = 0.5

# Processing
MAX_VIDEO_DURATION = 7200  # 2 hours
CLEANUP_AUDIO_AFTER_PROCESSING = True
```

## 🔧 Advanced Usage

### Using Different Models

**Whisper Models** (trade-off between speed and accuracy):
- `tiny` - Fastest, least accurate
- `base` - Good balance (default)
- `small` - Better accuracy
- `medium` - High accuracy
- `large-v2` - Best accuracy, slowest

**LLM Models**:
```bash
# Switch to smaller/faster model
docker exec youtube-rag-ollama ollama pull llama3.2:3b

# Update docker-compose.yml
environment:
  - LLM_MODEL=llama3.2:3b
```

### GPU Support

Uncomment in `docker-compose.yml`:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

Update config:
```python
WHISPER_DEVICE = "cuda"
```

### Running Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Install and start Ollama
ollama serve
ollama pull llama3.1:8b

# Start FastAPI
uvicorn app.main:app --reload

# Start Streamlit (new terminal)
streamlit run streamlit_app.py
```

## 🐛 Troubleshooting

### Ollama not connecting
```bash
# Check if Ollama is running
docker logs youtube-rag-ollama

# Restart Ollama
docker-compose restart ollama
```

### Out of memory errors
- Reduce `CHUNK_SIZE` to 300
- Use smaller Whisper model (`tiny` or `base`)
- Use smaller LLM (`llama3.2:3b`)

### Slow transcription
- Enable GPU support
- Use smaller Whisper model
- Process shorter videos

### Video download fails
- Check if video is available in your region
- Try with `--no-check-certificate` in yt-dlp options
- Ensure video is not private or age-restricted

## 📊 Performance Benchmarks

**10-minute video processing (base model, CPU)**:
- Download: ~30 seconds
- Transcription: ~2 minutes
- Chunking + Embedding: ~30 seconds
- **Total: ~3 minutes**

**Query response time**:
- Vector search: ~50ms
- LLM generation: ~2-5 seconds (streaming)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Multi-language support
- Batch video processing
- Better chunk boundary detection
- Query result caching
- Web UI improvements

## 📝 License

MIT License - feel free to use for personal or commercial projects

## 🙏 Acknowledgments

- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [ChromaDB](https://www.trychroma.com/)
- [Ollama](https://ollama.ai/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [sentence-transformers](https://www.sbert.net/)

## 📧 Support

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with:
   - Error messages/logs
   - System specifications
   - Steps to reproduce

---

**Happy learning! 🚀**