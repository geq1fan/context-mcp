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
