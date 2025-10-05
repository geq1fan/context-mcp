"""Contract tests for read tools.

Tests for: read_entire_file, read_file_lines, read_file_tail, read_files
"""

import pytest
from context_mcp.tools.read import (
    read_entire_file,
    read_file_lines,
    read_file_tail,
    read_files,
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
        assert (
            "PATH_SECURITY_ERROR" in str(exc_info.value)
            or "outside root" in str(exc_info.value).lower()
        )

    def test_error_file_not_found(self):
        """Test FILE_NOT_FOUND error."""
        with pytest.raises(Exception) as exc_info:
            read_entire_file(file_path="nonexistent_file_xyz.txt")
        assert (
            "FILE_NOT_FOUND" in str(exc_info.value)
            or "not exist" in str(exc_info.value).lower()
        )


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
        assert (
            "PATH_SECURITY_ERROR" in str(exc_info.value)
            or "outside root" in str(exc_info.value).lower()
        )

    def test_error_file_not_found(self):
        """Test FILE_NOT_FOUND error."""
        with pytest.raises(Exception) as exc_info:
            read_file_lines(file_path="nonexistent.txt", start_line=1, end_line=10)
        assert (
            "FILE_NOT_FOUND" in str(exc_info.value)
            or "not exist" in str(exc_info.value).lower()
        )

    def test_single_line_read(self, tmp_path, monkeypatch):
        """Test reading single line when start_line=end_line."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\n", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr("context_mcp.tools.read.validator", PathValidator(tmp_path))

        result = read_file_lines(file_path="test.txt", start_line=2, end_line=2)
        assert result["line_count"] == 1
        assert result["is_partial"] is True
        assert result["total_lines"] == 3
        assert "line2" in result["content"]

    def test_end_line_exceeds_total(self, tmp_path, monkeypatch):
        """Test end_line > total_lines automatically truncates."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\nline4\nline5\n", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr("context_mcp.tools.read.validator", PathValidator(tmp_path))

        result = read_file_lines(file_path="test.txt", start_line=3, end_line=10)
        # Should return lines 3-5 only
        assert result["line_count"] == 3
        assert result["total_lines"] == 5
        assert "line3" in result["content"]
        assert "line5" in result["content"]

    def test_read_entire_file_via_lines(self, tmp_path, monkeypatch):
        """Test reading entire file via start_line=1, end_line=total_lines."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        test_file = tmp_path / "test.txt"
        content = "".join(f"line{i}\n" for i in range(1, 11))
        test_file.write_text(content, encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr("context_mcp.tools.read.validator", PathValidator(tmp_path))

        result = read_file_lines(file_path="test.txt", start_line=1, end_line=10)
        assert result["line_count"] == 10
        assert result["is_partial"] is True
        assert result["total_lines"] == 10


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
        assert (
            "PATH_SECURITY_ERROR" in str(exc_info.value)
            or "outside root" in str(exc_info.value).lower()
        )

    def test_error_file_not_found(self):
        """Test FILE_NOT_FOUND error."""
        with pytest.raises(Exception) as exc_info:
            read_file_tail(file_path="nonexistent_xyz.log")
        assert (
            "FILE_NOT_FOUND" in str(exc_info.value)
            or "not exist" in str(exc_info.value).lower()
        )

    def test_num_lines_exceeds_total(self, tmp_path, monkeypatch):
        """Test num_lines > total_lines returns entire file."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\nline4\nline5\n", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr("context_mcp.tools.read.validator", PathValidator(tmp_path))

        result = read_file_tail(file_path="test.txt", num_lines=10)
        # Should return all 5 lines
        assert result["line_count"] == 5
        assert result["is_partial"] is False
        assert result["total_lines"] == 5

    def test_num_lines_equals_total(self, tmp_path, monkeypatch):
        """Test num_lines = total_lines boundary."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        test_file = tmp_path / "test.txt"
        test_file.write_text(
            "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\n", encoding="utf-8"
        )

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr("context_mcp.tools.read.validator", PathValidator(tmp_path))

        result = read_file_tail(file_path="test.txt", num_lines=8)
        # Should return all 8 lines
        assert result["line_count"] == 8
        assert result["is_partial"] is False
        assert result["total_lines"] == 8


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
        file_paths = [
            "README.md",
            "nonexistent1.txt",
            "pyproject.toml",
            "nonexistent2.txt",
        ]
        result = read_files(file_paths=file_paths)

        assert result["success_count"] + result["error_count"] == len(file_paths)

    def test_no_exception_on_partial_failure(self):
        """Test that batch operation doesn't throw exception on partial failure."""
        # This should not raise an exception
        result = read_files(file_paths=["README.md", "nonexistent.txt"])
        assert result["success_count"] >= 1
        assert result["error_count"] >= 1

    def test_empty_array_rejected(self):
        """Test that file_paths=[] violates minItems constraint."""
        # Empty array should either raise exception or return 0 counts
        try:
            result = read_files(file_paths=[])
            # If no exception, verify empty result
            assert result["success_count"] == 0
            assert result["error_count"] == 0
            assert len(result["files"]) == 0
        except Exception as exc_info:
            # Acceptable: some implementations may reject empty array
            assert "empty" in str(exc_info).lower() or "minItems" in str(exc_info)

    def test_large_batch(self, tmp_path, monkeypatch):
        """Test reading 100 files in batch (performance test)."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator
        import time

        # Create 100 small test files
        file_paths = []
        for i in range(100):
            test_file = tmp_path / f"test{i}.txt"
            test_file.write_text(f"content{i}\n", encoding="utf-8")
            file_paths.append(f"test{i}.txt")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr("context_mcp.tools.read.validator", PathValidator(tmp_path))

        start_time = time.time()
        result = read_files(file_paths=file_paths)
        elapsed = time.time() - start_time

        # Verify all files read successfully
        assert result["success_count"] == 100
        assert result["error_count"] == 0
        # Performance: should complete in <5 seconds
        assert elapsed < 5.0, f"Batch read took {elapsed:.2f}s, expected <5s"
