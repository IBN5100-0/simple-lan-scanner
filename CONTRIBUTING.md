# Contributing to Simple LAN Scanner

First off, thank you for considering contributing to Simple LAN Scanner! It's people like you that make Simple LAN Scanner such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Style Guides](#style-guides)
  - [Git Commit Messages](#git-commit-messages)
  - [Python Style Guide](#python-style-guide)
  - [Documentation Style Guide](#documentation-style-guide)
- [Testing](#testing)
- [Project Structure](#project-structure)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up your development environment (see [Development Setup](#development-setup))
4. Create a branch for your changes
5. Make your changes
6. Run tests to ensure everything works
7. Commit your changes
8. Push to your fork
9. Submit a pull request

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

**Bug Report Template:**

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows 10, Ubuntu 22.04]
 - Python Version: [e.g. 3.9.7]
 - nmap Version: [e.g. 7.92]
 - Simple LAN Scanner Version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Provide specific examples** to demonstrate the steps
- **Describe the current behavior** and **explain which behavior you expected to see instead**
- **Explain why this enhancement would be useful**

### Your First Code Contribution

Unsure where to begin contributing? You can start by looking through these issues:

- Issues labeled `good first issue` - issues which should only require a few lines of code
- Issues labeled `help wanted` - issues which should be a bit more involved than `good first issue` issues

### Pull Requests

Please follow these steps for sending us a pull request:

1. Follow all instructions in [the template](.github/pull_request_template.md)
2. Follow the [style guides](#style-guides)
3. After you submit your pull request, verify that all status checks are passing

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/IBN5100-0/simple-lan-scanner.git
   cd simple-lan-scanner
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .[dev]
   ```

4. **Install pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

5. **Verify setup**
   ```bash
   # Run tests
   pytest
   
   # Run the CLI
   lan-scan --help
   ```

## Style Guides

### Git Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools

Examples:
```
feat: add IPv6 support to network scanner
fix: correct MAC address parsing for certain vendors
docs: update installation instructions for macOS
test: add tests for online-only filter
```

### Python Style Guide

We follow PEP 8 with the following specifications:

- Use [Black](https://github.com/psf/black) for code formatting (88 character line limit)
- Use type hints for function signatures
- Write docstrings for all public functions and classes
- Use meaningful variable names

Example:
```python
from typing import List, Optional
from datetime import datetime

def get_online_devices(
    devices: List[Device], 
    threshold_seconds: int = 120
) -> List[Device]:
    """
    Filter devices that are currently online.
    
    Args:
        devices: List of Device objects to filter
        threshold_seconds: Maximum seconds since last seen to consider online
        
    Returns:
        List of devices that were seen within the threshold
    """
    now = datetime.now()
    return [
        device for device in devices 
        if (now - device.last_seen).total_seconds() < threshold_seconds
    ]
```

### Documentation Style Guide

- Use Markdown for all documentation
- Include code examples where appropriate
- Keep line length to 80 characters for better readability
- Use proper heading hierarchy
- Include a table of contents for long documents

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=simple_scanner --cov-report=term-missing

# Run specific test file
pytest tests/test_scanner.py

# Run with verbose output
pytest -v
```

### Writing Tests

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies (like nmap)

Example test:
```python
def test_device_is_online():
    """Test that online status is calculated correctly."""
    device = Device(
        mac_address="aa:bb:cc:dd:ee:ff",
        ip_address="192.168.1.100",
        last_seen=datetime.now(timezone.utc)
    )
    # Device is online if last seen within 120 seconds
    assert (datetime.now(timezone.utc) - device.last_seen).total_seconds() < 120
    
def test_device_is_offline():
    """Test that offline status is detected correctly."""
    device = Device(
        mac_address="aa:bb:cc:dd:ee:ff",
        ip_address="192.168.1.100",
        last_seen=datetime.now(timezone.utc) - timedelta(minutes=5)
    )
    # Device is offline if last seen more than 120 seconds ago
    assert (datetime.now(timezone.utc) - device.last_seen).total_seconds() >= 120
```

## Project Structure

Understanding the project structure will help you navigate the codebase:

```
simple-lan-scanner/
├── .github/                     # GitHub-specific files
│   ├── ISSUE_TEMPLATE/         # Issue templates
│   │   ├── bug_report.md       # Bug report template
│   │   └── feature_request.md  # Feature request template
│   ├── workflows/              # GitHub Actions
│   │   └── tests.yml           # Automated testing workflow
│   ├── CODEOWNERS              # Code ownership definitions
│   ├── FUNDING.yml             # Funding configuration
│   ├── SECURITY.md             # Security policy
│   └── pull_request_template.md # PR template
├── docs/                        # Documentation
│   ├── DOCUMENTATION.md         # Main documentation
│   └── README.md                # Documentation index
├── examples/                    # Usage examples
│   ├── README.md                # Examples overview
│   ├── basic_usage.py           # Basic scanning example
│   ├── continuous_monitoring.py # Monitoring example
│   └── advanced_filtering.py    # Filtering example
├── src/simple_scanner/          # Main package
│   ├── __init__.py              # Package initialization
│   ├── __main__.py              # Entry point
│   ├── cli.py                   # CLI implementation
│   ├── gui.py                   # GUI implementation
│   ├── models.py                # Data models
│   ├── scanner.py               # Core scanning logic
│   └── oui.py                   # MAC vendor lookup (future)
├── tests/                       # Test suite
│   ├── conftest.py              # Pytest configuration
│   ├── test_cli.py              # CLI tests
│   ├── test_gui.py              # GUI tests
│   ├── test_models.py           # Model tests
│   ├── test_scanner.py          # Scanner tests
│   ├── test_scanner_hostname_manufacturer.py  # Extended tests
│   └── test_models_comprehensive.py           # Comprehensive tests
├── CHANGELOG.md                 # Version history
├── CLAUDE.md                    # AI assistant instructions
├── CONTRIBUTING.md              # This file
├── LICENSE                      # MIT License
├── Makefile                     # Development shortcuts
├── README.md                    # Project overview
├── pyproject.toml               # Project configuration
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Basic dependencies
└── requirements-dev.txt         # Development dependencies
```

### Key Components

- **NetworkMonitor** (`scanner.py`): Core scanning engine
- **Device** (`models.py`): Device data model
- **CLI** (`cli.py`): Command-line interface
- **GUI** (`gui.py`): Graphical interface

## Questions?

Feel free to open an issue with the `question` label if you have any questions about contributing.

Thank you for contributing to Simple LAN Scanner! 🎉