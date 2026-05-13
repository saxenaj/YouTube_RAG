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
