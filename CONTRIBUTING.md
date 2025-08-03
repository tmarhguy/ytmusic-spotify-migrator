# Contributing to YT2Spot

Thank you for your interest in contributing to YT2Spot! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- Git

### Local Development

1. Fork and clone the repository:

```bash
git clone https://github.com/your-username/ytmusic-spotify-migrator.git
cd ytmusic-spotify-migrator
```

2. Set up the development environment:

```bash
# Run the setup script
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh

# Or manually:
python -m venv venv
source venv/bin/activate
pip install -e .
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

3. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your Spotify API credentials
```

4. Run the application:

```bash
# Terminal 1: Backend
cd backend
source ../venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

## Project Structure

```
ytmusic-spotify-migrator/
├── yt2spot/                 # Core Python package
├── backend/                 # FastAPI web server
├── frontend/                # React web interface
├── tools/                   # Utility tools
├── tests/                   # Test suites
└── scripts/                 # Development scripts
```

## Contribution Guidelines

### Code Style

**Python:**

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Maximum line length: 88 characters
- Use `black` for code formatting
- Use `ruff` for linting

**TypeScript/React:**

- Use TypeScript for all new code
- Follow React best practices and hooks patterns
- Use ESLint configuration provided
- Maximum line length: 100 characters

### Testing

**Python Tests:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=yt2spot

# Run specific test file
pytest tests/test_matching.py
```

**Frontend Tests:**

```bash
cd frontend
npm test
```

### Commit Convention

Use conventional commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Examples:

```
feat(auth): add spotify oauth integration
fix(matching): improve fuzzy matching algorithm
docs(readme): update installation instructions
```

### Pull Request Process

1. Create a feature branch from `main`:

```bash
git checkout -b feat/your-feature-name
```

2. Make your changes following the style guidelines

3. Add tests for new functionality

4. Ensure all tests pass:

```bash
pytest
cd frontend && npm test
```

5. Update documentation if needed

6. Commit your changes with conventional commit messages

7. Push to your fork and create a pull request

8. Fill out the pull request template completely

### Pull Request Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing

- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Screenshots (if applicable)

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No sensitive information included
```

## Issue Guidelines

### Bug Reports

Include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Log output or error messages

### Feature Requests

Include:

- Clear description of the proposed feature
- Use case and motivation
- Proposed implementation approach (if any)
- Alternative solutions considered

## Development Guidelines

### Adding New Features

1. Create an issue to discuss the feature first
2. Keep changes focused and atomic
3. Add comprehensive tests
4. Update documentation
5. Consider backward compatibility

### Bug Fixes

1. Identify the root cause
2. Add tests that reproduce the bug
3. Implement the fix
4. Verify tests pass

### Performance Improvements

1. Measure current performance
2. Implement improvements
3. Measure new performance
4. Add benchmarks if applicable

## Security

- Never commit API keys, tokens, or other secrets
- Use environment variables for configuration
- Follow secure coding practices
- Report security vulnerabilities privately

## Documentation

- Keep README files updated
- Add docstrings to all public functions
- Update API documentation for endpoint changes
- Include examples for new features

## Release Process

1. Update version numbers in `pyproject.toml` and `package.json`
2. Update CHANGELOG.md
3. Create a release PR
4. Tag the release after merging
5. Publish to PyPI (maintainers only)

## Getting Help

- Check existing issues and documentation first
- Create a new issue for questions
- Use clear, descriptive titles
- Provide relevant context and details

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold this code.

## Recognition

Contributors will be recognized in:

- README.md contributor section
- Release notes
- Project documentation

Thank you for contributing to YT2Spot!
