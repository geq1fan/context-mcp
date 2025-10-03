"""Integration tests covering full workflows from quickstart.md.

These tests validate end-to-end scenarios:
- Step 1-2: Navigation (list directory, show tree)
- Step 3: Search (in file, in files, by name, recent files)
- Step 4: Read (entire, lines, tail, batch)
"""
import pytest
import tempfile
import os
from pathlib import Path


class TestNavigationWorkflow:
    """Tests for navigation workflow (quickstart步骤1-2)."""

    def test_list_directory_and_sort(self):
        """Test listing directory with different sort options."""
        from agent_mcp.tools.navigation import list_directory

        # List current directory
        result = list_directory(path=".")
        assert result["total"] > 0
        assert len(result["entries"]) > 0

        # Sort by size descending
        result_sorted = list_directory(path=".", sort_by="size", order="desc")
        if len(result_sorted["entries"]) >= 2:
            assert result_sorted["entries"][0]["size"] >= result_sorted["entries"][1]["size"]

    def test_show_tree_with_depth_limit(self):
        """Test showing directory tree with depth limit."""
        from agent_mcp.tools.navigation import show_tree

        # Show tree with depth 2
        result = show_tree(path=".", max_depth=2)
        assert result["tree"]["depth"] == 0
        assert result["tree"]["type"] == "dir"

        # Check children depth
        if "children" in result["tree"] and len(result["tree"]["children"]) > 0:
            child = result["tree"]["children"][0]
            assert child["depth"] == 1


class TestSearchWorkflow:
    """Tests for search workflow (quickstart步骤3)."""

    def test_search_in_file_workflow(self):
        """Test searching within a single file."""
        from agent_mcp.tools.search import search_in_file

        # Search for common pattern in pyproject.toml
        result = search_in_file(query="name", file_path="pyproject.toml")
        assert result["total_matches"] >= 0
        assert isinstance(result["matches"], list)

    def test_search_in_files_with_pattern(self):
        """Test multi-file search with file pattern."""
        from agent_mcp.tools.search import search_in_files

        # Search Python files for import statements
        result = search_in_files(
            query="import",
            file_pattern="*.py",
            path="agent_mcp"
        )
        assert result["files_searched"] >= 0
        assert isinstance(result["timed_out"], bool)

    def test_find_files_by_name_pattern(self):
        """Test finding files by name pattern."""
        from agent_mcp.tools.search import find_files_by_name

        # Find all Python files
        result = find_files_by_name(name_pattern="*.py", path="agent_mcp")
        assert result["total_found"] >= 0
        assert isinstance(result["files"], list)

    def test_find_recently_modified_files(self):
        """Test finding recently modified files."""
        from agent_mcp.tools.search import find_recently_modified_files

        # Find files modified in last 24 hours
        result = find_recently_modified_files(
            hours_ago=24,
            path=".",
            file_pattern="*.py"
        )
        assert result["total_found"] >= 0
        assert isinstance(result["files"], list)


class TestReadWorkflow:
    """Tests for read workflow (quickstart步骤4)."""

    def test_read_entire_file_workflow(self):
        """Test reading complete file."""
        from agent_mcp.tools.read import read_entire_file

        # Read pyproject.toml
        result = read_entire_file(file_path="pyproject.toml")
        assert len(result["content"]) > 0
        assert result["line_count"] > 0
        assert result["encoding"] in ["utf-8", "ascii"]

    def test_read_file_lines_workflow(self):
        """Test reading specific line range."""
        from agent_mcp.tools.read import read_file_lines

        # Read first 10 lines
        result = read_file_lines(
            file_path="pyproject.toml",
            start_line=1,
            end_line=10
        )
        assert result["line_count"] <= 10
        assert result["is_partial"] == True
        assert result["total_lines"] >= result["line_count"]

    def test_read_file_tail_workflow(self):
        """Test reading file tail."""
        from agent_mcp.tools.read import read_file_tail

        # Read last 5 lines
        result = read_file_tail(file_path="pyproject.toml", num_lines=5)
        assert result["line_count"] <= 5
        assert isinstance(result["content"], str)

    def test_read_files_batch_workflow(self):
        """Test batch reading multiple files."""
        from agent_mcp.tools.read import read_files

        # Read multiple config files
        result = read_files(file_paths=["pyproject.toml", ".env.example"])
        assert result["success_count"] + result["error_count"] == 2
        assert len(result["files"]) == 2


