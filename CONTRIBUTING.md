# Contributing to Context MCP

Thank you for your interest in contributing to Context MCP! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Project Structure](#project-structure)

## Code of Conduct

This project adheres to a simple code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Report unacceptable behavior to the project maintainers

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/context-mcp.git
   cd context-mcp
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/geq1fan/context-mcp.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- uv (recommended) or pip
- Git
- Optional: ripgrep for faster searches

### Installation

```bash
# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"
```

### Environment Setup

Create a `.env` file for testing:

```bash
cp .env.example .env
# Edit .env and set PROJECT_ROOT to a test directory
```

### Running the Server Locally

```bash
PROJECT_ROOT=/path/to/test/project uv run python -m agent_mcp.server
```

## Making Changes

### Branch Naming Convention

- `feature/your-feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(search): add regex support to search_in_files

- Implement regex pattern matching
- Add use_regex parameter
- Update tests and documentation

Closes #123
```

```
fix(security): prevent directory traversal in path validation

- Use Path.resolve() to normalize paths
- Add security tests
- Update documentation

Fixes #456
```

## Testing

### Running Tests

```bash
# Run all tests
PROJECT_ROOT=$(pwd) uv run pytest

# Run specific test categories
PROJECT_ROOT=$(pwd) uv run pytest tests/contract/  # Contract tests
PROJECT_ROOT=$(pwd) uv run pytest tests/integration/  # Integration tests
PROJECT_ROOT=$(pwd) uv run pytest tests/unit/  # Unit tests

# Run with coverage
PROJECT_ROOT=$(pwd) uv run pytest --cov=agent_mcp --cov-report=html
```

### Writing Tests

All new features must include tests:

1. **Contract Tests** (`tests/contract/`): Verify MCP protocol compliance
   - Test input/output schemas
   - Validate error codes
   - Ensure contract consistency

2. **Integration Tests** (`tests/integration/`): Test end-to-end workflows
   - Test complete user scenarios
   - Verify tool interactions
   - Test edge cases

3. **Unit Tests** (`tests/unit/`): Test individual components
   - Test functions in isolation
   - Mock external dependencies
   - Cover edge cases

### Test Requirements

- All tests must pass before submitting PR
- Maintain or improve code coverage (currently 99.2%)
- Add tests for new features
- Add tests for bug fixes

## Submitting Changes

### Before Submitting

1. **Update tests**: Ensure all tests pass
2. **Update documentation**: Update README, docstrings, etc.
3. **Check code style**: Follow project conventions
4. **Run linters**: Ensure code quality
5. **Update CHANGELOG.md**: Document your changes

### Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your changes**:
   ```bash
   git push origin your-branch-name
   ```

3. **Create Pull Request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what changed and why
   - Link to related issues (if applicable)
   - Screenshots/examples (if applicable)

4. **PR Template** should include:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] All tests pass
   - [ ] New tests added
   - [ ] Coverage maintained/improved

   ## Checklist
   - [ ] Code follows project style
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] No breaking changes (or documented)
   ```

5. **Review Process**:
   - Maintainers will review your PR
   - Address feedback and update PR
   - Once approved, changes will be merged

## Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use type hints for function signatures
- Write clear docstrings (Google style)
- Maximum line length: 100 characters (flexible for readability)

### Example Function

```python
def search_in_file(
    query: str,
    file_path: str,
    use_regex: bool = False
) -> dict:
    """Search for text in a single file.

    Args:
        query: Search text or regex pattern
        file_path: File path relative to project root
        use_regex: Whether to treat query as regex

    Returns:
        dict with keys: matches (list), total_matches (int)

    Raises:
        FileNotFoundError: If file does not exist
        BinaryFileError: If file is binary
        PathSecurityError: If path is outside project root
    """
    # Implementation
```

### Documentation Style

- Use clear, concise language
- Provide examples where helpful
- Keep documentation up-to-date with code changes
- Use proper markdown formatting

## Project Structure

Understanding the project structure:

```
agent_mcp/
├── __init__.py          # Data models and exceptions
├── server.py            # FastMCP server entry point
├── config.py            # Environment configuration
├── tools/               # MCP tool implementations
│   ├── navigation.py    # Directory listing and tree
│   ├── search.py        # Search and find tools
│   └── read.py          # File reading tools
├── validators/          # Security validators
│   └── path_validator.py
└── utils/               # Utility functions
    ├── file_detector.py # Binary file detection
    └── logger.py        # Logging configuration

tests/
├── contract/            # MCP contract tests
├── integration/         # End-to-end tests
└── unit/                # Component tests

specs/
└── 001-agent-mcp-md/   # Design documentation
    ├── spec.md          # Feature specification
    ├── plan.md          # Implementation plan
    ├── contracts/       # MCP tool contracts (JSON Schema)
    └── ...
```

### Key Principles

1. **Simplicity**: Keep code simple and readable
2. **Security**: Follow security best practices
3. **Testing**: Write comprehensive tests
4. **Documentation**: Document public APIs
5. **Constitution**: Follow `.specify/memory/constitution.md` principles

## Development Workflow

### Adding a New MCP Tool

1. **Define contract** in `specs/001-agent-mcp-md/contracts/`
2. **Write contract test** in `tests/contract/`
3. **Implement function** in appropriate `tools/*.py` file
4. **Register in server.py** with `@mcp.tool()` decorator
5. **Write integration tests** in `tests/integration/`
6. **Update documentation** (README, quickstart.md)

### Fixing a Bug

1. **Create failing test** that reproduces the bug
2. **Fix the bug** in the code
3. **Verify test passes**
4. **Add regression test** if needed
5. **Update documentation** if behavior changed

## Questions?

- Open an issue for questions
- Check existing issues and PRs
- Review documentation in `/specs` directory

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- GitHub contributors list
- Release notes (for significant contributions)

Thank you for contributing to Context MCP! 🎉
