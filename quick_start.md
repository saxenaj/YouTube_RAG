# 🚀 Quick Start Guide - YouTube RAG System

Get up and running in 5 minutes!

## Option 1: Docker (Recommended) 🐳

### Step 1: Prerequisites
- Docker Desktop installed and running
- 10GB free disk space

### Step 2: Clone and Setup
```bash
# Clone repository
git clone <your-repo-url>
cd youtube-rag

# Copy environment file
cp .env.example .env

# Make setup script executable
chmod +x setup.sh
./setup.sh
```

### Step 3: Start Services
```bash
docker-compose up -d
```

Wait ~30 seconds for services to initialize.

### Step 4: Access UI
Open browser: **http://localhost:8501**

### Step 5: Process Your First Video
1. Click "Add Video" tab
2. Paste: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
3. Click "Process Video"
4. Wait 2-3 minutes
5. Start asking questions!

---

## Option 2: Local Development 💻

### Step 1: Prerequisites
```bash
# Check Python version (3.10+ required)
python3 --version

# Install FFmpeg
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### Step 2: Setup Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Install Ollama
```bash
# Download from https://ollama.ai
# Or use package manager:

# macOS:
brew install ollama

# Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Windows:
# Download installer from ollama.ai

# Pull the model
ollama pull llama3.1:8b
```

### Step 4: Start Services

**Terminal 1 - Ollama:**
```bash
ollama serve
```

**Terminal 2 - FastAPI:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Streamlit:**
```bash
streamlit run streamlit_app.py
```

### Step 5: Access
- **UI:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

---

## 🎯 First Video Test

Use this short video to test quickly:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Example questions to try:
- "What is this video about?"
- "Summarize the main points"
- "What happens at the beginning?"

---

## 📊 Verify Installation

### Check Docker Services
```bash
docker-compose ps

# Expected output:
# youtube-rag-ollama    running
# youtube-rag-app       running
```

### Check Local Services
```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test FastAPI
curl http://localhost:8000/health

# Expected: {"status":"healthy","version":"1.0.0"}
```

---

## 🐛 Quick Troubleshooting

### Docker Issues

**Services won't start:**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart
```

**Port already in use:**
```bash
# Edit docker-compose.yml and change ports:
ports:
  - "8001:8000"  # Changed from 8000
  - "8502:8501"  # Changed from 8501
```

### Local Setup Issues

**Import errors:**
```bash
# Make sure virtual environment is activated
which python  # Should show path to venv

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Ollama not responding:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
killall ollama
ollama serve
```

**Module not found:**
```bash
# Make sure you're in project root
pwd  # Should end with /youtube-rag

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 🎓 Next Steps

### 1. Configure Models
Edit `.env` to use different models:
```bash
# Faster transcription (less accurate)
WHISPER_MODEL=tiny

# Smaller LLM (faster, less capable)
LLM_MODEL=llama3.2:3b
```

### 2. Enable GPU (if available)
```bash
# Check GPU
nvidia-smi

# Uncomment in docker-compose.yml:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]

# Update .env:
WHISPER_DEVICE=cuda
```

### 3. Process Multiple Videos
```bash
# Use API directly
curl -X POST http://localhost:8000/api/v1/ingest/ \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://youtube.com/watch?v=VIDEO_ID"}'
```

### 4. Query via API
```bash
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "VIDEO_ID",
    "question": "What is this about?",
    "top_k": 5
  }'
```

---

## 📚 Learning Resources

### Understanding the Code
1. Start with `streamlit_app.py` (UI entry point)
2. Follow `app/main.py` (API entry point)
3. Check `app/services/video_processor.py` (main logic)
4. Explore other services as needed

### Debugging
```bash
# Watch logs in real-time
tail -f logs/youtube_rag_*.log

# Docker logs
docker-compose logs -f app

# Check database
sqlite3 data/metadata.db "SELECT * FROM videos;"
```

### Performance Tuning
```python
# In .env:
CHUNK_SIZE=300        # Smaller = more chunks, slower
TOP_K_CHUNKS=3        # Fewer = faster, less context
WHISPER_MODEL=tiny    # Faster transcription
```

---

## 🎉 Success Checklist

- [ ] Docker/Python environment running
- [ ] All services accessible (ports 8000, 8501, 11434)
- [ ] First video processed successfully
- [ ] Questions answered with sources
- [ ] No error messages in logs

---

## 💡 Tips for Best Results

1. **Video Selection**
   - Start with 5-10 minute videos
   - Educational content works best
   - Clear audio quality important

2. **Question Quality**
   - Be specific: "What does the speaker say about X?"
   - Use timestamps: "What happens at 2:30?"
   - Ask for summaries: "Summarize the key points"

3. **Performance**
   - First video takes longer (model loading)
   - GPU makes transcription 10x faster
   - Smaller models = faster but less accurate

---

## 🆘 Getting Help

1. **Check Documentation**
   - README.md - Full documentation
   - FILE_TREE.md - Code structure
   - API docs at http://localhost:8000/docs

2. **Common Issues**
   - Out of memory → Use smaller models
   - Slow transcription → Enable GPU or use tiny model
   - Video won't download → Check if video is available in your region

3. **Report Issues**
   - Include error messages
   - Specify: Docker or local setup
   - System specs (RAM, GPU, OS)

---

**Ready to dive deeper?** Check out README.md for complete documentation!

**Happy learning! 🚀**