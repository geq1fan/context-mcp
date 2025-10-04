# Modern CLI Tools: ripgrep, fd, and eza

## Overview

This document provides installation instructions and performance benchmarks for three modern command-line tools: ripgrep (rg), fd, and eza. These tools are written in Rust and offer significant improvements over traditional Unix utilities like grep, find, and ls.

## Installation Methods

### ripgrep (rg)

#### Windows
- **Chocolatey**: `choco install ripgrep`
- **Scoop**: `scoop install ripgrep`
- **Winget**: `winget install BurntSushi.ripgrep.MSVC`
- **Download**: [Official GitHub Releases](https://github.com/BurntSushi/ripgrep/releases)

#### Linux (Package Managers)
- **Ubuntu/Debian**: `sudo apt install ripgrep`
- **Fedora**: `sudo dnf install ripgrep`
- **Arch Linux**: `sudo pacman -S ripgrep`
- **openSUSE**: Available in Tumbleweed and Leap 15.1+

#### macOS
- **Homebrew**: `brew install ripgrep`

#### Cross-platform
- **Cargo (Rust)**: `cargo install ripgrep`

### fd

#### Windows
- **Scoop**: `scoop install fd`
- **Winget**: `winget install sharkdp.fd`
- **Download**: [Official GitHub Releases](https://github.com/sharkdp/fd/releases)

#### Linux
- **Ubuntu/Debian**: `sudo apt install fd-find`
- **Fedora**: `sudo dnf install fd-find`
- **Arch Linux**: `sudo pacman -S fd`

#### macOS
- **Homebrew**: `brew install fd`

#### Cross-platform
- **Cargo (Rust)**: `cargo install fd-find`

### eza

#### Windows
- **Winget**: `winget install eza-community.eza`
- **Scoop**: `scoop install eza`

#### Linux
- **Arch Linux**: Available in [extra] repository
- **Debian/Ubuntu**: Requires adding repository and GPG key
- **Fedora**: `sudo dnf install eza`
- **Void Linux**: Available in official repository
- **OpenSUSE**: Add openSUSE:Factory/eza repository

#### macOS
- **Homebrew**: `brew install eza`
- **MacPorts**: `port install eza`

#### Cross-platform
- **Cargo (Rust)**: `cargo install eza`

## Performance Benchmarks

### ripgrep vs grep

**Linux Kernel Source Tree Search Benchmark**:
- **ripgrep**: 0.082s (1.00x)
- **hypergrep**: 0.167s (2.04x)
- **git grep**: 0.273s (3.34x)
- **The Silver Searcher**: 0.443s (5.43x)
- **ugrep**: 0.639s (7.82x)

**Key Advantages**:
- Fastest grep-like tool
- Proper Unicode support
- Gitignore rule respecting
- First-class support on Windows, macOS, Linux

### fd vs find

**Performance Metrics**:
- Approximately 23x faster than `find -iregex`
- About 13x faster than `find -iname`
- Example: Searching jpg files
  - **fd**: 854.8 ms
  - **find**: 19.922 s

**Caveats**:
- Slower for simple file listing without pattern matching
- Git repositories: `git ls-files` is even faster

### eza vs ls

**Performance Comparison**:
- **ls is faster** in most scenarios
- macOS benchmark:
  - **ls**: 6.25 ms
  - **eza**: 15.19 ms (2.4x slower)
- Linux benchmark:
  - **ls**: 2-3x faster than eza

**Trade-offs**:
- eza offers enhanced visual features
- Prioritizes metadata display over raw speed

## Recommendations

1. **ripgrep**: Recommended for all text searching tasks
2. **fd**: Great for complex file search patterns
3. **eza**: Use for enhanced file listing, not for performance-critical tasks

## Resources
- [ripgrep GitHub](https://github.com/BurntSushi/ripgrep)
- [fd GitHub](https://github.com/sharkdp/fd)
- [eza GitHub](https://github.com/eza-community/eza)

## Benchmark Methodology
Benchmarks sourced from official GitHub repositories and independent performance testing. Always conduct your own tests for specific use cases.