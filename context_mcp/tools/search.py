"""Search tools: search_in_file, search_in_files, find_files_by_name, find_recently_modified_files.

Provides content search and file finding capabilities.
"""

import re
import subprocess
import shutil
import time
import platform
from pathlib import Path
from context_mcp.config import config
from context_mcp.validators.path_validator import PathValidator
from context_mcp.utils.file_detector import assert_text_file
from context_mcp.utils.logger import logger
from context_mcp.utils.tool_detector import ToolDetector


# Initialize path validator
validator: PathValidator | None
if config:
    validator = PathValidator(config.root_path)
else:
    validator = None

# Initialize tool detector
_tool_detector = ToolDetector()


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
        dict with keys: matches (list), total_matches (int), timed_out (bool)
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
        # ripgrep defaults to regex mode, only add -F for literal search
        if not use_regex:
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
                    # ripgrep with cwd=root_path returns paths relative to root_path
                    if not file_path.is_absolute():
                        file_path = (config.root_path / file_path).resolve()
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
                except (ValueError, IndexError) as e:
                    # Skip malformed lines or paths outside root
                    logger.info(f"Skip line due to {type(e).__name__}: {line[:100]}")
                    continue

        except subprocess.TimeoutExpired:
            timed_out = True
    # Try grep as fallback if ripgrep not available
    elif shutil.which("grep") and platform.system() != "Windows":
        # Use grep + find combination for Unix-like systems
        try:
            # First, find matching files
            if file_pattern != "*":
                find_cmd = ["find", str(abs_path), "-type", "f", "-name", file_pattern]
            else:
                find_cmd = ["find", str(abs_path), "-type", "f"]

            find_result = subprocess.run(
                find_cmd,
                capture_output=True,
                text=True,
                timeout=timeout // 2,  # Half timeout for find
                encoding="utf-8",
                errors="replace",
            )

            if find_result.returncode == 0:
                files_to_search = find_result.stdout.strip().split("\n")
                remaining_timeout = timeout - (timeout // 2)

                for file_str in files_to_search:
                    if time.time() - start_time > timeout:
                        timed_out = True
                        break

                    if not file_str.strip():
                        continue

                    # Build grep command
                    grep_cmd = ["grep", "-n"]  # -n for line numbers
                    if use_regex:
                        grep_cmd.append("-E")  # Extended regex
                    else:
                        grep_cmd.append("-F")  # Fixed string

                    grep_cmd.extend([query, file_str])

                    try:
                        grep_result = subprocess.run(
                            grep_cmd,
                            capture_output=True,
                            text=True,
                            timeout=min(5, remaining_timeout),
                            encoding="utf-8",
                            errors="replace",
                        )

                        # grep returns 0 if matches found, 1 if no matches, >1 for errors
                        if grep_result.returncode in (0, 1):
                            for line in grep_result.stdout.splitlines():
                                if not line.strip():
                                    continue
                                if exclude_query and exclude_query in line:
                                    continue

                                # Parse grep output: "line_number:line_content"
                                parts = line.split(":", 1)
                                if len(parts) == 2:
                                    try:
                                        line_num = int(parts[0])
                                        line_content = parts[1]

                                        file_path = Path(file_str)
                                        file_rel = file_path.relative_to(
                                            config.root_path
                                        )

                                        matches.append(
                                            {
                                                "file_path": str(file_rel).replace(
                                                    "\\", "/"
                                                ),
                                                "line_number": line_num,
                                                "line_content": line_content,
                                            }
                                        )
                                    except (ValueError, IndexError):
                                        continue

                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        continue

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # If grep fails, fall back to Python
            pass
    # Final fallback: manual Python search
    if not matches and not timed_out:
        # Fallback: manual search
        for file in abs_path.rglob(file_pattern):
            if time.time() - start_time > timeout:
                timed_out = True
                break

            if file.is_file():
                try:
                    file_result = search_in_file(
                        query, str(file.relative_to(config.root_path)), use_regex
                    )
                    for match in file_result["matches"]:
                        if exclude_query and exclude_query in match["line_content"]:
                            continue
                        matches.append(
                            {
                                "file_path": str(
                                    file.relative_to(config.root_path)
                                ).replace("\\", "/"),
                                "line_number": match["line_number"],
                                "line_content": match["line_content"],
                            }
                        )
                except Exception:
                    continue

    return {
        "matches": matches,
        "total_matches": len(matches),
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

    files = []

    # Try fd first if available
    if _tool_detector.has_fd:
        try:
            cmd = ["fd", "--type", "f", "--glob", name_pattern, str(abs_path)]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(config.root_path),
                encoding="utf-8",
                errors="replace",
            )

            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if not line.strip():
                        continue

                    try:
                        file_path = Path(line.strip())
                        if not file_path.is_absolute():
                            file_path = (abs_path / file_path).resolve()

                        file_rel = file_path.relative_to(config.root_path)
                        files.append(str(file_rel).replace("\\", "/"))
                    except (ValueError, OSError):
                        continue

                return {"files": files, "total_found": len(files)}

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # Fall through to next fallback
            pass

    # Try find as fallback on Unix-like systems
    if not files and shutil.which("find") and platform.system() != "Windows":
        try:
            cmd = ["find", str(abs_path), "-type", "f", "-name", name_pattern]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding="utf-8",
                errors="replace",
            )

            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if not line.strip():
                        continue

                    try:
                        file_path = Path(line.strip())
                        file_rel = file_path.relative_to(config.root_path)
                        files.append(str(file_rel).replace("\\", "/"))
                    except (ValueError, OSError):
                        continue

                return {"files": files, "total_found": len(files)}

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # Fall through to Python fallback
            pass

    # Final fallback: Python rglob
    for file in abs_path.rglob(name_pattern):
        if file.is_file():
            files.append(str(file.relative_to(config.root_path)).replace("\\", "/"))

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

    files = []

    # Try fd first (respects .gitignore automatically)
    if _tool_detector.has_fd:
        try:
            cmd = [
                "fd",
                "--type", "f",
                "--changed-within", f"{hours_ago}h",
                "--glob", file_pattern,
                str(abs_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(config.root_path),
                encoding="utf-8",
                errors="replace",
            )

            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if not line.strip():
                        continue

                    try:
                        file_path = Path(line.strip())
                        if not file_path.is_absolute():
                            file_path = (abs_path / file_path).resolve()

                        file_rel = file_path.relative_to(config.root_path)
                        mtime = file_path.stat().st_mtime

                        files.append(
                            {
                                "path": str(file_rel).replace("\\", "/"),
                                "mtime": mtime,
                            }
                        )
                    except (ValueError, OSError):
                        continue

                # Sort by modification time (most recent first)
                from typing import cast
                files.sort(key=lambda f: cast(float, f["mtime"]), reverse=True)
                return {"files": files, "total_found": len(files)}

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # Fall through to Python fallback
            pass

    for file in abs_path.rglob(file_pattern):
        if file.is_file():
            try:
                # Get path relative to root for exclusion check
                file_rel = file.relative_to(config.root_path)

                mtime = file.stat().st_mtime
                if mtime >= cutoff_time:
                    files.append(
                        {
                            "path": str(file_rel).replace("\\", "/"),
                            "mtime": mtime,
                        }
                    )
            except (OSError, PermissionError, ValueError):
                continue

    # Sort by modification time (most recent first)
    from typing import cast

    files.sort(key=lambda f: cast(float, f["mtime"]), reverse=True)

    return {"files": files, "total_found": len(files)}
