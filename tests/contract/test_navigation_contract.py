"""Contract tests for navigation tools: list_directory, show_tree, and read_project_context.

These tests verify that the MCP tool implementations conform to the contract
specifications defined in contracts/navigation_tools.json and read_project_context.json.
"""
import pytest
from pathlib import Path
from agent_mcp.tools.navigation import list_directory, show_tree, read_project_context


class TestListDirectoryContract:
    """Contract tests for list_directory tool."""

    def test_input_schema_default_values(self):
        """Test that default values match contract specification."""
        # Should work with only path parameter (others have defaults)
        result = list_directory(path=".")
        assert "entries" in result
        assert "total" in result
        assert "truncated" in result

    def test_input_schema_sort_by_validation(self):
        """Test that sort_by accepts only valid enum values."""
        # Valid values: "name", "size", "time"
        for sort_by in ["name", "size", "time"]:
            result = list_directory(path=".", sort_by=sort_by)
            assert isinstance(result["entries"], list)

    def test_input_schema_order_validation(self):
        """Test that order accepts only valid enum values."""
        # Valid values: "asc", "desc"
        for order in ["asc", "desc"]:
            result = list_directory(path=".", order=order)
            assert isinstance(result["entries"], list)

    def test_input_schema_limit_minimum(self):
        """Test that limit respects minimum constraint (-1)."""
        result = list_directory(path=".", limit=-1)
        assert isinstance(result["total"], int)

    def test_output_schema_required_fields(self):
        """Test that output contains all required fields."""
        result = list_directory(path=".")

        # Top-level required fields
        assert "entries" in result
        assert "total" in result
        assert "truncated" in result

        # Validate types
        assert isinstance(result["entries"], list)
        assert isinstance(result["total"], int)
        assert isinstance(result["truncated"], bool)

    def test_output_schema_entry_fields(self):
        """Test that each entry contains all required fields."""
        result = list_directory(path=".")

        for entry in result["entries"]:
            assert "name" in entry
            assert "type" in entry
            assert "size" in entry
            assert "mtime" in entry
            assert "path" in entry

            # Validate types
            assert isinstance(entry["name"], str)
            assert entry["type"] in ["file", "dir"]
            assert isinstance(entry["size"], int)
            assert isinstance(entry["mtime"], (int, float))
            assert isinstance(entry["path"], str)

    def test_error_path_security_error(self):
        """Test PATH_SECURITY_ERROR is raised for paths outside root."""
        with pytest.raises(Exception) as exc_info:
            list_directory(path="../../etc")
        assert "PATH_SECURITY_ERROR" in str(exc_info.value) or "outside root" in str(exc_info.value).lower()

    def test_error_path_not_found(self):
        """Test PATH_NOT_FOUND error for non-existent directory."""
        with pytest.raises(Exception) as exc_info:
            list_directory(path="nonexistent_directory_xyz")
        assert "PATH_NOT_FOUND" in str(exc_info.value) or "not exist" in str(exc_info.value).lower()


class TestShowTreeContract:
    """Contract tests for show_tree tool."""

    def test_input_schema_default_values(self):
        """Test that default values match contract specification."""
        result = show_tree(path=".")
        assert "tree" in result
        assert "max_depth_reached" in result

    def test_input_schema_max_depth_range(self):
        """Test that max_depth respects min/max constraints (1-10)."""
        # Minimum: 1
        result = show_tree(path=".", max_depth=1)
        assert result["tree"]["depth"] == 0

        # Maximum: 10
        result = show_tree(path=".", max_depth=10)
        assert isinstance(result["tree"], dict)

    def test_output_schema_required_fields(self):
        """Test that output contains all required fields."""
        result = show_tree(path=".")

        # Top-level required fields
        assert "tree" in result
        assert "max_depth_reached" in result

        # Validate types
        assert isinstance(result["tree"], dict)
        assert isinstance(result["max_depth_reached"], bool)

    def test_output_schema_tree_node_fields(self):
        """Test that tree node contains all required fields."""
        result = show_tree(path=".")
        tree = result["tree"]

        # Required fields for tree node
        assert "name" in tree
        assert "type" in tree
        assert "depth" in tree

        # Validate types
        assert isinstance(tree["name"], str)
        assert tree["type"] in ["file", "dir"]
        assert isinstance(tree["depth"], int)

        # Children is optional
        if "children" in tree:
            assert isinstance(tree["children"], list)

    def test_output_schema_recursive_structure(self):
        """Test that children nodes have same structure as parent."""
        result = show_tree(path=".", max_depth=2)
        tree = result["tree"]

        if "children" in tree and len(tree["children"]) > 0:
            child = tree["children"][0]
            assert "name" in child
            assert "type" in child
            assert "depth" in child
            assert child["depth"] == 1

    def test_error_path_security_error(self):
        """Test PATH_SECURITY_ERROR is raised for paths outside root."""
        with pytest.raises(Exception) as exc_info:
            show_tree(path="../../etc")
        assert "PATH_SECURITY_ERROR" in str(exc_info.value) or "outside root" in str(exc_info.value).lower()

    def test_error_path_not_found(self):
        """Test PATH_NOT_FOUND error for non-existent directory."""
        with pytest.raises(Exception) as exc_info:
            show_tree(path="nonexistent_directory_xyz")
        assert "PATH_NOT_FOUND" in str(exc_info.value) or "not exist" in str(exc_info.value).lower()


