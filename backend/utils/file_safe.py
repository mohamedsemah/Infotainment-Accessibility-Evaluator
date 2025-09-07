"""
File safety utilities for secure file handling and validation.
"""

import os
import zipfile
import tempfile
import shutil
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

@dataclass
class FileInfo:
    """Information about a file."""
    path: str
    size: int
    mime_type: str
    extension: str
    is_safe: bool
    reason: Optional[str] = None

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    # Web files
    '.html', '.htm', '.xhtml',
    '.css', '.scss', '.sass', '.less',
    '.js', '.jsx', '.ts', '.tsx',
    '.json', '.xml', '.svg',
    
    # QML files
    '.qml',
    
    # Image files
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg',
    
    # Font files
    '.woff', '.woff2', '.ttf', '.otf', '.eot',
    
    # Archive files
    '.zip', '.tar', '.gz', '.bz2',
    
    # Document files
    '.pdf', '.txt', '.md',
    
    # Other web assets
    '.ico', '.manifest', '.webmanifest'
}

# Dangerous file extensions
DANGEROUS_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    '.php', '.asp', '.aspx', '.jsp', '.py', '.rb', '.pl', '.sh', '.ps1',
    '.dll', '.so', '.dylib', '.bin', '.app', '.deb', '.rpm', '.msi'
}

# Maximum file sizes (in bytes)
MAX_FILE_SIZES = {
    '.zip': 50 * 1024 * 1024,  # 50MB
    '.html': 10 * 1024 * 1024,  # 10MB
    '.css': 5 * 1024 * 1024,   # 5MB
    '.js': 5 * 1024 * 1024,    # 5MB
    '.png': 10 * 1024 * 1024,  # 10MB
    '.jpg': 10 * 1024 * 1024,  # 10MB
    '.jpeg': 10 * 1024 * 1024, # 10MB
    '.gif': 10 * 1024 * 1024,  # 10MB
    '.svg': 2 * 1024 * 1024,   # 2MB
    'default': 1 * 1024 * 1024  # 1MB default
}

# MIME types that are safe for web content
SAFE_MIME_TYPES = {
    'text/html', 'text/css', 'text/javascript', 'application/javascript',
    'text/xml', 'application/xml', 'image/svg+xml', 'application/json',
    'text/plain', 'text/markdown',
    'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/svg+xml',
    'font/woff', 'font/woff2', 'font/ttf', 'font/otf',
    'application/zip', 'application/x-tar', 'application/gzip',
    'application/pdf', 'image/x-icon', 'application/manifest+json'
}

class FileSafetyChecker:
    """Checks files for safety and validity."""
    
    def __init__(self):
        self.allowed_extensions = ALLOWED_EXTENSIONS
        self.dangerous_extensions = DANGEROUS_EXTENSIONS
        self.max_file_sizes = MAX_FILE_SIZES
        self.safe_mime_types = SAFE_MIME_TYPES
    
    def check_file(self, file_path: str) -> FileInfo:
        """Check if a file is safe to process."""
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return FileInfo(
                path=file_path,
                size=0,
                mime_type='',
                extension='',
                is_safe=False,
                reason="File does not exist"
            )
        
        # Get file size
        size = path.stat().st_size
        
        # Get file extension
        extension = path.suffix.lower()
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'
        
        # Check if extension is allowed
        if extension not in self.allowed_extensions:
            return FileInfo(
                path=file_path,
                size=size,
                mime_type=mime_type,
                extension=extension,
                is_safe=False,
                reason=f"File extension '{extension}' is not allowed"
            )
        
        # Check if extension is dangerous
        if extension in self.dangerous_extensions:
            return FileInfo(
                path=file_path,
                size=size,
                mime_type=mime_type,
                extension=extension,
                is_safe=False,
                reason=f"File extension '{extension}' is potentially dangerous"
            )
        
        # Check file size
        max_size = self.max_file_sizes.get(extension, self.max_file_sizes['default'])
        if size > max_size:
            return FileInfo(
                path=file_path,
                size=size,
                mime_type=mime_type,
                extension=extension,
                is_safe=False,
                reason=f"File size {size} exceeds maximum allowed size {max_size}"
            )
        
        # Check MIME type
        if mime_type not in self.safe_mime_types:
            return FileInfo(
                path=file_path,
                size=size,
                mime_type=mime_type,
                extension=extension,
                is_safe=False,
                reason=f"MIME type '{mime_type}' is not allowed"
            )
        
        return FileInfo(
            path=file_path,
            size=size,
            mime_type=mime_type,
            extension=extension,
            is_safe=True
        )
    
    def check_zip_file(self, zip_path: str) -> Dict[str, Any]:
        """Check a ZIP file for safety."""
        result = {
            "safe": True,
            "files": [],
            "total_files": 0,
            "total_size": 0,
            "errors": [],
            "warnings": []
        }
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                # Check for zip bombs (too many files or too large)
                file_count = len(zip_file.namelist())
                if file_count > 10000:  # Reasonable limit
                    result["errors"].append(f"Too many files in ZIP: {file_count}")
                    result["safe"] = False
                
                # Check each file in the ZIP
                for file_info in zip_file.infolist():
                    file_name = file_info.filename
                    file_size = file_info.file_size
                    
                    # Check for path traversal attacks
                    if '..' in file_name or file_name.startswith('/'):
                        result["errors"].append(f"Path traversal detected: {file_name}")
                        result["safe"] = False
                        continue
                    
                    # Check file size
                    if file_size > MAX_FILE_SIZES.get('default', 1024 * 1024):
                        result["warnings"].append(f"Large file in ZIP: {file_name} ({file_size} bytes)")
                    
                    # Check if it's a directory
                    if file_name.endswith('/'):
                        # Skip directories - they're safe
                        continue
                    
                    # Check file extension
                    file_path = Path(file_name)
                    extension = file_path.suffix.lower()
                    
                    if extension not in self.allowed_extensions:
                        result["errors"].append(f"Unsafe file in ZIP: {file_name}")
                        result["safe"] = False
                        continue
                    
                    # Add to safe files
                    result["files"].append({
                        "name": file_name,
                        "size": file_size,
                        "extension": extension,
                        "safe": True
                    })
                    
                    result["total_size"] += file_size
                
                result["total_files"] = len(result["files"])
                
        except zipfile.BadZipFile:
            result["errors"].append("Invalid ZIP file")
            result["safe"] = False
        except Exception as e:
            result["errors"].append(f"Error reading ZIP file: {str(e)}")
            result["safe"] = False
        
        return result

