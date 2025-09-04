"""
Unified diff utilities for validating and applying patches.
Provides simulation capabilities without writing to disk.
"""

import re
from typing import List, Optional, Tuple


class DiffError(Exception):
    """Exception raised when diff operations fail."""
    pass


def parse_unified_diff(diff_content: str) -> List[dict]:
    """
    Parse a unified diff into structured format.
    
    Args:
        diff_content: Raw unified diff content
        
    Returns:
        List of diff hunks with metadata
    """
    hunks = []
    lines = diff_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Parse file headers
        if line.startswith('---'):
            old_file = line[4:].strip()
            i += 1
            if i < len(lines) and lines[i].startswith('+++'):
                new_file = lines[i][4:].strip()
                i += 1
            else:
                new_file = old_file
        elif line.startswith('@@'):
            # Parse hunk header
            hunk_match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
            if hunk_match:
                old_start = int(hunk_match.group(1))
                old_count = int(hunk_match.group(2) or 1)
                new_start = int(hunk_match.group(3))
                new_count = int(hunk_match.group(4) or 1)
                
                hunk = {
                    'old_start': old_start,
                    'old_count': old_count,
                    'new_start': new_start,
                    'new_count': new_count,
                    'lines': []
                }
                
                i += 1
                # Parse hunk lines
                while i < len(lines) and not lines[i].startswith('@@') and not lines[i].startswith('---'):
                    hunk['lines'].append(lines[i])
                    i += 1
                
                hunks.append(hunk)
                continue
        i += 1
    
    return hunks


def validate_diff(diff_content: str, original_content: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a unified diff can be applied to the original content.
    
    Args:
        diff_content: Unified diff to validate
        original_content: Original file content
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        hunks = parse_unified_diff(diff_content)
        original_lines = original_content.split('\n')
        
        for hunk in hunks:
            old_start = hunk['old_start'] - 1  # Convert to 0-based index
            old_count = hunk['old_count']
            
            # Check if the hunk fits within the original content
            if old_start < 0 or old_start + old_count > len(original_lines):
                return False, f"Hunk references lines outside file bounds"
            
            # Validate context lines match
            context_lines = []
            for line in hunk['lines']:
                if line.startswith(' '):
                    context_lines.append(line[1:])
                elif line.startswith('-'):
                    context_lines.append(line[1:])
                elif line.startswith('+'):
                    continue  # New lines don't need validation
            
            # Check if context matches
            for i, context_line in enumerate(context_lines):
                if old_start + i >= len(original_lines):
                    return False, f"Context line {i+1} exceeds file bounds"
                if original_lines[old_start + i] != context_line:
                    return False, f"Context mismatch at line {old_start + i + 1}"
        
        return True, None
        
    except Exception as e:
        return False, f"Parse error: {str(e)}"


def simulate_apply_diff(diff_content: str, original_content: str) -> Tuple[bool, Optional[str], str]:
    """
    Simulate applying a unified diff to original content.
    
    Args:
        diff_content: Unified diff to apply
        original_content: Original file content
        
    Returns:
        Tuple of (success, error_message, patched_content)
    """
    try:
        hunks = parse_unified_diff(diff_content)
        original_lines = original_content.split('\n')
        patched_lines = original_lines.copy()
        
        # Apply hunks in reverse order to maintain line numbers
        for hunk in reversed(hunks):
            old_start = hunk['old_start'] - 1  # Convert to 0-based index
            old_count = hunk['old_count']
            new_start = hunk['new_start'] - 1
            
            # Remove old lines
            del patched_lines[old_start:old_start + old_count]
            
            # Insert new lines
            new_lines = []
            for line in hunk['lines']:
                if line.startswith('+'):
                    new_lines.append(line[1:])
                elif line.startswith(' '):
                    new_lines.append(line[1:])
                # Skip lines starting with '-' (deletions)
            
            patched_lines[old_start:old_start] = new_lines
        
        return True, None, '\n'.join(patched_lines)
        
    except Exception as e:
        return False, f"Apply error: {str(e)}", original_content


def create_unified_diff(old_content: str, new_content: str, 
                       old_file: str = "original", new_file: str = "modified") -> str:
    """
    Create a unified diff between old and new content.
    
    Args:
        old_content: Original content
        new_content: Modified content
        old_file: Name of original file
        new_file: Name of modified file
        
    Returns:
        Unified diff string
    """
    old_lines = old_content.split('\n')
    new_lines = new_content.split('\n')
    
    # Simple diff implementation (could be enhanced with proper diff algorithm)
    diff_lines = [f"--- {old_file}", f"+++ {new_file}"]
    
    # Find differences (simplified)
    max_len = max(len(old_lines), len(new_lines))
    
    for i in range(max_len):
        old_line = old_lines[i] if i < len(old_lines) else ""
        new_line = new_lines[i] if i < len(new_lines) else ""
        
        if old_line != new_line:
            if old_line and new_line:
                diff_lines.append(f"@@ -{i+1},1 +{i+1},1 @@")
                diff_lines.append(f"-{old_line}")
                diff_lines.append(f"+{new_line}")
            elif old_line:
                diff_lines.append(f"@@ -{i+1},1 +{i+1},0 @@")
                diff_lines.append(f"-{old_line}")
            else:
                diff_lines.append(f"@@ -{i},0 +{i+1},1 @@")
                diff_lines.append(f"+{new_line}")
    
    return '\n'.join(diff_lines)


def extract_changed_lines(diff_content: str) -> List[Tuple[int, str, str]]:
    """
    Extract changed lines from a unified diff.
    
    Args:
        diff_content: Unified diff content
        
    Returns:
        List of (line_number, old_line, new_line) tuples
    """
    changes = []
    hunks = parse_unified_diff(diff_content)
    
    for hunk in hunks:
        line_num = hunk['new_start']
        
        for line in hunk['lines']:
            if line.startswith('-'):
                old_line = line[1:]
                # Find corresponding + line
                for next_line in hunk['lines'][hunk['lines'].index(line)+1:]:
                    if next_line.startswith('+'):
                        new_line = next_line[1:]
                        changes.append((line_num, old_line, new_line))
                        break
            elif line.startswith('+') and not any(l.startswith('-') for l in hunk['lines'][:hunk['lines'].index(line)]):
                # Addition without deletion
                changes.append((line_num, "", line[1:]))
            
            if not line.startswith('-'):
                line_num += 1
    
    return changes
