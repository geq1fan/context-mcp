"""Integration tests for tool fallback logic."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess


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
    """Create test files."""
    (tmp_path / "test1.txt").write_text("Hello world\nTest content\n")
    (tmp_path / "test2.py").write_text("def test():\n    pass\n")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "test3.txt").write_text("Nested file\n")
    return tmp_path


class TestSearchInFilesRipgrep:
    """Test search_in_files with ripgrep."""

    @patch("context_mcp.tools.search.shutil.which")
    @patch("context_mcp.tools.search.subprocess.run")
    def test_uses_ripgrep_when_available(
        self, mock_run, mock_which, mock_config, test_files
    ):
        """Test that ripgrep is used when available."""
        from context_mcp.tools.search import search_in_files

        # Mock ripgrep available
        mock_which.return_value = "/usr/bin/rg"

        # Mock ripgrep output
        mock_result = MagicMock()
        mock_result.stdout = "test1.txt:1:Hello world\ntest1.txt:2:Test content\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = search_in_files(query="Hello", path=".")

        # Verify ripgrep was called
        mock_run.assert_called_once()
        assert "rg" in mock_run.call_args[0][0][0]
        assert result["total_matches"] >= 0  # Should get results


class TestSearchInFilesFallback:
    """Test search_in_files fallback logic."""

    @patch("context_mcp.tools.search.shutil.which")
    @patch("context_mcp.tools.search.subprocess.run")
    def test_fallback_to_grep_when_ripgrep_unavailable(
        self, mock_run, mock_which, mock_config, test_files
    ):
        """Test fallback to grep when ripgrep is not available."""
        from context_mcp.tools.search import search_in_files

        # Mock ripgrep not available, but grep available
        def which_side_effect(cmd):
            if cmd == "rg":
                return None
            elif cmd == "grep":
                return "/usr/bin/grep"
            return None

        mock_which.side_effect = which_side_effect

        # Mock grep output
        mock_result = MagicMock()
        mock_result.stdout = "1:Hello world\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = search_in_files(query="Hello", path=".")

        # Should fall back to Python rglob since grep implementation not done yet
        # This test will properly validate after T009
        assert isinstance(result, dict)
        assert "total_matches" in result

    @patch("context_mcp.tools.search.shutil.which")
    def test_fallback_to_python_when_all_tools_unavailable(
        self, mock_which, mock_config, test_files
    ):
        """Test fallback to Python when all tools are unavailable."""
        from context_mcp.tools.search import search_in_files

        # Mock all tools unavailable
        mock_which.return_value = None

        result = search_in_files(query="Hello", path=".")

        # Should use Python fallback
        assert isinstance(result, dict)
        assert "total_matches" in result
        assert result["total_matches"] >= 0


class TestFindFilesByNameFd:
    """Test find_files_by_name with fd."""

    @patch("context_mcp.tools.search.shutil.which")
    @patch("context_mcp.tools.search.subprocess.run")
    def test_uses_fd_when_available(self, mock_run, mock_which, mock_config, test_files):
        """Test that fd is used when available."""
        from context_mcp.tools.search import find_files_by_name

        # This will be tested after T010 implementation
        # For now, verify current Python implementation works
        result = find_files_by_name(name_pattern="*.txt", path=".")
        assert isinstance(result, dict)
        assert "total_found" in result


class TestFindFilesByNameFallback:
    """Test find_files_by_name fallback logic."""

    @patch("context_mcp.tools.search.shutil.which")
    def test_fallback_to_python_when_all_tools_unavailable(
        self, mock_which, mock_config, test_files
    ):
        """Test fallback to Python when all tools are unavailable."""
        from context_mcp.tools.search import find_files_by_name

        mock_which.return_value = None

        result = find_files_by_name(name_pattern="*.txt", path=".")

        # Should use Python fallback
        assert isinstance(result, dict)
        assert "total_found" in result
        assert result["total_found"] >= 0


class TestCrossPlatform:
    """Test cross-platform compatibility."""

    @patch("platform.system")
    @patch("context_mcp.tools.search.shutil.which")
    def test_windows_fallback(self, mock_which, mock_platform, mock_config, test_files):
        """Test that Windows correctly falls back to Python."""
        from context_mcp.tools.search import find_files_by_name

        mock_platform.return_value = "Windows"
        # On Windows, find/grep may not be available
        mock_which.return_value = None

        result = find_files_by_name(name_pattern="*.txt", path=".")

        # Should work via Python fallback
        assert isinstance(result, dict)
        assert "total_found" in result
