"""
Documentation generator for MCP tools.

Generates Markdown documentation with embedded JSON Schema blocks.
"""

from typing import Dict, List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import json
from datetime import datetime

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def load_template():
    """Load Jinja2 template for tool documentation."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
    return env.get_template("tool_guide.md.j2")


def generate_tool_section(tool_metadata: dict) -> str:
    """
    Generate Markdown section for a single tool.

    Args:
        tool_metadata: Dict with name, description, input_schema, examples, return_format

    Returns:
        Markdown string for the tool section
    """
    section = f"### {tool_metadata['name']}\n"
    section += f"**Purpose**: {tool_metadata['description']}\n\n"

    section += "**Parameters**:\n"
    section += "```json\n"
    section += json.dumps(tool_metadata["input_schema"], indent=2)
    section += "\n```\n\n"

    if tool_metadata.get("examples"):
        section += "**Examples**:\n"
        for example in tool_metadata["examples"]:
            section += "```python\n"
            section += example.strip()
            section += "\n```\n"
        section += "\n"

    if tool_metadata.get("return_format"):
        section += f"**Returns**: {tool_metadata['return_format']}\n"

    section += "\n---\n"
    return section


def generate_category_section(category_name: str, tools: List[dict]) -> str:
    """
    Generate Markdown section for a tool category.

    Args:
        category_name: Category name (e.g., "Navigation")
        tools: List of tool metadata dicts

    Returns:
        Markdown string for the category section
    """
    section = f"## {category_name} Tools ({len(tools)})\n\n"
    for tool in tools:
        section += generate_tool_section(tool)
    return section


def render_document(
    tools_by_category: Dict[str, List[dict]],
    total_tools: int,
    filtered_count: int,
    filter_applied: bool = False,
    filtered_tools: str = "",
) -> str:
    """
    Render complete documentation using Jinja2 template.

    Args:
        tools_by_category: Dict mapping category names to tool lists
        total_tools: Total number of tools in the system
        filtered_count: Number of tools after filtering
        filter_applied: Whether filtering was applied
        filtered_tools: Comma-separated list of filtered tool names

    Returns:
        Complete Markdown document string
    """
    template = load_template()
    return template.render(
        generation_date=datetime.now().strftime("%Y-%m-%d"),
        tool_count=filtered_count,
        total_tools=total_tools,
        filter_applied=filter_applied,
        filtered_tools=filtered_tools,
        tools_by_category=tools_by_category,
    )


def calculate_doc_size(content: str) -> int:
    """Calculate document size in bytes (UTF-8 encoded)."""
    return len(content.encode("utf-8"))
