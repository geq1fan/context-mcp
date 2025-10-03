"""Unit tests for configuration loading and validation."""
import pytest
import os
from pathlib import Path
from agent_mcp.config import ProjectConfig, load_config


class TestProjectConfig:
    """Unit tests for ProjectConfig dataclass."""

    def test_valid_config_creation(self, tmp_path):
        """Test creating valid ProjectConfig."""
        config = ProjectConfig(
            root_path=tmp_path,
            search_timeout=30,
            log_retention_days=5
        )

        assert config.root_path == tmp_path
        assert config.search_timeout == 30
        assert config.log_retention_days == 5

    def test_config_with_defaults(self, tmp_path):
        """Test that defaults are applied correctly."""
        config = ProjectConfig(root_path=tmp_path)

        assert config.search_timeout == 60
        assert config.log_retention_days == 7

    def test_config_is_frozen(self, tmp_path):
        """Test that ProjectConfig is immutable (frozen=True)."""
        config = ProjectConfig(root_path=tmp_path)

        with pytest.raises(Exception):  # FrozenInstanceError
            config.search_timeout = 120

    def test_validation_fails_for_nonexistent_root(self, tmp_path):
        """Test that validation fails if root_path doesn't exist."""
        nonexistent = tmp_path / "nonexistent_dir"

        with pytest.raises(ValueError) as exc_info:
            ProjectConfig(root_path=nonexistent)

        assert "does not exist" in str(exc_info.value)

    def test_validation_fails_for_file_as_root(self, tmp_path):
        """Test that validation fails if root_path is a file."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test")

        with pytest.raises(ValueError) as exc_info:
            ProjectConfig(root_path=file_path)

        assert "not a directory" in str(exc_info.value)

    def test_validation_fails_for_negative_timeout(self, tmp_path):
        """Test that validation fails for negative timeout."""
        with pytest.raises(ValueError) as exc_info:
            ProjectConfig(root_path=tmp_path, search_timeout=-10)

        assert "must be positive" in str(exc_info.value)

    def test_validation_fails_for_zero_timeout(self, tmp_path):
        """Test that validation fails for zero timeout."""
        with pytest.raises(ValueError) as exc_info:
            ProjectConfig(root_path=tmp_path, search_timeout=0)

        assert "must be positive" in str(exc_info.value)

    def test_validation_fails_for_zero_retention_days(self, tmp_path):
        """Test that validation fails for zero retention days."""
        with pytest.raises(ValueError) as exc_info:
            ProjectConfig(root_path=tmp_path, log_retention_days=0)

        assert ">= 1" in str(exc_info.value)


class TestLoadConfig:
    """Unit tests for load_config() function."""

    def test_load_config_with_valid_env(self, tmp_path, monkeypatch):
        """Test loading config from environment variables."""
        monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
        monkeypatch.setenv("SEARCH_TIMEOUT", "30")

        config = load_config()

        assert config.root_path == tmp_path
        assert config.search_timeout == 30

    def test_load_config_with_default_timeout(self, tmp_path, monkeypatch):
        """Test that SEARCH_TIMEOUT defaults to 60."""
        monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
        monkeypatch.delenv("SEARCH_TIMEOUT", raising=False)

        config = load_config()

        assert config.search_timeout == 60

    def test_load_config_fails_without_project_root(self, monkeypatch):
        """Test that load_config fails if PROJECT_ROOT is not set."""
        monkeypatch.delenv("PROJECT_ROOT", raising=False)

        with pytest.raises(ValueError) as exc_info:
            load_config()

        assert "PROJECT_ROOT" in str(exc_info.value)
        assert "required" in str(exc_info.value)

    def test_load_config_fails_with_invalid_timeout(self, tmp_path, monkeypatch):
        """Test that load_config fails if SEARCH_TIMEOUT is not an integer."""
        monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
        monkeypatch.setenv("SEARCH_TIMEOUT", "not_a_number")

        with pytest.raises(ValueError) as exc_info:
            load_config()

        assert "SEARCH_TIMEOUT" in str(exc_info.value)
        assert "integer" in str(exc_info.value)

    def test_load_config_resolves_relative_path(self, tmp_path, monkeypatch):
        """Test that relative PROJECT_ROOT is resolved to absolute."""
        # Change to tmp_path directory
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            monkeypatch.setenv("PROJECT_ROOT", ".")

            config = load_config()

            assert config.root_path.is_absolute()
            assert config.root_path == tmp_path
        finally:
            os.chdir(orig_cwd)

    def test_load_config_normalizes_path(self, tmp_path, monkeypatch):
        """Test that PROJECT_ROOT with .. is normalized."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Set path with ..
        path_with_dots = str(subdir / "..")
        monkeypatch.setenv("PROJECT_ROOT", path_with_dots)

        config = load_config()

        # Should resolve to tmp_path
        assert config.root_path == tmp_path
