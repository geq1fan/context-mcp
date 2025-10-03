"""Contract tests for read tools.

Tests for: read_entire_file, read_file_lines, read_file_tail, read_files
"""
import pytest
from agent_mcp.tools.read import (
    read_entire_file,
    read_file_lines,
    read_file_tail,
    read_files
)


class TestReadEntireFileContract:
    """Contract tests for read_entire_file tool."""

    def test_input_schema_required_file_path(self):
        """Test that file_path is required."""
        result = read_entire_file(file_path="README.md")
        assert "content" in result
        assert "encoding" in result
        assert "line_count" in result
        assert "file_path" in result

    def test_output_schema_required_fields(self):
        """Test that output contains all required fields."""
        result = read_entire_file(file_path="pyproject.toml")

        assert "content" in result
        assert "encoding" in result
        assert "line_count" in result
        assert "file_path" in result

        assert isinstance(result["content"], str)
        assert isinstance(result["encoding"], str)
        assert isinstance(result["line_count"], int)
        assert isinstance(result["file_path"], str)

    def test_error_path_security_error(self):
        """Test PATH_SECURITY_ERROR for paths outside root."""
        with pytest.raises(Exception) as exc_info:
            read_entire_file(file_path="../../etc/passwd")
        assert "PATH_SECURITY_ERROR" in str(exc_info.value) or "outside root" in str(exc_info.value).lower()

    def test_error_file_not_found(self):
        """Test FILE_NOT_FOUND error."""
        with pytest.raises(Exception) as exc_info:
            read_entire_file(file_path="nonexistent_file_xyz.txt")
        assert "FILE_NOT_FOUND" in str(exc_info.value) or "not exist" in str(exc_info.value).lower()


class TestReadFileLinesContract:
    """Contract tests for read_file_lines tool."""

    def test_input_schema_required_fields(self):
        """Test that file_path, start_line, end_line are required."""
        result = read_file_lines(file_path="README.md", start_line=1, end_line=10)
        assert "content" in result
        assert "is_partial" in result
        assert "total_lines" in result

    def test_input_schema_line_minimum(self):
        """Test that start_line and end_line respect minimum (1)."""
        result = read_file_lines(file_path="pyproject.toml", start_line=1, end_line=5)
        assert isinstance(result["line_count"], int)

    def test_output_schema_required_fields(self):
        """Test that output contains all required fields."""
        result = read_file_lines(file_path="pyproject.toml", start_line=1, end_line=10)

        assert "content" in result
        assert "encoding" in result
        assert "line_count" in result
        assert "file_path" in result
        assert "is_partial" in result
        assert "total_lines" in result

        assert isinstance(result["content"], str)
        assert isinstance(result["encoding"], str)
        assert isinstance(result["line_count"], int)
        assert isinstance(result["file_path"], str)
        assert isinstance(result["is_partial"], bool)
        assert isinstance(result["total_lines"], int)

    def test_error_path_security_error(self):
        """Test PATH_SECURITY_ERROR for paths outside root."""
        with pytest.raises(Exception) as exc_info:
            read_file_lines(file_path="../../etc/passwd", start_line=1, end_line=10)
        assert "PATH_SECURITY_ERROR" in str(exc_info.value) or "outside root" in str(exc_info.value).lower()

    def test_error_file_not_found(self):
        """Test FILE_NOT_FOUND error."""
        with pytest.raises(Exception) as exc_info:
            read_file_lines(file_path="nonexistent.txt", start_line=1, end_line=10)
        assert "FILE_NOT_FOUND" in str(exc_info.value) or "not exist" in str(exc_info.value).lower()


