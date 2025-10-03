"""Unit tests for navigation tool helper functions.

These tests verify the behavior of internal helper functions used by
read_project_context tool, including file discovery and response generation.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from agent_mcp.tools.navigation import _discover_context_file, _generate_response


@pytest.mark.unit
class TestDiscoverContextFile:
    """Unit tests for _discover_context_file helper function."""

    def test_discover_file_exists_and_readable(self, tmp_path):
        """Test happy path: file exists and is readable."""
        # Setup
        filename = "AGENTS.md"
        content = "# Test Content\nSome instructions..."
        file_path = tmp_path / filename
        file_path.write_text(content, encoding="utf-8")

        # Execute
        result = _discover_context_file(filename, tmp_path)

        # Verify
        assert result["filename"] == filename
        assert result["exists"] is True
        assert result["readable"] is True
        assert result["size_bytes"] == file_path.stat().st_size
        assert result["content"] == content
        assert result["error"] is None

    def test_discover_file_not_exists(self, tmp_path):
        """Test file does not exist."""
        # Setup
        filename = "AGENTS.md"
        # No file created

        # Execute
        result = _discover_context_file(filename, tmp_path)

        # Verify
        assert result["filename"] == filename
        assert result["exists"] is False
        assert result["readable"] is False
        assert result["size_bytes"] is None
        assert result["content"] is None
        assert result["error"] is None

    def test_discover_file_permission_denied(self, tmp_path):
        """Test PermissionError handling."""
        import sys
        if sys.platform == "win32":
            pytest.skip("Permission testing requires POSIX platform")

        # Setup
        filename = "AGENTS.md"
        file_path = tmp_path / filename
        file_path.write_text("# Protected", encoding="utf-8")
        file_path.chmod(0o000)  # Remove all permissions

        try:
            # Execute
            result = _discover_context_file(filename, tmp_path)

            # Verify
            assert result["filename"] == filename
            assert result["exists"] is True
            assert result["readable"] is False
            assert result["size_bytes"] is None
            assert result["content"] is None
            assert result["error"] is not None
            assert "Permission denied" in result["error"] or "permission" in result["error"].lower()
        finally:
            # Cleanup
            file_path.chmod(0o644)

    def test_discover_file_invalid_utf8(self, tmp_path):
        """Test UnicodeDecodeError handling."""
        # Setup
        filename = "CLAUDE.md"
        file_path = tmp_path / filename
        file_path.write_bytes(b"# Valid\n\xff\xfeInvalid UTF-8")

        # Execute
        result = _discover_context_file(filename, tmp_path)

        # Verify
        assert result["filename"] == filename
        assert result["exists"] is True
        assert result["readable"] is False
        assert result["size_bytes"] is None
        assert result["content"] is None
        assert result["error"] is not None
        assert "encoding" in result["error"].lower() or "decode" in result["error"].lower()

    def test_discover_file_path_validation(self, tmp_path):
        """Test PathValidator integration."""
        # Setup
        filename = "AGENTS.md"
        file_path = tmp_path / filename
        file_path.write_text("# Content", encoding="utf-8")

        # Mock PathValidator instance to raise exception
        with patch("agent_mcp.tools.navigation.PathValidator") as MockValidator:
            mock_instance = MagicMock()
            mock_instance.validate.side_effect = Exception("PATH_SECURITY_ERROR: Path outside root")
            MockValidator.return_value = mock_instance

            # Execute
            result = _discover_context_file(filename, tmp_path)

            # Verify security error is handled
            assert result["filename"] == filename
            assert result["readable"] is False
            assert result["error"] is not None
            assert "PATH_SECURITY_ERROR" in result["error"] or "outside root" in result["error"].lower()

    def test_discover_file_size_warning(self, tmp_path, caplog):
        """Test large file warning is logged."""
        import logging

        # Setup
        filename = "AGENTS.md"
        large_content = "X" * (1024 * 1024 + 500)  # >1MB
        file_path = tmp_path / filename
        file_path.write_text(large_content, encoding="utf-8")

        # Execute with log capturing
        with caplog.at_level(logging.WARNING):
            result = _discover_context_file(filename, tmp_path)

        # Verify file is still readable
        assert result["exists"] is True
        assert result["readable"] is True
        assert result["content"] == large_content

        # Verify warning was logged
        warning_found = any(
            "large" in record.message.lower() and filename in record.message
            for record in caplog.records
        )
        assert warning_found, "Expected warning log for large file"

    def test_discover_empty_file(self, tmp_path):
        """Test empty file (0 bytes) is handled correctly."""
        # Setup
        filename = "CLAUDE.md"
        file_path = tmp_path / filename
        file_path.write_text("", encoding="utf-8")

        # Execute
        result = _discover_context_file(filename, tmp_path)

        # Verify
        assert result["filename"] == filename
        assert result["exists"] is True
        assert result["readable"] is True
        assert result["size_bytes"] == 0
        assert result["content"] == ""
        assert result["error"] is None


@pytest.mark.unit
class TestGenerateResponse:
    """Unit tests for _generate_response helper function."""

    def test_generate_response_all_found(self):
        """Test response when all files are found (total_found=2)."""
        # Setup
        files = [
            {
                "filename": "AGENTS.md",
                "exists": True,
                "readable": True,
                "size_bytes": 100,
                "content": "# AGENTS",
                "error": None
            },
            {
                "filename": "CLAUDE.md",
                "exists": True,
                "readable": True,
                "size_bytes": 50,
                "content": "# CLAUDE",
                "error": None
            }
        ]

        # Execute
        result = _generate_response(files)

        # Verify
        assert result["files"] == files
        assert result["total_found"] == 2
        assert result["message"] == "Found 2 of 2 context files"

    def test_generate_response_partial(self):
        """Test response when some files are found (total_found=1)."""
        # Setup
        files = [
            {
                "filename": "AGENTS.md",
                "exists": True,
                "readable": True,
                "size_bytes": 100,
                "content": "# AGENTS",
                "error": None
            },
            {
                "filename": "CLAUDE.md",
                "exists": False,
                "readable": False,
                "size_bytes": None,
                "content": None,
                "error": None
            }
        ]

        # Execute
        result = _generate_response(files)

        # Verify
        assert result["files"] == files
        assert result["total_found"] == 1
        assert result["message"] == "Found 1 of 2 context files"

    def test_generate_response_none_found(self):
        """Test response when no files are found (total_found=0)."""
        # Setup
        files = [
            {
                "filename": "AGENTS.md",
                "exists": False,
                "readable": False,
                "size_bytes": None,
                "content": None,
                "error": None
            },
            {
                "filename": "CLAUDE.md",
                "exists": False,
                "readable": False,
                "size_bytes": None,
                "content": None,
                "error": None
            }
        ]

        # Execute
        result = _generate_response(files)

        # Verify
        assert result["files"] == files
        assert result["total_found"] == 0
        assert "No context files found" in result["message"]

    def test_generate_response_exists_not_readable(self):
        """Test response when files exist but are not readable (special message)."""
        # Setup
        files = [
            {
                "filename": "AGENTS.md",
                "exists": True,
                "readable": False,
                "size_bytes": None,
                "content": None,
                "error": "Permission denied"
            },
            {
                "filename": "CLAUDE.md",
                "exists": False,
                "readable": False,
                "size_bytes": None,
                "content": None,
                "error": None
            }
        ]

        # Execute
        result = _generate_response(files)

        # Verify
        assert result["files"] == files
        assert result["total_found"] == 0
        assert "exists but not readable" in result["message"]

    def test_generate_response_multiple_exist_not_readable(self):
        """Test response when multiple files exist but are not readable."""
        # Setup
        files = [
            {
                "filename": "AGENTS.md",
                "exists": True,
                "readable": False,
                "size_bytes": None,
                "content": None,
                "error": "Permission denied"
            },
            {
                "filename": "CLAUDE.md",
                "exists": True,
                "readable": False,
                "size_bytes": None,
                "content": None,
                "error": "Encoding error"
            }
        ]

        # Execute
        result = _generate_response(files)

        # Verify
        assert result["total_found"] == 0
        assert "exists but not readable" in result["message"]

    def test_generate_response_mixed_scenario(self):
        """Test response with mixed scenario: one readable, one not readable."""
        # Setup
        files = [
            {
                "filename": "AGENTS.md",
                "exists": True,
                "readable": True,
                "size_bytes": 100,
                "content": "# AGENTS",
                "error": None
            },
            {
                "filename": "CLAUDE.md",
                "exists": True,
                "readable": False,
                "size_bytes": None,
                "content": None,
                "error": "Encoding error"
            }
        ]

        # Execute
        result = _generate_response(files)

        # Verify
        assert result["total_found"] == 1
        # Should still mention some exist but not readable
        assert "1 of 2" in result["message"] or "exists but not readable" in result["message"]
