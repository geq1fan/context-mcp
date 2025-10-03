# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Model

Context MCP is designed with security as a core principle:

### Read-Only Operations

- ✅ **No Write Operations**: The server cannot create, modify, or delete files
- ✅ **No Code Execution**: The server does not execute user code
- ✅ **No Network Operations**: The server does not make external network requests

### Path Security

- ✅ **Path Validation**: All file paths are validated and restricted to `PROJECT_ROOT`
- ✅ **Directory Traversal Protection**: Uses `Path.resolve()` to prevent `../` attacks
- ✅ **Absolute Path Enforcement**: Relative paths are resolved to absolute paths

### File Access Control

- ✅ **Binary File Protection**: Automatically detects and rejects binary files
- ✅ **Permission Respect**: Honors filesystem permissions and returns clear errors
- ✅ **No Privileged Operations**: Runs with the same permissions as the calling process

### Configuration Security

- ✅ **Environment-Based Config**: Sensitive configuration via environment variables
- ✅ **No Hardcoded Secrets**: No credentials or secrets in code
- ✅ **Minimal Permissions**: Requires only read access to configured project

## Known Limitations

### By Design

1. **Read-Only Access**: Cannot modify project files (this is intentional)
2. **Single Project**: Each instance serves one project directory
3. **Local Filesystem Only**: No remote filesystem support
4. **Text Files Only**: Binary files are rejected for safety

### Potential Risks

1. **Information Disclosure**: Can read any text file within `PROJECT_ROOT`
   - **Mitigation**: Carefully configure `PROJECT_ROOT` to exclude sensitive directories
   - **Recommendation**: Do not point `PROJECT_ROOT` to system directories or home directories

2. **Log File Exposure**: Logs may contain file paths and search queries
   - **Mitigation**: Logs are stored locally with 7-day retention
   - **Recommendation**: Review `agent_mcp.log` location and permissions

3. **Search Performance**: Complex searches may consume CPU
   - **Mitigation**: Configurable timeout (default 60 seconds)
   - **Recommendation**: Set appropriate `SEARCH_TIMEOUT` for your environment

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### How to Report

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please report security issues to:

📧 **Email**: context-mcp-security@example.com

### What to Include

Please include the following information:

1. **Description**: Clear description of the vulnerability
2. **Impact**: Potential impact and attack scenario
3. **Reproduction**: Step-by-step instructions to reproduce
4. **Environment**: OS, Python version, Agent MCP version
5. **Proposed Fix**: If you have suggestions (optional)

### Example Report Format

```
Subject: [SECURITY] Brief description of vulnerability

Vulnerability Type: [e.g., Path Traversal, Information Disclosure]

Description:
[Detailed description of the vulnerability]

Impact:
[What an attacker could do]

Steps to Reproduce:
1. Configure context-mcp with...
2. Send MCP request...
3. Observe...

Environment:
- OS: Ubuntu 22.04
- Python: 3.11.5
- context-mcp: 0.1.0

Proposed Fix:
[Optional suggestions]
```

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Status Update**: Every week until resolved
- **Fix Release**: Depends on severity (see below)

### Severity Levels

| Severity | Response Time | Fix Release |
|----------|---------------|-------------|
| Critical | 24 hours | 1-3 days |
| High | 3 days | 1 week |
| Medium | 1 week | 2 weeks |
| Low | 2 weeks | Next release |

## Security Best Practices

### For Users

1. **Restrict PROJECT_ROOT**:
   ```json
   {
     "env": {
       "PROJECT_ROOT": "/path/to/specific/project"  // Not "/" or "~"
     }
   }
   ```

2. **Review Permissions**:
   - Ensure Claude Desktop runs with minimal necessary permissions
   - Do not run as administrator/root

3. **Monitor Logs**:
   - Review `agent_mcp.log` periodically
   - Check for unexpected file access patterns

4. **Exclude Sensitive Directories**:
   - Do not include directories with secrets, keys, or credentials
   - Use `.gitignore` patterns as guidance

5. **Update Regularly**:
   - Keep context-mcp updated to latest version
   - Monitor security advisories

### For Developers

1. **Path Validation**:
   - Always use `PathValidator.validate()` before file operations
   - Never bypass security checks

2. **Input Sanitization**:
   - Validate all user inputs
   - Use type hints and runtime checks

3. **Error Messages**:
   - Do not expose sensitive paths in error messages
   - Log detailed errors, return sanitized messages to clients

4. **Testing**:
   - Include security tests in all PRs
   - Test path traversal scenarios
   - Test permission boundaries

5. **Dependencies**:
   - Keep dependencies updated
   - Review security advisories for dependencies

## Security Checklist

Before deploying context-mcp:

- [ ] `PROJECT_ROOT` points to a specific project directory
- [ ] `PROJECT_ROOT` does not contain sensitive credentials
- [ ] File permissions properly restrict access
- [ ] Log location is secure and monitored
- [ ] Running with minimal necessary permissions
- [ ] Latest version of context-mcp installed
- [ ] Dependencies are up to date
- [ ] Configuration reviewed for security issues

## Disclosure Policy

When a security vulnerability is fixed:

1. **Private Notification**: Reporters are notified privately
2. **Security Advisory**: Published on GitHub Security Advisories
3. **Patch Release**: New version released with fix
4. **Public Disclosure**: After patch is available (typically 7 days)
5. **Credit**: Reporter credited (if desired)

## Security Updates

Subscribe to security updates:

- **GitHub Watch**: Watch this repository for security advisories
- **Release Notes**: Check [CHANGELOG.md](CHANGELOG.md) for security fixes
- **Mailing List**: [Coming soon]

## Contact

For security concerns:
- **Email**: context-mcp-security@example.com
- **GPG Key**: [If available]

For general questions:
- **GitHub Issues**: [Non-security issues only]
- **Discussions**: [For general security questions]

---

Last Updated: 2025-10-03
Version: 1.0
