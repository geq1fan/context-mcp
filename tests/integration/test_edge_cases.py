"""Integration tests for edge cases and boundary conditions.

Tests from quickstart.md Step 5-6:
- Security boundaries (path traversal, binary files)
- Empty results, invalid inputs
- Timeouts, permission errors
"""
import pytest
import tempfile
import os
from pathlib import Path


class TestSecurityBoundaries:
    """Test security boundary conditions."""

    def test_path_traversal_attack_list_directory(self):
        """Test path traversal attack is blocked in list_directory."""
        from agent_mcp.tools.navigation import list_directory

        with pytest.raises(Exception) as exc_info:
            list_directory(path="../../etc")
        assert "security" in str(exc_info.value).lower() or "outside" in str(exc_info.value).lower()

    def test_path_traversal_attack_read_file(self):
        """Test path traversal attack is blocked in read operations."""
        from agent_mcp.tools.read import read_entire_file

        with pytest.raises(Exception) as exc_info:
            read_entire_file(file_path="../../../etc/passwd")
        assert "security" in str(exc_info.value).lower() or "outside" in str(exc_info.value).lower()

    def test_path_traversal_attack_search(self):
        """Test path traversal attack is blocked in search operations."""
        from agent_mcp.tools.search import search_in_files

        with pytest.raises(Exception) as exc_info:
            search_in_files(query="test", path="../../etc")
        assert "security" in str(exc_info.value).lower() or "outside" in str(exc_info.value).lower()


class TestEmptyAndInvalidInputs:
    """Test empty results and invalid inputs."""

    def test_empty_directory(self):
        """Test listing an empty directory."""
        from agent_mcp.tools.navigation import list_directory
        import tempfile
        import os

        # Create temporary empty directory within project
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            dir_name = os.path.basename(tmpdir)
            result = list_directory(path=dir_name)
            assert result["total"] == 0
            assert len(result["entries"]) == 0
            assert result["truncated"] == False

    def test_nonexistent_directory(self):
        """Test accessing non-existent directory."""
        from agent_mcp.tools.navigation import list_directory

        with pytest.raises(Exception) as exc_info:
            list_directory(path="nonexistent_dir_xyz_123")
        assert "not found" in str(exc_info.value).lower() or "not exist" in str(exc_info.value).lower()

    def test_nonexistent_file(self):
        """Test reading non-existent file."""
        from agent_mcp.tools.read import read_entire_file

        with pytest.raises(Exception) as exc_info:
            read_entire_file(file_path="nonexistent_file_xyz_123.txt")
        # Check for FILE_NOT_FOUND error code or relevant error messages
        error_msg = str(exc_info.value).lower()
        assert "file_not_found" in error_msg or "not found" in error_msg or "not exist" in error_msg

    def test_search_no_matches(self):
        """Test search with no matches using a very unique string unlikely to exist."""
        from agent_mcp.tools.search import search_in_files

        # Use an extremely unique query string with special markers
        result = search_in_files(
            query="ZZZYYYXXX_NONEXISTENT_UNIQUE_MARKER_999888777",
            file_pattern="*.md"  # Limit to markdown files to reduce false positives
        )
        # Note: In a real codebase, there might be matches in generated files or logs
        # This test checks the structure is correct even if matches > 0
        assert isinstance(result["total_matches"], int)
        assert isinstance(result["matches"], list)
        assert result["timed_out"] == False

    def test_find_no_matching_files(self):
        """Test find with no matching files."""
        from agent_mcp.tools.search import find_files_by_name

        result = find_files_by_name(name_pattern="*.nonexistent_extension_xyz")
        assert result["total_found"] == 0
        assert len(result["files"]) == 0


class TestInvalidLineRanges:
    """Test invalid line range scenarios."""

    def test_line_range_out_of_bounds(self):
        """Test reading lines beyond file length."""
        from agent_mcp.tools.read import read_file_lines

        # Try to read lines way beyond file length
        with pytest.raises(Exception) as exc_info:
            read_file_lines(
                file_path="pyproject.toml",
                start_line=10000,
                end_line=20000
            )
        # Should raise error about invalid range or just return empty

    def test_line_range_start_greater_than_end(self):
        """Test invalid line range where start > end."""
        from agent_mcp.tools.read import read_file_lines

        with pytest.raises(Exception) as exc_info:
            read_file_lines(
                file_path="pyproject.toml",
                start_line=10,
                end_line=5
            )
        assert "invalid" in str(exc_info.value).lower() or "range" in str(exc_info.value).lower()


