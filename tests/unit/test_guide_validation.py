"""Unit tests for guide tool name validation logic."""

import pytest
from context_mcp.tools.guide import _validate_and_filter_tools


class TestToolNameNormalization:
    """Test tool name normalization and server prefix stripping."""

    def test_standard_tool_names(self):
        """Standard tool names should work without modification."""
        all_schemas = {
            "list_directory": {},
            "show_tree": {},
            "read_files": {},
        }

        tools, warnings, invalid = _validate_and_filter_tools(
            ["list_directory", "show_tree"], all_schemas
        )

        assert tools == {"list_directory", "show_tree"}
        assert warnings == []
        assert invalid == []


    def test_all_invalid_tools(self):
        """All invalid tool names should generate appropriate warnings."""
        all_schemas = {
            "list_directory": {},
            "show_tree": {},
        }

        tools, warnings, invalid = _validate_and_filter_tools(
            ["fake_tool_1", "fake_tool_2"], all_schemas
        )

        assert tools == set()
        assert len(warnings) == 1
        assert "fake_tool_1" in warnings[0]
        assert "fake_tool_2" in warnings[0]
        assert set(invalid) == {"fake_tool_1", "fake_tool_2"}

    def test_none_tool_names_returns_all(self):
        """None tool_names should return all available tools."""
        all_schemas = {
            "list_directory": {},
            "show_tree": {},
            "read_files": {},
        }

        tools, warnings, invalid = _validate_and_filter_tools(None, all_schemas)

        assert tools == {"list_directory", "show_tree", "read_files"}
        assert warnings == []
        assert invalid == []

    def test_empty_tool_names_list(self):
        """Empty tool_names list should return empty set."""
        all_schemas = {
            "list_directory": {},
            "show_tree": {},
        }

        tools, warnings, invalid = _validate_and_filter_tools([], all_schemas)

        assert tools == set()
        assert warnings == []
        assert invalid == []


    def test_case_sensitivity(self):
        """Tool name matching should be case-sensitive."""
        all_schemas = {
            "list_directory": {},
            "show_tree": {},
        }

        tools, warnings, invalid = _validate_and_filter_tools(
            ["mcp_List_Directory", "MCP_SHOW_TREE"], all_schemas
        )

        # Case mismatch should not match
        assert tools == set()
        assert len(warnings) == 1
        assert len(invalid) == 2


class TestWarningMessages:
    """Test warning message generation."""

    def test_single_invalid_tool_message(self):
        """Single invalid tool should use singular form."""
        all_schemas = {"list_directory": {}}

        _, warnings, _ = _validate_and_filter_tools(["fake_tool"], all_schemas)

        assert len(warnings) == 1
        assert warnings[0].startswith("Tool")
        assert "not found" in warnings[0].lower()

    def test_multiple_invalid_tools_message(self):
        """Multiple invalid tools should use plural form."""
        all_schemas = {"list_directory": {}}

        _, warnings, _ = _validate_and_filter_tools(
            ["fake_tool_1", "fake_tool_2"], all_schemas
        )

        assert len(warnings) == 1
        assert warnings[0].startswith("Tools")
        assert "not found" in warnings[0].lower()

    def test_warning_includes_available_tools(self):
        """Warning should list available tools."""
        all_schemas = {
            "list_directory": {},
            "show_tree": {},
        }

        _, warnings, _ = _validate_and_filter_tools(["fake_tool"], all_schemas)

        assert len(warnings) == 1
        assert "list_directory" in warnings[0]
        assert "show_tree" in warnings[0]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_duplicate_tool_names(self):
        """Duplicate tool names should be deduplicated."""
        all_schemas = {"list_directory": {}}

        tools, warnings, invalid = _validate_and_filter_tools(
            ["list_directory", "list_directory"], all_schemas
        )

        assert tools == {"list_directory"}
        assert warnings == []
        assert invalid == []

    def test_whitespace_in_tool_names(self):
        """Tool names with whitespace should not match."""
        all_schemas = {"list_directory": {}}

        tools, warnings, invalid = _validate_and_filter_tools(
            [" list_directory ", "list_directory"], all_schemas
        )

        # Only exact match should work
        assert tools == {"list_directory"}
        assert len(invalid) == 1
        assert " list_directory " in invalid

    def test_empty_string_tool_name(self):
        """Empty string tool name should be handled gracefully."""
        all_schemas = {"list_directory": {}}

        tools, warnings, invalid = _validate_and_filter_tools([""], all_schemas)

        assert tools == set()
        assert len(invalid) == 1
        assert "" in invalid

