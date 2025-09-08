"""
File parsing service for extracting and analyzing uploaded files.
"""

import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import mimetypes
import magic

from models.schemas import UploadResult
from utils.file_safe import FileSafetyChecker

@dataclass
class FileInfo:
    """Information about a parsed file."""
    path: str
    relative_path: str
    size: int
    mime_type: str
    extension: str
    is_safe: bool
    content: Optional[str] = None
    encoding: str = 'utf-8'
    line_count: int = 0
    is_binary: bool = False

class FileParser:
    """Service for parsing and extracting uploaded files."""
    
    def __init__(self):
        self.safety_checker = FileSafetyChecker()
        self.supported_extensions = {
            '.html', '.htm', '.xhtml', '.xml', '.qml', '.css', '.scss', '.sass',
            '.js', '.jsx', '.ts', '.tsx', '.json', '.png', '.jpg', '.jpeg',
            '.gif', '.svg', '.webp', '.ico'
        }
        self.text_extensions = {
            '.html', '.htm', '.xhtml', '.xml', '.qml', '.css', '.scss', '.sass',
            '.js', '.jsx', '.ts', '.tsx', '.json'
        }
    
    async def parse_upload(self, file_path: str, upload_id: str) -> Tuple[str, List[FileInfo]]:
        """
        Parse uploaded file and extract all relevant files.
        Returns (extract_path, file_infos)
        """
        # Create temporary extraction directory
        extract_dir = tempfile.mkdtemp(prefix=f"extract_{upload_id}_")
        
        try:
            # Determine file type and extract
            if file_path.endswith('.zip'):
                await self._extract_zip(file_path, extract_dir)
            else:
                # Single file upload
                await self._copy_single_file(file_path, extract_dir)
            
            # Parse all files in extraction directory
            file_infos = await self._parse_directory(extract_dir)
            
            return extract_dir, file_infos
            
        except Exception as e:
            # Cleanup on error
            shutil.rmtree(extract_dir, ignore_errors=True)
            raise e
    
    async def _extract_zip(self, zip_path: str, extract_dir: str):
        """Safely extract ZIP file."""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Validate ZIP file
            if zip_ref.testzip():
                raise ValueError("ZIP file is corrupted")
            
            # Extract all files
            for member in zip_ref.infolist():
                # Security check: prevent path traversal
                if os.path.isabs(member.filename) or ".." in member.filename:
                    continue
                
                # Extract file
                zip_ref.extract(member, extract_dir)
    
    async def _copy_single_file(self, file_path: str, extract_dir: str):
        """Copy single file to extraction directory."""
        filename = os.path.basename(file_path)
        dest_path = os.path.join(extract_dir, filename)
        shutil.copy2(file_path, dest_path)
    
    async def _parse_directory(self, directory: str) -> List[FileInfo]:
        """Parse all files in directory and return file information."""
        file_infos = []
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, directory)
                
                # Check if file is supported
                file_ext = Path(filename).suffix.lower()
                if file_ext not in self.supported_extensions:
                    continue
                
                # Get file information
                file_info = await self._analyze_file(file_path, relative_path)
                if file_info:
                    file_infos.append(file_info)
        
        return file_infos
    
    async def _analyze_file(self, file_path: str, relative_path: str) -> Optional[FileInfo]:
        """Analyze a single file and return file information."""
        try:
            # Get file stats
            stat = os.stat(file_path)
            size = stat.st_size
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = magic.from_file(file_path, mime=True)
            
            # Get extension
            extension = Path(file_path).suffix.lower()
            
            # Safety check
            safety_result = self.safety_checker.check_file(file_path)
            if not safety_result.is_safe:
                return None
            
            # Determine if file is binary
            is_binary = extension not in self.text_extensions
            
            # Read content for text files
            content = None
            encoding = 'utf-8'
            line_count = 0
            
            if not is_binary:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        line_count = content.count('\n') + 1
                except UnicodeDecodeError:
                    # Try other encodings
                    for enc in ['latin-1', 'cp1252', 'iso-8859-1']:
                        try:
                            with open(file_path, 'r', encoding=enc) as f:
                                content = f.read()
                                encoding = enc
                                line_count = content.count('\n') + 1
                                break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is None:
                        # Mark as binary if we can't decode
                        is_binary = True
            
            return FileInfo(
                path=file_path,
                relative_path=relative_path,
                size=size,
                mime_type=mime_type or 'application/octet-stream',
                extension=extension,
                is_safe=safety_result.is_safe,
                content=content,
                encoding=encoding,
                line_count=line_count,
                is_binary=is_binary
            )
            
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            return None
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """Get content of a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try other encodings
            for enc in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
        except Exception:
            pass
        return None
    
    def get_file_lines(self, file_path: str, start_line: int = 1, end_line: int = None) -> List[str]:
        """Get specific lines from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                if end_line is None:
                    end_line = len(lines)
                
                # Convert to 0-based indexing
                start_idx = max(0, start_line - 1)
                end_idx = min(len(lines), end_line)
                
                return lines[start_idx:end_idx]
        except Exception:
            return []
    
    def cleanup_extraction(self, extract_dir: str):
        """Clean up extraction directory."""
        try:
            shutil.rmtree(extract_dir)
        except Exception:
            pass

