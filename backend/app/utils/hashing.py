"""
Hashing utilities for content and span identification.
Provides deterministic hashing for deduplication and caching.
"""

import hashlib
from typing import List, Optional


def content_hash(content: str) -> str:
    """
    Generate a deterministic hash for file content.
    
    Args:
        content: File content to hash
        
    Returns:
        SHA-256 hash as hex string
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def span_hash(file_path: str, start_line: int, end_line: int, code_snippet: str) -> str:
    """
    Generate a deterministic hash for a code span.
    
    Args:
        file_path: Path to the file
        start_line: Starting line number
        end_line: Ending line number
        code_snippet: Code content in the span
        
    Returns:
        SHA-256 hash as hex string
    """
    span_data = f"{file_path}:{start_line}:{end_line}:{code_snippet}"
    return hashlib.sha256(span_data.encode('utf-8')).hexdigest()


def rule_hash(rule_id: str, title: str, span_hash: str) -> str:
    """
    Generate a hash for a rule-issue combination.
    
    Args:
        rule_id: WCAG rule ID
        title: Issue title
        span_hash: Hash of the code span
        
    Returns:
        SHA-256 hash as hex string
    """
    rule_data = f"{rule_id}:{title}:{span_hash}"
    return hashlib.sha256(rule_data.encode('utf-8')).hexdigest()


def session_hash(session_id: str, model_map: dict) -> str:
    """
    Generate a hash for a session configuration.
    
    Args:
        session_id: Session identifier
        model_map: Model configuration
        
    Returns:
        SHA-256 hash as hex string
    """
    import json
    config_data = f"{session_id}:{json.dumps(model_map, sort_keys=True)}"
    return hashlib.sha256(config_data.encode('utf-8')).hexdigest()


def short_hash(content: str, length: int = 8) -> str:
    """
    Generate a short hash for display purposes.
    
    Args:
        content: Content to hash
        length: Length of the short hash
        
    Returns:
        Short hash string
    """
    full_hash = content_hash(content)
    return full_hash[:length]


def file_span_hash(file_path: str, line_range: tuple) -> str:
    """
    Generate a hash for a file and line range.
    
    Args:
        file_path: Path to the file
        line_range: Tuple of (start_line, end_line)
        
    Returns:
        SHA-256 hash as hex string
    """
    span_data = f"{file_path}:{line_range[0]}:{line_range[1]}"
    return hashlib.sha256(span_data.encode('utf-8')).hexdigest()


def deduplicate_by_hash(items: List[dict], hash_key: str = 'hash') -> List[dict]:
    """
    Remove duplicate items based on their hash.
    
    Args:
        items: List of items with hash keys
        hash_key: Key to use for hashing
        
    Returns:
        Deduplicated list
    """
    seen_hashes = set()
    unique_items = []
    
    for item in items:
        item_hash = item.get(hash_key)
        if item_hash and item_hash not in seen_hashes:
            seen_hashes.add(item_hash)
            unique_items.append(item)
    
    return unique_items


def generate_cache_key(prefix: str, *args) -> str:
    """
    Generate a cache key from a prefix and arguments.
    
    Args:
        prefix: Key prefix
        *args: Arguments to include in the key
        
    Returns:
        Cache key string
    """
    key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
    return hashlib.md5(key_data.encode('utf-8')).hexdigest()
