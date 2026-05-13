"""
Helper Utilities Module

Common utility functions used across the application
"""

import re
import hashlib
from typing import Optional, List
from datetime import datetime, timedelta
import numpy as np
from urllib.parse import urlparse, parse_qs


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "1h 23m 45s" or "5m 30s")
    
    Examples:
        >>> format_duration(3665)
        '1h 1m 5s'
        >>> format_duration(90)
        '1m 30s'
        >>> format_duration(45)
        '45s'
    """
    if seconds < 60:
        return f"{seconds}s"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def format_timestamp(seconds: float, include_hours: bool = False) -> str:
    """
    Format seconds to timestamp (MM:SS or HH:MM:SS)
    
    Args:
        seconds: Time in seconds
        include_hours: Force HH:MM:SS format even for short durations
    
    Returns:
        Formatted timestamp string
    
    Examples:
        >>> format_timestamp(125.5)
        '02:05'
        >>> format_timestamp(3665)
        '01:01:05'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0 or include_hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def calculate_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector
        vec2: Second vector
    
    Returns:
        Similarity score between -1 and 1
    
    Examples:
        >>> v1 = [1, 0, 0]
        >>> v2 = [1, 0, 0]
        >>> calculate_similarity(v1, v2)
        1.0
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    # Handle zero vectors
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = np.dot(v1, v2) / (norm1 * norm2)
    return float(similarity)


def validate_youtube_url(url: str) -> bool:
    """
    Validate if URL is a valid YouTube URL
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid YouTube URL, False otherwise
    
    Examples:
        >>> validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        True
        >>> validate_youtube_url("https://youtu.be/dQw4w9WgXcQ")
        True
        >>> validate_youtube_url("https://example.com")
        False
    """
    youtube_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
    ]
    
    return any(re.match(pattern, url) for pattern in youtube_patterns)


def extract_video_id_from_url(url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL
    
    Args:
        url: YouTube URL
    
    Returns:
        Video ID or None if not found
    
    Examples:
        >>> extract_video_id_from_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id_from_url("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    patterns = [
        r'(?:v=|\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
    
    Returns:
        Sanitized filename
    
    Examples:
        >>> sanitize_filename("My Video: Part 1 (2024)")
        'My_Video_Part_1_2024'
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces and special chars with underscore
    sanitized = re.sub(r'[\s\(\)\[\]]+', '_', sanitized)
    
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Trim underscores from ends
    sanitized = sanitized.strip('_')
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def estimate_tokens(text: str, chars_per_token: int = 4) -> int:
    """
    Estimate number of tokens in text
    
    Args:
        text: Input text
        chars_per_token: Average characters per token (rough estimate)
    
    Returns:
        Estimated token count
    
    Examples:
        >>> estimate_tokens("Hello, world!")
        3
    """
    return len(text) // chars_per_token


def chunk_list(items: List, chunk_size: int) -> List[List]:
    """
    Split a list into chunks of specified size
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    
    Examples:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def generate_hash(text: str, algorithm: str = 'md5') -> str:
    """
    Generate hash of text
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256)
    
    Returns:
        Hexadecimal hash string
    
    Examples:
        >>> generate_hash("hello")
        '5d41402abc4b2a76b9719d911017c592'
    """
    hash_func = getattr(hashlib, algorithm)()
    hash_func.update(text.encode('utf-8'))
    return hash_func.hexdigest()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
    
    Returns:
        Truncated text
    
    Examples:
        >>> truncate_text("This is a very long text", 10)
        'This is...'
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_time_string(time_str: str) -> int:
    """
    Parse time string (MM:SS or HH:MM:SS) to seconds
    
    Args:
        time_str: Time string
    
    Returns:
        Time in seconds
    
    Examples:
        >>> parse_time_string("02:30")
        150
        >>> parse_time_string("01:02:30")
        3750
    """
    parts = time_str.split(':')
    
    if len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    else:
        raise ValueError(f"Invalid time format: {time_str}")


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in MB
    """
    import os
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def time_ago(dt: datetime) -> str:
    """
    Convert datetime to "time ago" string
    
    Args:
        dt: Datetime object
    
    Returns:
        Human-readable time ago string
    
    Examples:
        >>> time_ago(datetime.now() - timedelta(minutes=5))
        '5 minutes ago'
    """
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"


def batch_items(items: List, batch_size: int):
    """
    Generator that yields batches of items
    
    Args:
        items: List of items
        batch_size: Size of each batch
    
    Yields:
        Batches of items
    
    Examples:
        >>> list(batch_items([1,2,3,4,5], 2))
        [[1, 2], [3, 4], [5]]
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def retry_with_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
    
    Returns:
        Function result
    """
    import time
    
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(delay)
                delay *= backoff_factor
            else:
                raise last_exception
    
    raise last_exception