# 🧪 Testing Guide - YouTube RAG System

Complete guide to testing the YouTube RAG system.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Files](#test-files)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Writing Tests](#writing-tests)
6. [CI/CD Integration](#cicd-integration)

---

## 🚀 Quick Start

### Install Test Dependencies

```bash
# Core testing
pip install pytest pytest-asyncio

# Additional tools (optional)
pip install pytest-cov pytest-watch pytest-xdist
```

### Run All Tests

```bash
# Simple
pytest

# Verbose
pytest -v

# With coverage
pytest --cov=app --cov-report=html
```

### Use Test Runner Script

```bash
chmod +x run_tests.sh
./run_tests.sh
```

---

## 📁 Test Files

### Current Test Structure

```
tests/
├── __init__.py
├── test_helpers.py         # Unit tests for utility functions
├── test_basic.py           # Integration tests
├── test_services.py        # Service layer tests (TODO)
├── test_api.py            # API endpoint tests (TODO)
└── conftest.py            # Pytest fixtures (TODO)
```

### Test File: `test_helpers.py`

**Location:** `tests/test_helpers.py`  
**Lines:** ~450  
**Tests:** 50+ test cases

**Coverage:**
- ✅ `format_duration()` - 4 tests
- ✅ `format_timestamp()` - 4 tests
- ✅ `validate_youtube_url()` - 2 tests
- ✅ `extract_video_id_from_url()` - 6 tests
- ✅ `sanitize_filename()` - 5 tests
- ✅ `estimate_tokens()` - 4 tests
- ✅ `calculate_similarity()` - 5 tests
- ✅ `truncate_text()` - 4 tests
- ✅ `parse_time_string()` - 3 tests
- ✅ `chunk_list()` - 4 tests
- ✅ `generate_hash()` - 4 tests
- ✅ `time_ago()` - 6 tests
- ✅ `batch_items()` - 4 tests

### Test File: `test_basic.py`

**Location:** `tests/test_basic.py`  
**Lines:** ~300  
**Tests:** 20+ test cases

**Coverage:**
- ✅ Schema validation
- ✅ Database operations
- ✅ Embedding generation (slow)
- ✅ Vector store (integration)
- ✅ Chunking logic

---

## 🏃 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_helpers.py

# Run specific test class
pytest tests/test_helpers.py::TestFormatDuration

# Run specific test
pytest tests/test_helpers.py::TestFormatDuration::test_seconds_only

# Run with verbose output
pytest -v

# Run with extra verbose output
pytest -vv

# Show print statements
pytest -s
```

### Test Markers

```bash
# Run only unit tests (fast)
pytest -m "not integration and not slow"

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run only API tests
pytest -m api
```

### Coverage Reports

```bash
# Terminal coverage
pytest --cov=app

# HTML coverage report
pytest --cov=app --cov-report=html

# Both terminal and HTML
pytest --cov=app --cov-report=term --cov-report=html

# Show missing lines
pytest --cov=app --cov-report=term-missing

# Minimum coverage threshold (fails if below)
pytest --cov=app --cov-fail-under=80
```

### Parallel Testing

```bash
# Install plugin
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4

# Auto-detect number of CPUs
pytest -n auto
```

### Watch Mode

```bash
# Install plugin
pip install pytest-watch

# Run in watch mode
ptw

# With specific options
ptw -- -v --cov=app
```

---

## 🏷️ Test Categories

### Unit Tests
**Fast, no external dependencies**

```python
@pytest.mark.unit
def test_format_duration():
    assert format_duration(90) == "1m 30s"
```

```bash
# Run unit tests
pytest -m unit
```

### Integration Tests
**Require services (database, vector store)**

```python
@pytest.mark.integration
def test_vector_store():
    # Requires ChromaDB running
    vector_store.add_chunks(...)
```

```bash
# Run integration tests
pytest -m integration
```

### Slow Tests
**Tests that take >1 second**

```python
@pytest.mark.slow
def test_embedding_generation():
    # Downloads model first time
    embedding_service.embed_text("test")
```

```bash
# Skip slow tests
pytest -m "not slow"
```

### API Tests

```python
@pytest.mark.api
def test_ingest_endpoint():
    response = client.post("/api/v1/ingest/", ...)
    assert response.status_code == 200
```

---

## ✍️ Writing Tests

### Test Structure

```python
import pytest
from app.utils.helpers import some_function

class TestSomeFunction:
    """Test some_function utility"""
    
    def test_basic_case(self):
        """Test basic functionality"""
        result = some_function("input")
        assert result == "expected"
    
    def test_edge_case(self):
        """Test edge case"""
        result = some_function("")
        assert result == ""
    
    def test_error_handling(self):
        """Test error is raised"""
        with pytest.raises(ValueError):
            some_function(None)
```

### Fixtures

Create `tests/conftest.py`:

```python
import pytest
from app.models.database import Database

@pytest.fixture
def test_db():
    """Provide a test database"""
    db = Database(":memory:")
    yield db
    # Cleanup happens here

@pytest.fixture
def sample_video_data():
    """Provide sample video data"""
    return {
        "id": "test123",
        "title": "Test Video",
        "duration": 120
    }

# Usage in tests
def test_video_creation(test_db, sample_video_data):
    test_db.create_video(**sample_video_data)
    video = test_db.get_video("test123")
    assert video is not None
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", 5),
    ("world", 5),
    ("", 0),
])
def test_length(input, expected):
    assert len(input) == expected
