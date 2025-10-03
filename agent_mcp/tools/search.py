"""Search tools: search_in_file, search_in_files, find_files_by_name, find_recently_modified_files.

Provides content search and file finding capabilities.
"""

import re
import subprocess
import shutil
import time
from pathlib import Path
from agent_mcp.config import config
from agent_mcp.validators.path_validator import PathValidator
from agent_mcp.utils.file_detector import assert_text_file
from agent_mcp.utils.logger import logger


# Initialize path validator
validator: PathValidator | None
if config:
    validator = PathValidator(config.root_path)
else:
    validator = None


def search_in_file(query: str, file_path: str, use_regex: bool = False) -> dict:
    """Search for text in a single file.

    Args:
        query: Search text or regex pattern
        file_path: File path relative to project root
        use_regex: Whether to treat query as regex

    Returns:
        dict with keys: matches (list), total_matches (int)
    """
    if config is None or validator is None:
        raise RuntimeError("Configuration not loaded")

    logger.info(f"search_in_file: query={query}, file={file_path}, regex={use_regex}")

    # Validate path
    abs_path = validator.validate(file_path)

    if not abs_path.exists():
        raise FileNotFoundError(f"FILE_NOT_FOUND: {file_path}")

    # Check if binary
    assert_text_file(abs_path)

    # Read file and search
    matches = []
    try:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip("\n")
                if use_regex:
                    try:
                        if re.search(query, line):
                            matches.append(
                                {"line_number": line_num, "line_content": line}
                            )
                    except re.error as e:
                        raise ValueError(f"INVALID_REGEX: {str(e)}")
                else:
                    if query in line:
                        matches.append({"line_number": line_num, "line_content": line})
    except PermissionError:
        raise PermissionError(f"PERMISSION_DENIED: Cannot read {file_path}")

    return {"matches": matches, "total_matches": len(matches)}


def search_in_files(
    query: str,
    file_pattern: str = "*",
    path: str = ".",
    use_regex: bool = False,
    exclude_query: str = "",
    timeout: int = 60,
) -> dict:
    """Search for text across multiple files.

    Args:
        query: Search text or regex pattern
        file_pattern: File name glob pattern
        path: Starting directory
        use_regex: Whether to treat query as regex
        exclude_query: Exclude matches containing this pattern
        timeout: Timeout in seconds

    Returns:
        dict with keys: matches (list), total_matches (int), files_searched (int), timed_out (bool)
    """
    if config is None or validator is None:
        raise RuntimeError("Configuration not loaded")

    logger.info(f"search_in_files: query={query}, pattern={file_pattern}, path={path}")

    # Validate path
    abs_path = validator.validate(path)

    if not abs_path.exists():
        raise FileNotFoundError(f"PATH_NOT_FOUND: {path}")

    # Use ripgrep if available, otherwise grep
    matches = []
    files_searched = 0
    timed_out = False
    start_time = time.time()

    try:
        search_root_rel = abs_path.relative_to(config.root_path)
    except ValueError:
        search_root_rel = Path(".")
    search_root_parts = tuple(
        part for part in search_root_rel.parts if part not in (".",)
    )

    # Try to use rg (ripgrep) first
    rg_cmd = shutil.which("rg")
    if rg_cmd:
        cmd = [rg_cmd, "--line-number", "--no-heading"]
        if use_regex:
            cmd.append("--regexp")
        else:
            cmd.append("--fixed-strings")

        if file_pattern != "*":
            cmd.extend(["--glob", file_pattern])

        cmd.append(query)
        cmd.append(str(abs_path))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(config.root_path),
                encoding="utf-8",
                errors="replace",
            )

            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                if exclude_query and exclude_query in line:
                    continue

                # Handle Windows paths with drive letters (e.g., C:\path:123:content)
                # Split only at the first two colons after the path
                # For Windows: "C:\path\file.txt:123:content" or ".\path\file.txt:123:content"
                # For Unix: "/path/file.txt:123:content"

                # Find the first colon that's not part of a drive letter
                colon_positions = []
                for i, char in enumerate(line):
                    if char == ":":
                        # Skip if it's a drive letter (position 1)
                        if i == 1 and len(line) > 2 and line[i + 1] in ("\\", "/"):
                            continue
                        colon_positions.append(i)

                if len(colon_positions) < 2:
                    continue

                file_str = line[: colon_positions[0]]
                line_num_str = line[colon_positions[0] + 1 : colon_positions[1]]
                line_content = line[colon_positions[1] + 1 :]

                try:
                    file_path = Path(file_str)
                    if not file_path.is_absolute():
                        normalized_parts = tuple(
                            part for part in file_path.parts if part not in (".",)
                        )
                        # Avoid duplicating the search root when ripgrep already returned a project-relative path
                        if (
                            search_root_parts
                            and normalized_parts[: len(search_root_parts)]
                            == search_root_parts
                        ):
                            file_path = (config.root_path / file_path).resolve()
                        else:
                            file_path = (abs_path / file_path).resolve()
                    else:
                        file_path = file_path.resolve()
                    file_rel = file_path.relative_to(config.root_path)

                    matches.append(
                        {
                            "file_path": str(file_rel).replace("\\", "/"),
                            "line_number": int(line_num_str),
                            "line_content": line_content,
                        }
                    )
                except (ValueError, IndexError):
                    # Skip malformed lines or paths outside root
                    continue

        except subprocess.TimeoutExpired:
            timed_out = True
    else:
        # Fallback: manual search
        for file in abs_path.rglob(file_pattern):
            if time.time() - start_time > timeout:
                timed_out = True
                break

            if file.is_file():
                try:
                    files_searched += 1
                    file_result = search_in_file(
                        query, str(file.relative_to(config.root_path)), use_regex
                    )
                    for match in file_result["matches"]:
                        if exclude_query and exclude_query in match["line_content"]:
                            continue
                        matches.append(
                            {
                                "file_path": str(file.relative_to(config.root_path)),
                                "line_number": match["line_number"],
                                "line_content": match["line_content"],
                            }
                        )
                except Exception:
                    continue

    return {
        "matches": matches,
        "total_matches": len(matches),
        "files_searched": files_searched,
        "timed_out": timed_out,
    }