class TestCompleteAgentWorkflow:
    """Test complete agent workflow from quickstart.md."""

    def test_analyze_new_project_workflow(self):
        """Simulate agent analyzing a new project (quickstart complete workflow)."""
        from agent_mcp.tools.navigation import show_tree, list_directory
        from agent_mcp.tools.search import find_files_by_name, search_in_files
        from agent_mcp.tools.read import read_files

        # Step 1: View project structure
        tree_result = show_tree(path=".", max_depth=2)
        assert "tree" in tree_result

        # Step 2: Find configuration files
        json_files = find_files_by_name(name_pattern="*.json")
        toml_files = find_files_by_name(name_pattern="*.toml")
        assert json_files["total_found"] >= 0 or toml_files["total_found"] >= 0

        # Step 3: Read key configuration
        config_files = ["pyproject.toml"]
        read_result = read_files(file_paths=config_files)
        assert read_result["success_count"] >= 1

        # Step 4: Search for imports
        search_result = search_in_files(
            query="import",
            file_pattern="*.py",
            path="agent_mcp"
        )
        assert isinstance(search_result["matches"], list)


@pytest.mark.integration
class TestContextFileWorkflow:
    """Integration tests for read_project_context tool workflow."""

    def test_read_context_files_full_workflow(self, tmp_path, monkeypatch):
        """Test full workflow: create context files, read them, verify response."""
        from agent_mcp.tools.navigation import read_project_context
        from agent_mcp.config import ProjectConfig

        # Step 1: Setup - Create both context files
        agents_content = """# Universal Agent Instructions

## Project Guidelines
- Follow TDD principles
- Use type hints
- Write comprehensive tests

## Code Style
- PEP 8 compliant
- Maximum line length: 100
- Use pathlib for file operations
"""

        claude_content = """# Claude Code Configuration

## Response Style
- Be concise and direct
- Provide code examples
- Explain complex concepts

## Project Context
This is a Python MCP server using fastmcp framework.
Focus on security and performance.
"""

        (tmp_path / "AGENTS.md").write_text(agents_content, encoding="utf-8")
        (tmp_path / "CLAUDE.md").write_text(claude_content, encoding="utf-8")

        # Mock PROJECT_ROOT
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Step 2: Call read_project_context
        result = read_project_context()

        # Step 3: Verify response structure
        assert "files" in result
        assert "message" in result
        assert "total_found" in result

        # Step 4: Verify both files returned
        assert len(result["files"]) == 2
        assert result["total_found"] == 2
        assert result["message"] == "Found 2 of 2 context files"

        # Step 5: Verify AGENTS.md comes first (priority order)
        assert result["files"][0]["filename"] == "AGENTS.md"
        assert result["files"][0]["exists"] is True
        assert result["files"][0]["readable"] is True
        assert result["files"][0]["content"] == agents_content

        # Step 6: Verify CLAUDE.md comes second
        assert result["files"][1]["filename"] == "CLAUDE.md"
        assert result["files"][1]["exists"] is True
        assert result["files"][1]["readable"] is True
        assert result["files"][1]["content"] == claude_content

        # Step 7: Verify metadata
        assert result["files"][0]["size_bytes"] == (tmp_path / "AGENTS.md").stat().st_size
        assert result["files"][1]["size_bytes"] == (tmp_path / "CLAUDE.md").stat().st_size
        assert result["files"][0]["error"] is None
        assert result["files"][1]["error"] is None

    def test_context_files_missing_graceful_handling(self, tmp_path, monkeypatch):
        """Test graceful handling when no context files exist."""
        from agent_mcp.tools.navigation import read_project_context
        from agent_mcp.config import ProjectConfig

        # Setup: Empty directory (no context files)
        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify graceful response
        assert "files" in result
        assert "message" in result
        assert "total_found" in result

        assert len(result["files"]) == 2
        assert result["total_found"] == 0
        assert "No context files found" in result["message"]

        # Both files should be reported as not existing
        for file_info in result["files"]:
            assert file_info["exists"] is False
            assert file_info["readable"] is False
            assert file_info["content"] is None
            assert file_info["size_bytes"] is None
            assert file_info["error"] is None

    def test_context_files_partial_discovery(self, tmp_path, monkeypatch):
        """Test when only one context file exists."""
        from agent_mcp.tools.navigation import read_project_context
        from agent_mcp.config import ProjectConfig

        # Setup: Create only AGENTS.md
        agents_content = "# Project-wide agent instructions\n"
        (tmp_path / "AGENTS.md").write_text(agents_content, encoding="utf-8")

        mock_config = ProjectConfig(root_path=tmp_path)
        monkeypatch.setattr("agent_mcp.config.config", mock_config)

        # Execute
        result = read_project_context()

        # Verify partial discovery
        assert result["total_found"] == 1
        assert result["message"] == "Found 1 of 2 context files"

        # AGENTS.md found
        assert result["files"][0]["filename"] == "AGENTS.md"
        assert result["files"][0]["exists"] is True
        assert result["files"][0]["content"] == agents_content

        # CLAUDE.md not found
        assert result["files"][1]["filename"] == "CLAUDE.md"
        assert result["files"][1]["exists"] is False
        assert result["files"][1]["content"] is None
