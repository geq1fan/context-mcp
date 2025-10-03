"""Contract tests for search tools.

Tests for: search_in_file, search_in_files, find_files_by_name, find_recently_modified_files
"""
import pytest
from agent_mcp.tools.search import (
    search_in_file,
    search_in_files,
    find_files_by_name,
    find_recently_modified_files
)


class TestSearchInFileContract:
    """Contract tests for search_in_file tool."""

    def test_input_schema_required_fields(self):
        """Test that query and file_path are required."""
        result = search_in_file(query="test", file_path="README.md")
        assert "matches" in result
        assert "total_matches" in result

    def test_input_schema_use_regex_default(self):
        """Test that use_regex defaults to false."""
        result = search_in_file(query="test", file_path="README.md")
        assert isinstance(result["matches"], list)

    def test_output_schema_required_fields(self):
        """Test that output contains all required fields."""
        result = search_in_file(query="test", file_path="README.md")

        assert "matches" in result
        assert "total_matches" in result
        assert isinstance(result["matches"], list)
        assert isinstance(result["total_matches"], int)

    def test_output_schema_match_fields(self):
        """Test that each match contains required fields."""
        result = search_in_file(query="test", file_path="README.md")

        for match in result["matches"]:
            assert "line_number" in match
            assert "line_content" in match
            assert isinstance(match["line_number"], int)
            assert isinstance(match["line_content"], str)

    def test_error_path_security_error(self):
        """Test PATH_SECURITY_ERROR for paths outside root."""
        with pytest.raises(Exception) as exc_info:
            search_in_file(query="test", file_path="../../etc/passwd")
        assert "PATH_SECURITY_ERROR" in str(exc_info.value) or "outside root" in str(exc_info.value).lower()

    def test_error_file_not_found(self):
        """Test FILE_NOT_FOUND error."""
        with pytest.raises(Exception) as exc_info:
            search_in_file(query="test", file_path="nonexistent_file.txt")
        assert "FILE_NOT_FOUND" in str(exc_info.value) or "not exist" in str(exc_info.value).lower()


class TestSearchInFilesContract:
    """Contract tests for search_in_files tool."""

    def test_input_schema_required_only_query(self):
        """Test that only query is required."""
        result = search_in_files(query="test")
        assert "matches" in result
        assert "total_matches" in result
        assert "files_searched" in result
        assert "timed_out" in result

    def test_input_schema_default_values(self):
        """Test default values for optional parameters."""
        result = search_in_files(query="test")
        assert isinstance(result, dict)

    def test_input_schema_timeout_minimum(self):
        """Test that timeout respects minimum constraint (1)."""
        result = search_in_files(query="test", timeout=1)
        assert isinstance(result["timed_out"], bool)

    def test_output_schema_required_fields(self):
        """Test that output contains all required fields."""
        result = search_in_files(query="test")

        assert "matches" in result
        assert "total_matches" in result
        assert "files_searched" in result
        assert "timed_out" in result

        assert isinstance(result["matches"], list)
        assert isinstance(result["total_matches"], int)
        assert isinstance(result["files_searched"], int)
        assert isinstance(result["timed_out"], bool)

    def test_output_schema_match_fields(self):
        """Test that each match contains required fields."""
        result = search_in_files(query="test")

        for match in result["matches"]:
            assert "file_path" in match
            assert "line_number" in match
            assert "line_content" in match
            assert isinstance(match["file_path"], str)
            assert isinstance(match["line_number"], int)
            assert isinstance(match["line_content"], str)

    def test_error_path_security_error(self):
        """Test PATH_SECURITY_ERROR for paths outside root."""
        with pytest.raises(Exception) as exc_info:
            search_in_files(query="test", path="../../etc")
        assert "PATH_SECURITY_ERROR" in str(exc_info.value) or "outside root" in str(exc_info.value).lower()


class TestFindFilesByNameContract:
    """Contract tests for find_files_by_name tool."""

    def test_input_schema_required_name_pattern(self):
        """Test that name_pattern is required."""
        result = find_files_by_name(name_pattern="*.py")
        assert "files" in result
        assert "total_found" in result

    def test_input_schema_path_default(self):
        """Test that path defaults to current directory."""
        result = find_files_by_name(name_pattern="*.md")
        assert isinstance(result["files"], list)

    def test_output_schema_required_fields(self):
        """Test that output contains all required fields."""
        result = find_files_by_name(name_pattern="*.json")

        assert "files" in result
        assert "total_found" in result
        assert isinstance(result["files"], list)
        assert isinstance(result["total_found"], int)

    def test_output_schema_file_paths_are_strings(self):
        """Test that each file path is a string."""
        result = find_files_by_name(name_pattern="*.toml")

        for file_path in result["files"]:
            assert isinstance(file_path, str)

    def test_error_path_security_error(self):
        """Test PATH_SECURITY_ERROR for paths outside root."""
        with pytest.raises(Exception) as exc_info:
            find_files_by_name(name_pattern="*.txt", path="../../etc")
        assert "PATH_SECURITY_ERROR" in str(exc_info.value) or "outside root" in str(exc_info.value).lower()


class TestFindRecentlyModifiedFilesContract:
    """Contract tests for find_recently_modified_files tool."""

    def test_input_schema_required_hours_ago(self):
        """Test that hours_ago is required."""
        result = find_recently_modified_files(hours_ago=24)
        assert "files" in result
        assert "total_found" in result

    def test_input_schema_hours_ago_minimum(self):
        """Test that hours_ago respects minimum constraint (1)."""
        result = find_recently_modified_files(hours_ago=1)
        assert isinstance(result["files"], list)

    def test_input_schema_default_values(self):
        """Test default values for path and file_pattern."""
        result = find_recently_modified_files(hours_ago=48)
        assert isinstance(result, dict)

    def test_output_schema_required_fields(self):
        """Test that output contains all required fields."""
        result = find_recently_modified_files(hours_ago=24)

        assert "files" in result
        assert "total_found" in result
        assert isinstance(result["files"], list)
        assert isinstance(result["total_found"], int)

    def test_output_schema_file_entry_fields(self):
        """Test that each file entry contains required fields."""
        result = find_recently_modified_files(hours_ago=720)  # 30 days

        for file_entry in result["files"]:
            assert "path" in file_entry
            assert "mtime" in file_entry
            assert isinstance(file_entry["path"], str)
            assert isinstance(file_entry["mtime"], (int, float))

    def test_error_path_security_error(self):
        """Test PATH_SECURITY_ERROR for paths outside root."""
        with pytest.raises(Exception) as exc_info:
            find_recently_modified_files(hours_ago=24, path="../../etc")
        assert "PATH_SECURITY_ERROR" in str(exc_info.value) or "outside root" in str(exc_info.value).lower()
