"""Unit tests for ToolDetector."""

import subprocess
from unittest.mock import patch, MagicMock
import pytest
import time


@pytest.fixture
def reset_singleton():
    """Reset ToolDetector singleton between tests."""
    from context_mcp.utils.tool_detector import ToolDetector

    # Reset singleton
    ToolDetector._instance = None
    yield
    # Clean up after test
    ToolDetector._instance = None


class TestToolDetectorSingleton:
    """Test ToolDetector singleton behavior."""

    def test_singleton_returns_same_instance(self, reset_singleton):
        """Test that ToolDetector returns the same instance."""
        from context_mcp.utils.tool_detector import ToolDetector

        detector1 = ToolDetector()
        detector2 = ToolDetector()

        assert detector1 is detector2
        assert id(detector1) == id(detector2)

    def test_singleton_state_persists(self, reset_singleton):
        """Test that singleton state persists across calls."""
        from context_mcp.utils.tool_detector import ToolDetector

        detector1 = ToolDetector()
        has_rg_1 = detector1.has_ripgrep
        has_fd_1 = detector1.has_fd

        detector2 = ToolDetector()
        assert detector2.has_ripgrep == has_rg_1
        assert detector2.has_fd == has_fd_1


class TestToolDetectorRipgrep:
    """Test ripgrep detection."""

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_ripgrep_available(self, mock_run, mock_which, reset_singleton):
        """Test detection when ripgrep is available."""
        from context_mcp.utils.tool_detector import ToolDetector

        mock_which.return_value = "/usr/bin/rg"
        mock_run.return_value = MagicMock(returncode=0)

        detector = ToolDetector()
        assert detector.has_ripgrep is True

    @patch("shutil.which")
    def test_ripgrep_not_in_path(self, mock_which, reset_singleton):
        """Test detection when ripgrep is not in PATH."""
        from context_mcp.utils.tool_detector import ToolDetector

        mock_which.return_value = None

        detector = ToolDetector()
        assert detector.has_ripgrep is False

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_ripgrep_exists_but_not_executable(
        self, mock_run, mock_which, reset_singleton
    ):
        """Test detection when ripgrep exists but version check fails."""
        from context_mcp.utils.tool_detector import ToolDetector

        mock_which.return_value = "/usr/bin/rg"
        mock_run.side_effect = FileNotFoundError

        detector = ToolDetector()
        assert detector.has_ripgrep is False

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_ripgrep_timeout(self, mock_run, mock_which, reset_singleton):
        """Test detection when ripgrep version check times out."""
        from context_mcp.utils.tool_detector import ToolDetector

        mock_which.return_value = "/usr/bin/rg"
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="rg", timeout=5)

        detector = ToolDetector()
        assert detector.has_ripgrep is False

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_ripgrep_non_zero_exit(self, mock_run, mock_which, reset_singleton):
        """Test detection when ripgrep returns non-zero exit code."""
        from context_mcp.utils.tool_detector import ToolDetector

        mock_which.return_value = "/usr/bin/rg"
        mock_run.return_value = MagicMock(returncode=1)

        detector = ToolDetector()
        assert detector.has_ripgrep is False


class TestToolDetectorFd:
    """Test fd detection."""

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_fd_available(self, mock_run, mock_which, reset_singleton):
        """Test detection when fd is available."""
        from context_mcp.utils.tool_detector import ToolDetector

        # Mock fd detection
        def which_side_effect(tool):
            if tool == "rg":
                return None
            elif tool == "fd":
                return "/usr/bin/fd"
            return None

        mock_which.side_effect = which_side_effect
        mock_run.return_value = MagicMock(returncode=0)

        detector = ToolDetector()
        assert detector.has_fd is True

    @patch("shutil.which")
    def test_fd_not_in_path(self, mock_which, reset_singleton):
        """Test detection when fd is not in PATH."""
        from context_mcp.utils.tool_detector import ToolDetector

        mock_which.return_value = None

        detector = ToolDetector()
        assert detector.has_fd is False


class TestToolDetectorPerformance:
    """Test ToolDetector performance."""

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_detection_performance(self, mock_run, mock_which, reset_singleton):
        """Test that detection completes within 100ms."""
        from context_mcp.utils.tool_detector import ToolDetector

        mock_which.return_value = "/usr/bin/rg"
        mock_run.return_value = MagicMock(returncode=0)

        start = time.perf_counter()
        ToolDetector()
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

        # Should complete well under 100ms (mocked operations are instant)
        assert elapsed < 100
