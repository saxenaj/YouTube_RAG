#!/bin/bash

# YouTube RAG System Setup Script
# This script creates the complete project structure and copies files

set -e  # Exit on error

echo "🎥 YouTube RAG System - Setup Script"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run this script from the project root."
    exit 1
fi

# Create directory structure
print_info "Creating directory structure..."

mkdir -p app/api
mkdir -p app/services
mkdir -p app/models
mkdir -p app/utils
mkdir -p data/audio
mkdir -p data/chroma_db
mkdir -p logs
mkdir -p tests

print_success "Directory structure created"

# Create __init__.py files
print_info "Creating __init__.py files..."

touch app/__init__.py
touch app/api/__init__.py
touch app/services/__init__.py
touch app/models/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py

print_success "__init__.py files created"

# Create .env file from example
if [ ! -f ".env" ]; then
    print_info "Creating .env file from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env file created"
    else
        print_error ".env.example not found"
    fi
else
    print_info ".env file already exists, skipping..."
fi

# Create .gitignore
print_info "Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Data
data/audio/*.mp3
data/chroma_db/
data/metadata.db
logs/*.log

# Environment
.env

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore

# Temporary
*.tmp
*.bak
EOF

print_success ".gitignore created"

# Check Python version
print_info "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python version: $python_version"

# Check if Docker is installed
print_info "Checking Docker installation..."
if command -v docker &> /dev/null; then
    docker_version=$(docker --version | awk '{print $3}' | sed 's/,//')
    print_success "Docker version: $docker_version"
    
    if command -v docker-compose &> /dev/null; then
        compose_version=$(docker-compose --version | awk '{print $4}' | sed 's/,//')
        print_success "Docker Compose version: $compose_version"
    else
        print_error "Docker Compose not found. Please install docker-compose."
    fi
else
    print_error "Docker not found. Please install Docker to use the containerized setup."
fi

# Create a simple test file
print_info "Creating test file..."
cat > tests/test_helpers.py << 'EOF'
import pytest
from app.utils.helpers import (
    format_duration,
    format_timestamp,
    validate_youtube_url,
    sanitize_filename,
    estimate_tokens
)


def test_format_duration():
    assert format_duration(45) == "45s"
    assert format_duration(90) == "1m 30s"
    assert format_duration(3665) == "1h 1m 5s"


def test_format_timestamp():
    assert format_timestamp(125) == "02:05"
    assert format_timestamp(3665) == "01:01:05"


def test_validate_youtube_url():
    assert validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == True
    assert validate_youtube_url("https://youtu.be/dQw4w9WgXcQ") == True
    assert validate_youtube_url("https://example.com") == False


def test_sanitize_filename():
    assert sanitize_filename("My Video: Part 1") == "My_Video_Part_1"
    assert sanitize_filename("Test (2024)") == "Test_2024"


def test_estimate_tokens():
    assert estimate_tokens("Hello, world!") >= 3
    assert estimate_tokens("This is a longer sentence with more words.") >= 10
EOF

print_success "Test file created"

# Create Makefile for convenience
print_info "Creating Makefile..."
cat > Makefile << 'EOF'
.PHONY: help install test run docker-up docker-down docker-logs clean

help:
	@echo "YouTube RAG System - Available Commands:"
	@echo ""
	@echo "  make install       - Install Python dependencies"
	@echo "  make test         - Run tests"
	@echo "  make run          - Run application locally"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make docker-logs  - View Docker logs"
	@echo "  make clean        - Clean temporary files"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services are ready!"
	@echo "FastAPI: http://localhost:8000"
	@echo "Streamlit: http://localhost:8501"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
EOF

print_success "Makefile created"

# Summary
echo ""
echo "===================================="
echo "✅ Setup Complete!"
echo "===================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Install dependencies:"
echo "   For local development:"
echo "   $ python -m venv venv"
echo "   $ source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   $ pip install -r requirements.txt"
echo ""
echo "   OR use Docker:"
echo "   $ docker-compose up -d"
echo ""
echo "2. Configure settings:"
echo "   Edit .env file with your preferences"
echo ""
echo "3. Start the application:"
echo "   Local: $ uvicorn app.main:app --reload"
echo "   Docker: $ docker-compose up -d"
echo ""
echo "4. Access the UI:"
echo "   Streamlit: http://localhost:8501"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "For more information, see README.md"
echo ""

print_success "All done! Happy coding! 🚀"