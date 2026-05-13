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
