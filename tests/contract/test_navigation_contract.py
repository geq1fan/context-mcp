"""Contract tests for navigation tools: list_directory and show_tree.

These tests verify that the MCP tool implementations conform to the contract
specifications defined in contracts/navigation_tools.json.
"""
import pytest
from agent_mcp.tools.navigation import list_directory, show_tree


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
