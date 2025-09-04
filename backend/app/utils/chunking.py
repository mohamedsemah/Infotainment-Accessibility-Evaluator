"""
Token-aware chunking utilities for processing large files.
Implements line-based chunking with overlap for better context preservation.
"""

import re
from typing import List, Tuple


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count for text.
    Uses a simple heuristic: ~4 characters per token.
    
    Args:
        text: Text to estimate tokens for
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def chunk_file(content: str, max_tokens: int = 3000, overlap_lines: int = 20) -> List[Tuple[int, int, str]]:
    """
    Chunk a file into smaller pieces with overlap.
    
    Args:
        content: File content to chunk
        max_tokens: Maximum tokens per chunk
        overlap_lines: Number of lines to overlap between chunks
        
    Returns:
        List of (start_line, end_line, chunk_content) tuples
    """
    lines = content.split('\n')
    chunks = []
    
    if not lines:
        return chunks
    
    start_line = 1
    current_chunk_lines = []
    current_tokens = 0
    
    for i, line in enumerate(lines):
        line_tokens = estimate_tokens(line)
        
        # If adding this line would exceed token limit, create a chunk
        if current_tokens + line_tokens > max_tokens and current_chunk_lines:
            end_line = start_line + len(current_chunk_lines) - 1
            chunk_content = '\n'.join(current_chunk_lines)
            chunks.append((start_line, end_line, chunk_content))
            
            # Start new chunk with overlap
            overlap_start = max(0, len(current_chunk_lines) - overlap_lines)
            current_chunk_lines = current_chunk_lines[overlap_start:]
            current_tokens = estimate_tokens('\n'.join(current_chunk_lines))
            start_line = end_line - len(current_chunk_lines) + 1
        
        current_chunk_lines.append(line)
        current_tokens += line_tokens
    
    # Add final chunk if there's content
    if current_chunk_lines:
        end_line = start_line + len(current_chunk_lines) - 1
        chunk_content = '\n'.join(current_chunk_lines)
        chunks.append((start_line, end_line, chunk_content))
    
    return chunks


def chunk_by_lines(content: str, max_lines: int = 200, overlap_lines: int = 20) -> List[Tuple[int, int, str]]:
    """
    Simple line-based chunking without token estimation.
    
    Args:
        content: File content to chunk
        max_lines: Maximum lines per chunk
        overlap_lines: Number of lines to overlap between chunks
        
    Returns:
        List of (start_line, end_line, chunk_content) tuples
    """
    lines = content.split('\n')
    chunks = []
    
    if not lines:
        return chunks
    
    start_line = 1
    
    for i in range(0, len(lines), max_lines - overlap_lines):
        end_idx = min(i + max_lines, len(lines))
        chunk_lines = lines[i:end_idx]
        
        if chunk_lines:
            end_line = start_line + len(chunk_lines) - 1
            chunk_content = '\n'.join(chunk_lines)
            chunks.append((start_line, end_line, chunk_content))
            start_line = end_line - overlap_lines + 1
    
    return chunks


def get_file_span_from_chunk(chunk_start: int, chunk_end: int, 
                           target_start: int, target_end: int) -> Tuple[int, int]:
    """
    Get the actual file span for a target within a chunk.
    
    Args:
        chunk_start: Starting line of the chunk
        chunk_end: Ending line of the chunk
        target_start: Target start line within chunk
        target_end: Target end line within chunk
        
    Returns:
        Tuple of (actual_start, actual_end) in file coordinates
    """
    actual_start = chunk_start + target_start - 1
    actual_end = chunk_start + target_end - 1
    
    return actual_start, actual_end


def merge_overlapping_chunks(chunks: List[Tuple[int, int, str]]) -> List[Tuple[int, int, str]]:
    """
    Merge chunks that have significant overlap.
    
    Args:
        chunks: List of (start_line, end_line, chunk_content) tuples
        
    Returns:
        Merged chunks with reduced overlap
    """
    if not chunks:
        return chunks
    
    merged = [chunks[0]]
    
    for current_start, current_end, current_content in chunks[1:]:
        last_start, last_end, last_content = merged[-1]
        
        # If chunks overlap significantly, merge them
        overlap = min(current_end, last_end) - max(current_start, last_start) + 1
        if overlap > 10:  # Merge if more than 10 lines overlap
            # Merge content, avoiding duplication
            merged_content = last_content + '\n' + current_content
            merged[-1] = (last_start, current_end, merged_content)
        else:
            merged.append((current_start, current_end, current_content))
    
    return merged
