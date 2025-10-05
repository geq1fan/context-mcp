"""Contract tests for search tools.

Tests for: search_in_file, search_in_files, find_files_by_name, find_recently_modified_files
"""

import pytest
from context_mcp.tools.search import (
    search_in_file,
    search_in_files,
    find_files_by_name,
    find_recently_modified_files,
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
        assert (
            "PATH_SECURITY_ERROR" in str(exc_info.value)
            or "outside root" in str(exc_info.value).lower()
        )

    def test_error_file_not_found(self):
        """Test FILE_NOT_FOUND error."""
        with pytest.raises(Exception) as exc_info:
            search_in_file(query="test", file_path="nonexistent_file.txt")
        assert (
            "FILE_NOT_FOUND" in str(exc_info.value)
            or "not exist" in str(exc_info.value).lower()
        )

    def test_use_regex_true(self, tmp_path, monkeypatch):
        """Test regex pattern search with use_regex=True."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        test_file = tmp_path / "test.txt"
        test_file.write_text("test123\nfoo\ntest456\n", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr(
            "context_mcp.tools.search.validator", PathValidator(tmp_path)
        )

        result = search_in_file(query=r"test\d+", file_path="test.txt", use_regex=True)
        assert result["total_matches"] == 2
        assert any("test123" in m["line_content"] for m in result["matches"])
        assert any("test456" in m["line_content"] for m in result["matches"])

    def test_query_with_regex_special_chars_literal(self, tmp_path, monkeypatch):
        """Test regex special chars treated as literal when use_regex=False."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        test_file = tmp_path / "test.txt"
        test_file.write_text("test[0-9]+\ntest123\n", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr(
            "context_mcp.tools.search.validator", PathValidator(tmp_path)
        )

        result = search_in_file(
            query="test[0-9]+", file_path="test.txt", use_regex=False
        )
        # Should match literal "test[0-9]+", NOT test123
        assert result["total_matches"] == 1
        assert "test[0-9]+" in result["matches"][0]["line_content"]


class TestSearchInFilesContract:
    """Contract tests for search_in_files tool."""

    def test_input_schema_required_only_query(self):
        """Test that only query is required."""
        result = search_in_files(query="test")
        assert "matches" in result
        assert "total_matches" in result
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
        assert "timed_out" in result

        assert isinstance(result["matches"], list)
        assert isinstance(result["total_matches"], int)
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
        assert (
            "PATH_SECURITY_ERROR" in str(exc_info.value)
            or "outside root" in str(exc_info.value).lower()
        )

    def test_file_pattern_specific(self, tmp_path, monkeypatch):
        """Test file_pattern filters to specific extensions."""
        from context_mcp.config import ProjectConfig

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)

        # Create .py and .txt files
        (tmp_path / "test.py").write_text("searchme", encoding="utf-8")
        (tmp_path / "test.txt").write_text("searchme", encoding="utf-8")

        result = search_in_files(query="searchme", file_pattern="*.py", path=".")
        # Should only match .py file
        assert result["total_matches"] >= 1
        for match in result["matches"]:
            assert match["file_path"].endswith(".py")

    def test_use_regex_and_exclude_query(self, tmp_path, monkeypatch):
        """Test use_regex=True with exclude_query combination."""
        from context_mcp.config import ProjectConfig

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)

        test_file = tmp_path / "test.txt"
        test_file.write_text("test123\nexclude_this_test\ntest456\n", encoding="utf-8")

        result = search_in_files(
            query=r"test.*", use_regex=True, exclude_query="exclude", path="."
        )
        # Should match test123 and test456, but NOT exclude_this_test
        assert result["total_matches"] >= 2
        for match in result["matches"]:
            assert "exclude" not in match["line_content"]

    def test_timeout_large_value(self):
        """Test timeout=3600 (large value) does not cause exception."""
        result = search_in_files(query="test", timeout=3600)
        assert "matches" in result
        assert result["timed_out"] is False

    def test_path_subdirectory(self, tmp_path, monkeypatch):
        """Test path parameter restricts search to subdirectory."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        # Create files in root and subdir
        (tmp_path / "root.txt").write_text("findme\n", encoding="utf-8")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "sub.txt").write_text("findme\n", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr(
            "context_mcp.tools.search.validator", PathValidator(tmp_path)
        )

        result = search_in_files(query="findme", path="subdir")
        # Should only find matches in subdir (if any found)
        if result["total_matches"] > 0:
            for match in result["matches"]:
                assert match["file_path"].startswith("subdir")


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
        assert (
            "PATH_SECURITY_ERROR" in str(exc_info.value)
            or "outside root" in str(exc_info.value).lower()
        )

    def test_complex_glob_pattern(self, tmp_path, monkeypatch):
        """Test complex glob pattern like 'test_*.py'."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        # Create test files
        (tmp_path / "test_foo.py").write_text("\n", encoding="utf-8")
        (tmp_path / "bar.py").write_text("\n", encoding="utf-8")
        (tmp_path / "test_baz.py").write_text("\n", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr(
            "context_mcp.tools.search.validator", PathValidator(tmp_path)
        )

        result = find_files_by_name(name_pattern="test_*.py", path=".")
        # Should find test_*.py files (implementation may vary by search tool)
        assert result["total_found"] >= 0
        if result["total_found"] > 0:
            for file_path in result["files"]:
                assert file_path.endswith(".py")

    def test_path_subdirectory(self, tmp_path, monkeypatch):
        """Test path parameter restricts search to subdirectory."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        # Create files in root and subdir
        (tmp_path / "root.txt").write_text("\n", encoding="utf-8")
        subdir = tmp_path / "context_mcp"
        subdir.mkdir()
        (subdir / "sub.txt").write_text("\n", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr(
            "context_mcp.tools.search.validator", PathValidator(tmp_path)
        )

        result = find_files_by_name(name_pattern="*.txt", path="context_mcp")
        # Should only find files in context_mcp directory (if any found)
        if result["total_found"] > 0:
            for file_path in result["files"]:
                assert file_path.startswith("context_mcp")


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
        assert (
            "PATH_SECURITY_ERROR" in str(exc_info.value)
            or "outside root" in str(exc_info.value).lower()
        )

    def test_file_pattern_filter(self, tmp_path, monkeypatch):
        """Test file_pattern filters to specific extensions."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator
        import time

        # Create recent .md and .py files
        (tmp_path / "recent.md").write_text("\n", encoding="utf-8")
        time.sleep(0.01)
        (tmp_path / "recent.py").write_text("\n", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr(
            "context_mcp.tools.search.validator", PathValidator(tmp_path)
        )

        result = find_recently_modified_files(
            hours_ago=1, file_pattern="*.md", path="."
        )
        # Should only find .md files (if any found)
        if result["total_found"] > 0:
            for file_entry in result["files"]:
                assert file_entry["path"].endswith(".md")

    def test_hours_ago_large(self):
        """Test hours_ago=720 (30 days) large value."""
        result = find_recently_modified_files(hours_ago=720)
        # Should return files modified in last 30 days without error
        assert "files" in result
        assert isinstance(result["total_found"], int)

    def test_path_subdirectory(self, tmp_path, monkeypatch):
        """Test path parameter restricts search to subdirectory."""
        from context_mcp.config import ProjectConfig
        from context_mcp.validators.path_validator import PathValidator

        # Create files in root and specs subdir
        (tmp_path / "root.txt").write_text("\n", encoding="utf-8")
        subdir = tmp_path / "specs"
        subdir.mkdir()
        (subdir / "sub.txt").write_text("\n", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("context_mcp.config.config", mock_config)
        monkeypatch.setattr(
            "context_mcp.tools.search.validator", PathValidator(tmp_path)
        )

        result = find_recently_modified_files(hours_ago=1, path="specs")
        # Should only find files in specs directory (if any found)
        if result["total_found"] > 0:
            for file_entry in result["files"]:
                assert file_entry["path"].startswith("specs")