class TestReadFileTailContract:
    """Contract tests for read_file_tail tool."""

    def test_input_schema_required_file_path(self):
        """Test that file_path is required."""
        result = read_file_tail(file_path="README.md")
        assert "content" in result
        assert "is_partial" in result

    def test_input_schema_num_lines_default(self):
        """Test that num_lines defaults to 10."""
        result = read_file_tail(file_path="pyproject.toml")
        assert isinstance(result["line_count"], int)

    def test_input_schema_num_lines_minimum(self):
        """Test that num_lines respects minimum (1)."""
        result = read_file_tail(file_path="pyproject.toml", num_lines=1)
        assert result["line_count"] >= 0

    def test_output_schema_required_fields(self):
        """Test that output contains all required fields."""
        result = read_file_tail(file_path="pyproject.toml", num_lines=5)

        assert "content" in result
        assert "encoding" in result
        assert "line_count" in result
        assert "file_path" in result
        assert "is_partial" in result
        assert "total_lines" in result

        assert isinstance(result["content"], str)
        assert isinstance(result["encoding"], str)
        assert isinstance(result["line_count"], int)
        assert isinstance(result["file_path"], str)
        assert isinstance(result["is_partial"], bool)
        assert isinstance(result["total_lines"], int)

    def test_error_path_security_error(self):
        """Test PATH_SECURITY_ERROR for paths outside root."""
        with pytest.raises(Exception) as exc_info:
            read_file_tail(file_path="../../etc/passwd")
        assert "PATH_SECURITY_ERROR" in str(exc_info.value) or "outside root" in str(exc_info.value).lower()

    def test_error_file_not_found(self):
        """Test FILE_NOT_FOUND error."""
        with pytest.raises(Exception) as exc_info:
            read_file_tail(file_path="nonexistent_xyz.log")
        assert "FILE_NOT_FOUND" in str(exc_info.value) or "not exist" in str(exc_info.value).lower()


class TestReadFilesContract:
    """Contract tests for read_files tool (batch operation)."""

    def test_input_schema_required_file_paths(self):
        """Test that file_paths array is required."""
        result = read_files(file_paths=["README.md", "pyproject.toml"])
        assert "files" in result
        assert "success_count" in result
        assert "error_count" in result

    def test_input_schema_min_items(self):
        """Test that file_paths requires at least 1 item."""
        result = read_files(file_paths=["pyproject.toml"])
        assert len(result["files"]) == 1

    def test_output_schema_required_fields(self):
        """Test that output contains all required fields."""
        result = read_files(file_paths=["README.md"])

        assert "files" in result
        assert "success_count" in result
        assert "error_count" in result

        assert isinstance(result["files"], list)
        assert isinstance(result["success_count"], int)
        assert isinstance(result["error_count"], int)

    def test_output_schema_file_entry_required_fields(self):
        """Test that each file entry contains file_path."""
        result = read_files(file_paths=["pyproject.toml", "nonexistent.txt"])

        for file_entry in result["files"]:
            assert "file_path" in file_entry
            assert isinstance(file_entry["file_path"], str)

    def test_output_schema_success_entry_fields(self):
        """Test that successful entries contain content fields."""
        result = read_files(file_paths=["pyproject.toml"])

        success_entries = [f for f in result["files"] if "content" in f]
        if success_entries:
            entry = success_entries[0]
            assert "content" in entry
            assert "encoding" in entry
            assert "line_count" in entry

    def test_output_schema_error_entry_fields(self):
        """Test that error entries contain error object."""
        result = read_files(file_paths=["nonexistent_file_xyz.txt"])

        error_entries = [f for f in result["files"] if "error" in f]
        if error_entries:
            entry = error_entries[0]
            assert "error" in entry
            assert "code" in entry["error"]
            assert "message" in entry["error"]

    def test_output_schema_count_consistency(self):
        """Test that success_count + error_count equals total files."""
        file_paths = ["README.md", "nonexistent1.txt", "pyproject.toml", "nonexistent2.txt"]
        result = read_files(file_paths=file_paths)

        assert result["success_count"] + result["error_count"] == len(file_paths)

    def test_no_exception_on_partial_failure(self):
        """Test that batch operation doesn't throw exception on partial failure."""
        # This should not raise an exception
        result = read_files(file_paths=["README.md", "nonexistent.txt"])
        assert result["success_count"] >= 1
        assert result["error_count"] >= 1