```

### Mocking

```python
from unittest.mock import Mock, patch

def test_with_mock():
    mock_service = Mock()
    mock_service.download.return_value = "path/to/file"
    
    result = process_with_service(mock_service)
    
    mock_service.download.assert_called_once()
    assert result == "path/to/file"

@patch('app.services.download_service.yt_dlp')
def test_with_patch(mock_yt_dlp):
    mock_yt_dlp.YoutubeDL.return_value.extract_info.return_value = {
        'id': 'test123',
        'title': 'Test Video'
    }
    
    # Your test code here
```

---

## 📊 Coverage Goals

### Current Coverage
- **Utilities:** ~95%
- **Models:** ~80%
- **Services:** ~60% (TODO: increase)
- **API:** ~50% (TODO: increase)

### Target Coverage
- **Overall:** 80%+
- **Critical paths:** 95%+
- **Utilities:** 95%+
- **Services:** 85%+
- **API:** 80%+

---

## 🔄 CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Running tests before commit..."

pytest tests/ -m "not slow and not integration" -v

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "Tests passed. Proceeding with commit."
```

---

## 📝 Testing Checklist

### Before Committing
- [ ] All tests pass: `pytest`
- [ ] No new warnings
- [ ] Coverage doesn't decrease
- [ ] New code has tests
- [ ] Tests are documented

### Before Release
- [ ] All tests pass including slow/integration
- [ ] Coverage > 80%
- [ ] API tests pass
- [ ] End-to-end test passes
- [ ] Performance tests pass

---

## 🐛 Debugging Tests

### Run with Debugger

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start
pytest --trace
```

### Show Full Output

```bash
# Show print statements
pytest -s

# Show full traceback
pytest --tb=long

# Show local variables in traceback
pytest --tb=auto -vv
```

### Run Single Test with Debug

```python
if __name__ == "__main__":
    # Run this file directly for debugging
    pytest.main([__file__, "-v", "-s"])
```

---

## 📚 Additional Resources

### Pytest Documentation
- Official docs: https://docs.pytest.org/
- Best practices: https://docs.pytest.org/en/stable/goodpractices.html

### Testing Patterns
- Arrange-Act-Assert (AAA) pattern
- Given-When-Then (GWT) pattern
- Test fixtures and mocking
- Parametrized tests

### Tools
- **pytest**: Test framework
- **pytest-cov**: Coverage plugin
- **pytest-asyncio**: Async test support
- **pytest-xdist**: Parallel testing
- **pytest-watch**: Watch mode
- **hypothesis**: Property-based testing

---

## 🎯 Next Steps

1. **Run existing tests**
   ```bash
   pytest tests/test_helpers.py -v
   ```

2. **Add more tests**
   - Create `tests/test_services.py`
   - Create `tests/test_api.py`
   - Create `tests/conftest.py` with fixtures

3. **Set up CI/CD**
   - Add GitHub Actions workflow
   - Add pre-commit hooks
   - Set up coverage tracking

4. **Improve coverage**
   - Target 80%+ overall coverage
   - Focus on critical paths
   - Add integration tests

---

**Happy Testing! 🧪**