def safe_extract_zip(zip_path: str, extract_to: str) -> Dict[str, Any]:
    """Safely extract a ZIP file to a directory."""
    result = {
        "success": False,
        "extracted_files": [],
        "errors": [],
        "warnings": []
    }
    
    # Create extraction directory
    os.makedirs(extract_to, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            for file_info in zip_file.infolist():
                file_name = file_info.filename
                
                # Skip directories
                if file_name.endswith('/'):
                    continue
                
                # Check for path traversal
                if '..' in file_name or file_name.startswith('/'):
                    result["errors"].append(f"Path traversal detected: {file_name}")
                    continue
                
                # Extract file
                try:
                    zip_file.extract(file_info, extract_to)
                    result["extracted_files"].append(file_name)
                except Exception as e:
                    result["errors"].append(f"Error extracting {file_name}: {str(e)}")
        
        result["success"] = len(result["errors"]) == 0
        
    except zipfile.BadZipFile:
        result["errors"].append("Invalid ZIP file")
    except Exception as e:
        result["errors"].append(f"Error extracting ZIP: {str(e)}")
    
    return result

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to make it safe."""
    # Remove path separators and dangerous characters
    dangerous_chars = '<>:"/\\|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading dots and spaces
    filename = filename.lstrip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def get_file_manifest(directory: str) -> List[Dict[str, Any]]:
    """Get a manifest of all files in a directory."""
    manifest = []
    checker = FileSafetyChecker()
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            
            file_info = checker.check_file(file_path)
            
            manifest.append({
                "path": relative_path,
                "absolute_path": file_path,
                "size": file_info.size,
                "extension": file_info.extension,
                "mime_type": file_info.mime_type,
                "safe": file_info.is_safe,
                "reason": file_info.reason
            })
    
    return manifest

def validate_upload(upload_path: str) -> Dict[str, Any]:
    """Validate an uploaded file or directory."""
    result = {
        "valid": False,
        "type": "unknown",
        "files": [],
        "total_size": 0,
        "errors": [],
        "warnings": []
    }
    
    if not os.path.exists(upload_path):
        result["errors"].append("Upload path does not exist")
        return result
    
    if os.path.isfile(upload_path):
        # Single file upload
        path = Path(upload_path)
        extension = path.suffix.lower()
        
        if extension == '.zip':
            result["type"] = "zip"
            zip_result = FileSafetyChecker().check_zip_file(upload_path)
            result["valid"] = zip_result["safe"]
            result["files"] = zip_result["files"]
            result["total_size"] = zip_result["total_size"]
            result["errors"].extend(zip_result["errors"])
            result["warnings"].extend(zip_result["warnings"])
        else:
            # Single file
            result["type"] = "file"
            file_info = FileSafetyChecker().check_file(upload_path)
            result["valid"] = file_info.is_safe
            result["files"] = [{
                "path": path.name,
                "size": file_info.size,
                "extension": file_info.extension,
                "mime_type": file_info.mime_type,
                "safe": file_info.is_safe,
                "reason": file_info.reason
            }]
            result["total_size"] = file_info.size
            if not file_info.is_safe:
                result["errors"].append(file_info.reason)
    
    elif os.path.isdir(upload_path):
        # Directory upload
        result["type"] = "directory"
        manifest = get_file_manifest(upload_path)
        result["files"] = manifest
        result["total_size"] = sum(f["size"] for f in manifest)
        result["valid"] = all(f["safe"] for f in manifest)
        
        # Collect errors and warnings
        for file_info in manifest:
            if not file_info["safe"]:
                result["errors"].append(f"{file_info['path']}: {file_info['reason']}")
    
    return result
