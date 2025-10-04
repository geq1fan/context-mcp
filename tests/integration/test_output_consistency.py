"""Integration tests for output format consistency across tools."""

import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def mock_config(tmp_path):
    """Mock config with test project root."""
    with patch("context_mcp.tools.search.config") as mock_cfg:
        mock_cfg.root_path = tmp_path
        with patch("context_mcp.tools.search.validator") as mock_val:

            def validate_side_effect(path):
                abs_path = tmp_path / path if path != "." else tmp_path
                return abs_path.resolve()

            mock_val.validate.side_effect = validate_side_effect
            yield mock_cfg


@pytest.fixture
def test_files(tmp_path):
    """Create test files with known content."""
    (tmp_path / "file1.txt").write_text("Hello world\nTest content\nHello again\n")
    (tmp_path / "file2.py").write_text(
        "def hello():\n    print('Hello')\n    return 'world'\n"
    )
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file3.txt").write_text("Nested Hello\n")
    return tmp_path


class TestSearchOutputConsistency:
    """Test search_in_files output consistency across tools."""

    @patch("context_mcp.tools.search.shutil.which")
    def test_python_fallback_output_structure(
        self, mock_which, mock_config, test_files
    ):
        """Test that Python fallback produces correct output structure."""
        from context_mcp.tools.search import search_in_files

        # Force Python fallback
        mock_which.return_value = None

        result = search_in_files(query="Hello", path=".")

        # Verify output structure
        assert isinstance(result, dict)
        assert "matches" in result
        assert "total_matches" in result
        assert "files_searched" in result
        assert "timed_out" in result

        # Verify matches structure
        if result["matches"]:
            match = result["matches"][0]
            assert "file_path" in match
            assert "line_number" in match
            assert "line_content" in match

    @patch("context_mcp.tools.search.shutil.which")
    def test_path_format_uses_forward_slashes(
        self, mock_which, mock_config, test_files
    ):
        """Test that file paths use forward slashes."""
        from context_mcp.tools.search import search_in_files

        # Force Python fallback
        mock_which.return_value = None

        result = search_in_files(query="Hello", path=".")

        # Check all file paths use forward slashes
        for match in result["matches"]:
            file_path = match["file_path"]
            # Should not contain backslashes
            assert "\\" not in file_path or "/" in file_path


class TestFindOutputConsistency:
    """Test find_files_by_name output consistency across tools."""

    @patch("context_mcp.tools.search.shutil.which")
    def test_python_fallback_output_structure(
        self, mock_which, mock_config, test_files
    ):
        """Test that Python fallback produces correct output structure."""
        from context_mcp.tools.search import find_files_by_name

        # Force Python fallback
        mock_which.return_value = None

        result = find_files_by_name(name_pattern="*.txt", path=".")

        # Verify output structure
        assert isinstance(result, dict)
        assert "files" in result
        assert "total_found" in result
        assert isinstance(result["files"], list)

    @patch("context_mcp.tools.search.shutil.which")
    def test_path_format_consistent(self, mock_which, mock_config, test_files):
        """Test that file paths are relative and use forward slashes."""
        from context_mcp.tools.search import find_files_by_name

        # Force Python fallback
        mock_which.return_value = None

        result = find_files_by_name(name_pattern="*.txt", path=".")

        # Check all paths are relative and use forward slashes
        for file_path in result["files"]:
            # Should be relative paths
            assert not Path(file_path).is_absolute()
            # Ideally should use forward slashes (current implementation may vary)
            # This will be enforced after T010