@pytest.mark.contract
class TestReadProjectContextContract:
    """Contract tests for read_project_context tool."""

    def test_both_files_exist(self, tmp_path, monkeypatch):
        """Test case: Both AGENTS.md and CLAUDE.md exist and are readable."""
        # Setup: Create both context files
        agents_content = "# Agent Instructions\nFollow these guidelines..."
        claude_content = "# Claude Configuration\nUse these settings..."

        (tmp_path / "AGENTS.md").write_text(agents_content, encoding="utf-8")
        (tmp_path / "CLAUDE.md").write_text(claude_content, encoding="utf-8")

        # Mock config module
        from agent_mcp.config import ProjectConfig
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify output schema
        assert "files" in result
        assert "message" in result
        assert "total_found" in result

        assert len(result["files"]) == 2
        assert result["total_found"] == 2
        assert result["message"] == "Found 2 of 2 context files"

        # Verify AGENTS.md (first in priority order)
        agents_file = result["files"][0]
        assert agents_file["filename"] == "AGENTS.md"
        assert agents_file["exists"] is True
        assert agents_file["readable"] is True
        assert agents_file["size_bytes"] == (tmp_path / "AGENTS.md").stat().st_size
        assert agents_file["content"] == agents_content
        assert agents_file["error"] is None

        # Verify CLAUDE.md (second in priority order)
        claude_file = result["files"][1]
        assert claude_file["filename"] == "CLAUDE.md"
        assert claude_file["exists"] is True
        assert claude_file["readable"] is True
        assert claude_file["size_bytes"] == (tmp_path / "CLAUDE.md").stat().st_size
        assert claude_file["content"] == claude_content
        assert claude_file["error"] is None

    def test_only_agents_md_exists(self, tmp_path, monkeypatch):
        """Test case: Only AGENTS.md exists, CLAUDE.md is missing."""
        # Setup: Create only AGENTS.md
        agents_content = "# Universal Agent Instructions\nProject conventions..."
        (tmp_path / "AGENTS.md").write_text(agents_content, encoding="utf-8")

        from agent_mcp.config import ProjectConfig
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify
        assert len(result["files"]) == 2
        assert result["total_found"] == 1
        assert result["message"] == "Found 1 of 2 context files"

        # AGENTS.md exists
        assert result["files"][0]["filename"] == "AGENTS.md"
        assert result["files"][0]["exists"] is True
        assert result["files"][0]["readable"] is True
        assert result["files"][0]["content"] == agents_content

        # CLAUDE.md does not exist
        assert result["files"][1]["filename"] == "CLAUDE.md"
        assert result["files"][1]["exists"] is False
        assert result["files"][1]["readable"] is False
        assert result["files"][1]["content"] is None
        assert result["files"][1]["size_bytes"] is None

    def test_only_claude_md_exists(self, tmp_path, monkeypatch):
        """Test case: Only CLAUDE.md exists, AGENTS.md is missing."""
        # Setup: Create only CLAUDE.md
        claude_content = "# Claude-specific rules\nCode style preferences..."
        (tmp_path / "CLAUDE.md").write_text(claude_content, encoding="utf-8")

        from agent_mcp.config import ProjectConfig
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify
        assert len(result["files"]) == 2
        assert result["total_found"] == 1
        assert result["message"] == "Found 1 of 2 context files"

        # AGENTS.md does not exist (but listed first due to priority)
        assert result["files"][0]["filename"] == "AGENTS.md"
        assert result["files"][0]["exists"] is False

        # CLAUDE.md exists
        assert result["files"][1]["filename"] == "CLAUDE.md"
        assert result["files"][1]["exists"] is True
        assert result["files"][1]["readable"] is True
        assert result["files"][1]["content"] == claude_content

    def test_no_files_exist(self, tmp_path, monkeypatch):
        """Test case: Neither AGENTS.md nor CLAUDE.md exist in PROJECT_ROOT."""
        # Setup: Empty directory (no context files)
        from agent_mcp.config import ProjectConfig
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify
        assert len(result["files"]) == 2
        assert result["total_found"] == 0
        assert "No context files found" in result["message"]

        # Both files do not exist
        for file_info in result["files"]:
            assert file_info["exists"] is False
            assert file_info["readable"] is False
            assert file_info["content"] is None
            assert file_info["size_bytes"] is None

    def test_empty_file(self, tmp_path, monkeypatch):
        """Test case: AGENTS.md exists but is empty (0 bytes)."""
        # Setup: Create empty AGENTS.md
        (tmp_path / "AGENTS.md").write_text("", encoding="utf-8")

        from agent_mcp.config import ProjectConfig
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify
        assert result["total_found"] == 1
        assert result["message"] == "Found 1 of 2 context files"

        agents_file = result["files"][0]
        assert agents_file["filename"] == "AGENTS.md"
        assert agents_file["exists"] is True
        assert agents_file["readable"] is True
        assert agents_file["size_bytes"] == 0
        assert agents_file["content"] == ""
        assert agents_file["error"] is None

    def test_permission_denied(self, tmp_path, monkeypatch):
        """Test case: AGENTS.md exists but cannot be read due to permission error."""
        import sys
        if sys.platform == "win32":
            pytest.skip("Permission testing requires POSIX platform")

        # Setup: Create file with no read permissions
        agents_file = tmp_path / "AGENTS.md"
        agents_file.write_text("# Protected content", encoding="utf-8")
        agents_file.chmod(0o000)  # Remove all permissions

        from agent_mcp.config import ProjectConfig
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        try:
            # Execute
            result = read_project_context()

            # Verify
            assert result["total_found"] == 0
            assert "exists but not readable" in result["message"]

            agents_file_result = result["files"][0]
            assert agents_file_result["filename"] == "AGENTS.md"
            assert agents_file_result["exists"] is True
            assert agents_file_result["readable"] is False
            assert agents_file_result["content"] is None
            assert "Permission denied" in agents_file_result["error"]
        finally:
            # Cleanup: Restore permissions
            agents_file.chmod(0o644)

    def test_invalid_encoding(self, tmp_path, monkeypatch):
        """Test case: CLAUDE.md exists but contains invalid UTF-8 bytes."""
        # Setup: Create file with invalid UTF-8
        claude_file = tmp_path / "CLAUDE.md"
        claude_file.write_bytes(b"# Valid start\n\xff\xfe\nInvalid bytes")

        from agent_mcp.config import ProjectConfig
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify
        assert result["total_found"] == 0
        assert "exists but not readable" in result["message"]

        claude_file_result = result["files"][1]
        assert claude_file_result["filename"] == "CLAUDE.md"
        assert claude_file_result["exists"] is True
        assert claude_file_result["readable"] is False
        assert claude_file_result["content"] is None
        assert claude_file_result["error"] is not None
        assert "encoding" in claude_file_result["error"].lower() or "decode" in claude_file_result["error"].lower()

    def test_large_file(self, tmp_path, monkeypatch, caplog):
        """Test case: AGENTS.md is larger than 1MB (warning logged but file still returned)."""
        import logging

        # Setup: Create file >1MB
        large_content = "A" * (1024 * 1024 + 100)  # 1MB + 100 bytes
        (tmp_path / "AGENTS.md").write_text(large_content, encoding="utf-8")

        from agent_mcp.config import ProjectConfig
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute with log capturing
        with caplog.at_level(logging.WARNING):
            result = read_project_context()

        # Verify file is still returned
        assert result["total_found"] == 1
        agents_file = result["files"][0]
        assert agents_file["filename"] == "AGENTS.md"
        assert agents_file["exists"] is True
        assert agents_file["readable"] is True
        assert agents_file["size_bytes"] == (tmp_path / "AGENTS.md").stat().st_size
        assert agents_file["content"] == large_content

        # Verify warning was logged
        assert any("large" in record.message.lower() for record in caplog.records)

    def test_output_schema_required_fields(self, tmp_path, monkeypatch):
        """Test that output contains all required fields according to contract."""
        from agent_mcp.config import ProjectConfig
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        result = read_project_context()

        # Top-level required fields
        assert "files" in result
        assert "message" in result

        # Validate types
        assert isinstance(result["files"], list)
        assert isinstance(result["message"], str)
        assert len(result["message"]) > 0

        # Optional field
        if "total_found" in result:
            assert isinstance(result["total_found"], int)
            assert 0 <= result["total_found"] <= 2

        # Files array constraints
        assert len(result["files"]) == 2  # Exactly 2 files (AGENTS.md and CLAUDE.md)

        # Verify each file has required fields
        for file_info in result["files"]:
            assert "filename" in file_info
            assert "exists" in file_info
            assert "readable" in file_info

            assert isinstance(file_info["filename"], str)
            assert file_info["filename"] in ["AGENTS.md", "CLAUDE.md"]
            assert isinstance(file_info["exists"], bool)
            assert isinstance(file_info["readable"], bool)

            # Optional fields
            if file_info["exists"]:
                assert "size_bytes" in file_info
                assert file_info["size_bytes"] is None or isinstance(file_info["size_bytes"], int)

            assert "content" in file_info
            assert file_info["content"] is None or isinstance(file_info["content"], str)

            assert "error" in file_info
            assert file_info["error"] is None or isinstance(file_info["error"], str)
