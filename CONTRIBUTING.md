# Contributing to Token Helper

Thank you for your interest in contributing to the Token Helper project! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs
- Use the [Bug Report template](https://github.com/chilhoekdev/token-helper/issues/new?template=bug_report.yml)
- Check if the issue already exists before reporting
- Include as much detail as possible (OS, version, steps to reproduce)
- Include error messages and screenshots when applicable

### Suggesting Enhancements
- Use the [Feature Request template](https://github.com/chilhoekdev/token-helper/issues/new?template=feature_request.yml)
- Clearly describe the enhancement and why it would be useful
- Provide examples of how this feature would be used

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages (`git commit -m 'Add some AmazingFeature'`)
6. Push to your branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## Development Setup

### Prerequisites
- Python 3.9 or later
- Git
- A text editor or IDE of your choice

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/chilhoekdev/token-helper.git
cd token-helper

# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.\.venv\Scripts\Activate.ps1
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller  # For building executables
```

### Running Tests
```bash
# Run the application
python main.py

# Build executable
.\build.ps1
```

## Coding Standards

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Include error handling
- Test your changes on Windows 10/11

## Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Example: `Add support for Discord Canary` or `Fix Firefox profile detection`

## Pull Request Process

1. Update the README.md with any new features or changes
2. Ensure your code passes the linting checks (GitHub Actions)
3. Link any related issues in the PR description
4. Wait for code review and address feedback
5. Once approved, your PR will be merged

## Versioning

We use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Use the versioning script to manage releases:
```bash
python scripts/version.py patch "Your message here"
```

## Questions?

- Check existing [Issues](https://github.com/chilhoekdev/token-helper/issues)
- Review [Discussions](https://github.com/chilhoekdev/token-helper/discussions)
- Feel free to open a new discussion

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

Thank you for contributing! ❤️
