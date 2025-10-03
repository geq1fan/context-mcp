"""Unit tests for binary file detector."""
import pytest
from pathlib import Path
from agent_mcp.utils.file_detector import is_binary_file, assert_text_file, BinaryFileError


class TestBinaryFileDetector:
    """Unit tests for binary file detection."""

    def test_detect_text_file(self, tmp_path):
        """Test that text files are detected as non-binary."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("Hello, World!\nThis is a text file.", encoding='utf-8')

        assert is_binary_file(text_file) == False

    def test_detect_binary_file_with_null_bytes(self, tmp_path):
        """Test that files with NULL bytes are detected as binary."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03\x04\x05')

        assert is_binary_file(binary_file) == True

    def test_detect_utf8_file(self, tmp_path):
        """Test that UTF-8 files are detected as text."""
        utf8_file = tmp_path / "test_utf8.txt"
        utf8_file.write_text("Hello 世界! 🌍", encoding='utf-8')

        assert is_binary_file(utf8_file) == False

    def test_detect_python_source_file(self, tmp_path):
        """Test that Python source files are detected as text."""
        py_file = tmp_path / "test.py"
        py_file.write_text("#!/usr/bin/env python3\nimport os\nprint('hello')\n", encoding='utf-8')

        assert is_binary_file(py_file) == False

    def test_detect_json_file(self, tmp_path):
        """Test that JSON files are detected as text."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value", "number": 123}', encoding='utf-8')

        assert is_binary_file(json_file) == False

    def test_detect_empty_file(self, tmp_path):
        """Test that empty files are detected as text."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        assert is_binary_file(empty_file) == False

    def test_assert_text_file_passes_for_text(self, tmp_path):
        """Test that assert_text_file passes for text files."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("This is text")

        # Should not raise
        assert_text_file(text_file)

    def test_assert_text_file_raises_for_binary(self, tmp_path):
        """Test that assert_text_file raises for binary files."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b'\x00\x01\x02')

        with pytest.raises(BinaryFileError) as exc_info:
            assert_text_file(binary_file)

        error = exc_info.value
        assert error.file_path == str(binary_file)
        assert "BINARY_FILE_ERROR" in str(error)

    def test_binary_detection_with_custom_chunk_size(self, tmp_path):
        """Test binary detection with custom chunk size."""
        # Create file with NULL byte after 2000 bytes
        binary_file = tmp_path / "late_null.bin"
        content = b'a' * 2000 + b'\x00' + b'b' * 100
        binary_file.write_bytes(content)

        # Default chunk size (1024) won't catch the NULL byte
        assert is_binary_file(binary_file, chunk_size=1024) == False

        # Larger chunk size will catch it
        assert is_binary_file(binary_file, chunk_size=4096) == True

    def test_is_binary_file_handles_nonexistent_file(self, tmp_path):
        """Test that is_binary_file returns False for nonexistent files."""
        nonexistent = tmp_path / "nonexistent.txt"

        # Should return False (not binary) and let actual read operation fail
        assert is_binary_file(nonexistent) == False
