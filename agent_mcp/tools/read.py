"""Read tools: read_entire_file, read_file_lines, read_file_tail, read_files.

Provides file reading capabilities with encoding detection and partial reading support.
"""
import chardet
from pathlib import Path
from typing import Optional
from agent_mcp.config import config
from agent_mcp.validators.path_validator import PathValidator
from agent_mcp.utils.file_detector import assert_text_file
from agent_mcp.utils.logger import logger


# Initialize path validator
if config:
    validator = PathValidator(config.root_path)
else:
    validator = None


def detect_encoding(file_path: Path) -> str:
    """Detect file encoding using chardet.

    Args:
        file_path: Path to file

    Returns:
        Detected encoding string (e.g., 'utf-8', 'ascii')
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB for detection
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    except Exception:
        return 'utf-8'  # Default fallback


def read_entire_file(file_path: str) -> dict:
    """Read complete file content.

    Args:
        file_path: File path relative to project root

    Returns:
        dict with keys: content, encoding, line_count, file_path
    """
    if not validator:
        raise RuntimeError("Configuration not loaded")

    logger.info(f"read_entire_file: {file_path}")

    # Validate path
    abs_path = validator.validate(file_path)

    if not abs_path.exists():
        raise FileNotFoundError(f"FILE_NOT_FOUND: {file_path}")

    if not abs_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Check if binary
    assert_text_file(abs_path)

    # Detect encoding
    encoding = detect_encoding(abs_path)

    # Read file
    try:
        with open(abs_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
            line_count = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
    except PermissionError:
        raise PermissionError(f"PERMISSION_DENIED: Cannot read {file_path}")

    return {
        "content": content,
        "encoding": encoding,
        "line_count": line_count,
        "file_path": file_path
    }


def read_file_lines(
    file_path: str,
    start_line: int,
    end_line: int
) -> dict:
    """Read specific line range from file.

    Args:
        file_path: File path relative to project root
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (inclusive)

    Returns:
        dict with keys: content, encoding, line_count, file_path, is_partial, total_lines
    """
    if not validator:
        raise RuntimeError("Configuration not loaded")

    logger.info(f"read_file_lines: {file_path}, lines {start_line}-{end_line}")

    # Validate line numbers
    if start_line < 1 or end_line < 1:
        raise ValueError("Line numbers must be >= 1")
    if start_line > end_line:
        raise ValueError(f"INVALID_LINE_RANGE: start_line ({start_line}) > end_line ({end_line})")

    # Validate path
    abs_path = validator.validate(file_path)

    if not abs_path.exists():
        raise FileNotFoundError(f"FILE_NOT_FOUND: {file_path}")

    # Check if binary
    assert_text_file(abs_path)

    # Detect encoding
    encoding = detect_encoding(abs_path)

    # Read lines
    try:
        with open(abs_path, 'r', encoding=encoding, errors='replace') as f:
            all_lines = f.readlines()
            total_lines = len(all_lines)

            # Check if range is valid
            if start_line > total_lines:
                raise ValueError(f"INVALID_LINE_RANGE: File has only {total_lines} lines")

            # Extract requested lines
            # Convert to 0-indexed
            actual_end = min(end_line, total_lines)
            selected_lines = all_lines[start_line-1:actual_end]

            content = ''.join(selected_lines)
            line_count = len(selected_lines)
            is_partial = True

    except PermissionError:
        raise PermissionError(f"PERMISSION_DENIED: Cannot read {file_path}")

    return {
        "content": content,
        "encoding": encoding,
        "line_count": line_count,
        "file_path": file_path,
        "is_partial": is_partial,
        "total_lines": total_lines
    }


def read_file_tail(
    file_path: str,
    num_lines: int = 10
) -> dict:
    """Read last N lines of file.

    Args:
        file_path: File path relative to project root
        num_lines: Number of lines to read from end

    Returns:
        dict with keys: content, encoding, line_count, file_path, is_partial, total_lines
    """
    if not validator:
        raise RuntimeError("Configuration not loaded")

    logger.info(f"read_file_tail: {file_path}, num_lines={num_lines}")

    # Validate path
    abs_path = validator.validate(file_path)

    if not abs_path.exists():
        raise FileNotFoundError(f"FILE_NOT_FOUND: {file_path}")

    # Check if binary
    assert_text_file(abs_path)

    # Detect encoding
    encoding = detect_encoding(abs_path)

    # Read file tail
    try:
        with open(abs_path, 'r', encoding=encoding, errors='replace') as f:
            all_lines = f.readlines()
            total_lines = len(all_lines)

            # Get last N lines
            tail_lines = all_lines[-num_lines:] if total_lines > num_lines else all_lines
            content = ''.join(tail_lines)
            line_count = len(tail_lines)
            is_partial = total_lines > num_lines

    except PermissionError:
        raise PermissionError(f"PERMISSION_DENIED: Cannot read {file_path}")

    return {
        "content": content,
        "encoding": encoding,
        "line_count": line_count,
        "file_path": file_path,
        "is_partial": is_partial,
        "total_lines": total_lines
    }


def read_files(file_paths: list[str]) -> dict:
    """Batch read multiple files.

    Args:
        file_paths: List of file paths relative to project root

    Returns:
        dict with keys: files (list), success_count (int), error_count (int)
    """
    if not validator:
        raise RuntimeError("Configuration not loaded")

    logger.info(f"read_files: {len(file_paths)} files")

    results = []
    success_count = 0
    error_count = 0

    for file_path in file_paths:
        try:
            # Try to read the file
            file_result = read_entire_file(file_path)
            results.append(file_result)
            success_count += 1
        except Exception as e:
            # Record error
            error_code = "UNKNOWN_ERROR"
            if "FILE_NOT_FOUND" in str(e):
                error_code = "FILE_NOT_FOUND"
            elif "BINARY_FILE_ERROR" in str(e):
                error_code = "BINARY_FILE_ERROR"
            elif "PATH_SECURITY_ERROR" in str(e):
                error_code = "PATH_SECURITY_ERROR"
            elif "PERMISSION_DENIED" in str(e):
                error_code = "PERMISSION_DENIED"

            results.append({
                "file_path": file_path,
                "error": {
                    "code": error_code,
                    "message": str(e)
                }
            })
            error_count += 1

    return {
        "files": results,
        "success_count": success_count,
        "error_count": error_count
    }
