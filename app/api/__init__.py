"""
YouTube RAG System - Main Application Package

A local-first RAG system for YouTube videos using:
- FastAPI for API
- Whisper for transcription
- ChromaDB for vector storage
- Ollama for LLM inference
"""

__version__ = "1.0.0"
__author__ = "Jatin Saxeena"

from app.config import settings

# Make settings available at package level
__all__ = ["settings"]