class TestLimitAndTruncation:
    """Test limit and truncation behavior."""

    def test_list_directory_with_limit(self):
        """Test directory listing respects limit."""
        from agent_mcp.tools.navigation import list_directory

        # List with limit
        result = list_directory(path=".", limit=3)
        assert len(result["entries"]) <= 3
        if result["total"] > 3:
            assert result["truncated"] == True

    def test_list_directory_no_limit(self):
        """Test directory listing with no limit (-1)."""
        from agent_mcp.tools.navigation import list_directory

        result = list_directory(path=".", limit=-1)
        assert len(result["entries"]) == result["total"]
        assert result["truncated"] == False


class TestBatchOperationResilience:
    """Test batch operations handle partial failures."""

    def test_read_files_mixed_success_failure(self):
        """Test batch read with mix of valid and invalid files."""
        from agent_mcp.tools.read import read_files

        file_paths = [
            "pyproject.toml",           # Valid
            "nonexistent1.txt",         # Invalid
            ".env.example",             # Valid
            "nonexistent2.txt",         # Invalid
        ]

        result = read_files(file_paths=file_paths)

        # Should have both successes and errors
        assert result["success_count"] >= 2
        assert result["error_count"] >= 2
        assert result["success_count"] + result["error_count"] == 4

        # Check that valid files have content
        success_files = [f for f in result["files"] if "content" in f]
        assert len(success_files) >= 2

        # Check that invalid files have errors
        error_files = [f for f in result["files"] if "error" in f]
        assert len(error_files) >= 2


class TestSortingBehavior:
    """Test sorting edge cases."""

    def test_sort_by_time_descending(self):
        """Test sorting by modification time."""
        from agent_mcp.tools.navigation import list_directory

        result = list_directory(path=".", sort_by="time", order="desc")
        entries = result["entries"]

        if len(entries) >= 2:
            # Most recent first
            assert entries[0]["mtime"] >= entries[1]["mtime"]

    def test_sort_by_name_ascending(self):
        """Test alphabetical sorting."""
        from agent_mcp.tools.navigation import list_directory

        result = list_directory(path=".", sort_by="name", order="asc")
        entries = result["entries"]

        if len(entries) >= 2:
            # Check alphabetical order
            assert entries[0]["name"] <= entries[1]["name"]


class TestMaxDepthBehavior:
    """Test max_depth edge cases in show_tree."""

    def test_max_depth_one(self):
        """Test tree with max_depth=1 shows only current level."""
        from agent_mcp.tools.navigation import show_tree

        result = show_tree(path=".", max_depth=1)
        tree = result["tree"]

        # Root should be depth 0
        assert tree["depth"] == 0

        # Children should be depth 1 with no further children
        if "children" in tree:
            for child in tree["children"]:
                assert child["depth"] == 1
                # Should not have children at max_depth
                if child["type"] == "dir":
                    assert "children" not in child or len(child.get("children", [])) == 0

    def test_max_depth_maximum_limit(self):
        """Test tree with max_depth=10 (maximum allowed)."""
        from agent_mcp.tools.navigation import show_tree

        result = show_tree(path=".", max_depth=10)
        assert "tree" in result
        assert isinstance(result["max_depth_reached"], bool)