def find_files_by_name(name_pattern: str, path: str = ".") -> dict:
    """Find files by name pattern (glob).

    Args:
        name_pattern: File name pattern with wildcards (* and ?)
        path: Starting directory

    Returns:
        dict with keys: files (list[str]), total_found (int)
    """
    if config is None or validator is None:
        raise RuntimeError("Configuration not loaded")

    logger.info(f"find_files_by_name: pattern={name_pattern}, path={path}")

    # Validate path
    abs_path = validator.validate(path)

    if not abs_path.exists():
        raise FileNotFoundError(f"PATH_NOT_FOUND: {path}")

    # Find matching files
    files = []
    for file in abs_path.rglob(name_pattern):
        if file.is_file():
            files.append(str(file.relative_to(config.root_path)))

    return {"files": files, "total_found": len(files)}


def find_recently_modified_files(
    hours_ago: int, path: str = ".", file_pattern: str = "*"
) -> dict:
    """Find files modified within the last N hours.

    Args:
        hours_ago: Number of hours to look back
        path: Starting directory
        file_pattern: File name pattern

    Returns:
        dict with keys: files (list[dict]), total_found (int)
    """
    if config is None or validator is None:
        raise RuntimeError("Configuration not loaded")

    logger.info(f"find_recently_modified_files: hours_ago={hours_ago}, path={path}")

    # Validate path
    abs_path = validator.validate(path)

    if not abs_path.exists():
        raise FileNotFoundError(f"PATH_NOT_FOUND: {path}")

    # Calculate cutoff time
    cutoff_time = time.time() - (hours_ago * 3600)

    # Find recently modified files
    files = []
    for file in abs_path.rglob(file_pattern):
        if file.is_file():
            try:
                mtime = file.stat().st_mtime
                if mtime >= cutoff_time:
                    files.append(
                        {
                            "path": str(file.relative_to(config.root_path)),
                            "mtime": mtime,
                        }
                    )
            except (OSError, PermissionError):
                continue

    # Sort by modification time (most recent first)
    from typing import cast

    files.sort(key=lambda f: cast(float, f["mtime"]), reverse=True)

    return {"files": files, "total_found": len(files)}