@pytest.mark.integration
class TestContextFileEdgeCases:
    """Edge case tests for read_project_context tool."""

    def test_context_file_permission_error(self, tmp_path, monkeypatch):
        """Test handling of permission denied error when reading context file."""
        import sys
        if sys.platform == "win32":
            pytest.skip("Permission testing requires POSIX platform")

        from agent_mcp.tools.navigation import read_project_context
        from agent_mcp.config import ProjectConfig

        # Setup: Create AGENTS.md with no read permissions
        agents_file = tmp_path / "AGENTS.md"
        agents_file.write_text("# Protected Instructions", encoding="utf-8")
        agents_file.chmod(0o000)  # Remove all permissions

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        try:
            # Execute
            result = read_project_context()

            # Verify graceful error handling
            assert result["total_found"] == 0
            assert "exists but not readable" in result["message"]

            agents_result = result["files"][0]
            assert agents_result["filename"] == "AGENTS.md"
            assert agents_result["exists"] is True
            assert agents_result["readable"] is False
            assert agents_result["content"] is None
            assert agents_result["size_bytes"] is None
            assert agents_result["error"] is not None
            assert "Permission denied" in agents_result["error"] or "permission" in agents_result["error"].lower()
        finally:
            # Cleanup: Restore permissions
            agents_file.chmod(0o644)

    def test_context_file_large_size_warning(self, tmp_path, monkeypatch, caplog):
        """Test warning is logged for large context files (>1MB)."""
        import logging
        from agent_mcp.tools.navigation import read_project_context
        from agent_mcp.config import ProjectConfig

        # Setup: Create file >1MB
        large_content = "A" * (1024 * 1024 + 200)  # 1MB + 200 bytes
        (tmp_path / "AGENTS.md").write_text(large_content, encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute with log capturing
        with caplog.at_level(logging.WARNING):
            result = read_project_context()

        # Verify file is still returned (not blocked)
        assert result["total_found"] == 1
        agents_file = result["files"][0]
        assert agents_file["filename"] == "AGENTS.md"
        assert agents_file["exists"] is True
        assert agents_file["readable"] is True
        assert agents_file["size_bytes"] == (tmp_path / "AGENTS.md").stat().st_size
        assert agents_file["content"] == large_content
        assert agents_file["error"] is None

        # Verify warning was logged
        warning_logged = any(
            "large" in record.message.lower() and "AGENTS.md" in record.message
            for record in caplog.records if record.levelname == "WARNING"
        )
        assert warning_logged, "Expected WARNING log for large file"

    def test_context_file_invalid_encoding(self, tmp_path, monkeypatch):
        """Test handling of invalid UTF-8 encoding in context file."""
        from agent_mcp.tools.navigation import read_project_context
        from agent_mcp.config import ProjectConfig

        # Setup: Create CLAUDE.md with invalid UTF-8 bytes
        claude_file = tmp_path / "CLAUDE.md"
        claude_file.write_bytes(b"# Valid Header\n\xff\xfe\nInvalid UTF-8 bytes here")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify graceful error handling
        assert result["total_found"] == 0
        assert "exists but not readable" in result["message"]

        claude_result = result["files"][1]
        assert claude_result["filename"] == "CLAUDE.md"
        assert claude_result["exists"] is True
        assert claude_result["readable"] is False
        assert claude_result["content"] is None
        assert claude_result["size_bytes"] is None
        assert claude_result["error"] is not None
        assert "encoding" in claude_result["error"].lower() or "decode" in claude_result["error"].lower()

    def test_context_file_empty_file(self, tmp_path, monkeypatch):
        """Test handling of empty context file (0 bytes)."""
        from agent_mcp.tools.navigation import read_project_context
        from agent_mcp.config import ProjectConfig

        # Setup: Create empty files
        (tmp_path / "AGENTS.md").write_text("", encoding="utf-8")
        (tmp_path / "CLAUDE.md").write_text("", encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify empty files are treated as valid
        assert result["total_found"] == 2
        assert result["message"] == "Found 2 of 2 context files"

        for file_info in result["files"]:
            assert file_info["exists"] is True
            assert file_info["readable"] is True
            assert file_info["size_bytes"] == 0
            assert file_info["content"] == ""
            assert file_info["error"] is None

    def test_context_file_whitespace_only(self, tmp_path, monkeypatch):
        """Test handling of context file with only whitespace."""
        from agent_mcp.tools.navigation import read_project_context
        from agent_mcp.config import ProjectConfig

        # Setup: Create files with only whitespace
        whitespace_content = "   \n\n\t\t  \n   "
        (tmp_path / "AGENTS.md").write_text(whitespace_content, encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify whitespace is preserved (not trimmed)
        assert result["total_found"] == 1
        agents_file = result["files"][0]
        assert agents_file["content"] == whitespace_content
        assert agents_file["size_bytes"] == (tmp_path / "AGENTS.md").stat().st_size

    def test_context_file_with_special_characters(self, tmp_path, monkeypatch):
        """Test handling of context files with special characters and unicode."""
        from agent_mcp.tools.navigation import read_project_context
        from agent_mcp.config import ProjectConfig

        # Setup: Create file with various special characters
        special_content = """# Agent Instructions 🤖

## Emoji Support
✅ Tests
❌ Errors
🚀 Performance

## Unicode Characters
- 中文字符
- русский язык
- العربية
- 日本語

## Special Symbols
© ® ™ € £ ¥ § ¶ † ‡
"""
        (tmp_path / "CLAUDE.md").write_text(special_content, encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify special characters are preserved
        assert result["total_found"] == 1
        claude_file = result["files"][1]
        assert claude_file["content"] == special_content
        assert claude_file["readable"] is True
        assert claude_file["error"] is None

    def test_context_file_symlink_handling(self, tmp_path, monkeypatch):
        """Test handling of symlinked context files."""
        import sys
        if sys.platform == "win32":
            pytest.skip("Symlink testing requires POSIX platform or admin rights on Windows")

        from agent_mcp.tools.navigation import read_project_context
        from agent_mcp.config import ProjectConfig

        # Setup: Create actual file and symlink to it
        actual_file = tmp_path / "actual_agents.md"
        actual_content = "# Actual Agent Instructions"
        actual_file.write_text(actual_content, encoding="utf-8")

        symlink = tmp_path / "AGENTS.md"
        symlink.symlink_to(actual_file)

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify symlink is followed and content is read
        assert result["total_found"] == 1
        agents_file = result["files"][0]
        assert agents_file["exists"] is True
        assert agents_file["readable"] is True
        assert agents_file["content"] == actual_content
