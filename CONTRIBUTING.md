# Contributing to GeoElastix

Thank you for your interest in contributing to GeoElastix! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background or experience level.

### Expected Behavior

- Be respectful and considerate
- Focus on constructive feedback
- Accept criticism gracefully
- Help others learn and grow

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing others' private information

## How to Contribute

There are many ways to contribute:

### 1. Report Bugs

Found a bug? Please create an issue with:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, GeoElastix version)
- Error messages and tracebacks
- Sample data (if possible)

### 2. Suggest Features

Have an idea? Open an issue describing:
- The problem it solves
- Proposed solution
- Use cases
- Example workflow

### 3. Improve Documentation

Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples or tutorials
- Improve API documentation
- Translate documentation

### 4. Write Code

Contribute bug fixes or new features:
- Fix reported issues
- Implement requested features
- Optimize performance
- Add new registration methods
- Improve error handling

### 5. Create Examples

Share your workflows:
- Real-world use cases
- Integration with other tools
- Advanced techniques
- Visualization examples

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/geoelastix.git
cd geoelastix

# Add upstream remote
git remote add upstream https://github.com/yzh211/geoelastix.git
```

### 2. Create Environment

```bash
# Create and activate conda environment from environment.yml
conda env create -f environment.yml
conda activate geoelastix

# Install development dependencies
pip install pytest pytest-cov black flake8 isort mypy
```

### 3. Create Branch

```bash
# Update master
git checkout master
git pull upstream master

# Create feature branch
git checkout -b feature/your-feature-name
```

## Coding Standards

### Python Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specifics:

**Line Length**: 100 characters max (120 acceptable for long strings)

**Imports**: Organized with isort
```python
# Standard library
import os
from pathlib import Path

# Third-party
import numpy as np
from osgeo import gdal

# Local
from geoelastix.io import RasterIO
```

**Docstrings**: Use Google style
```python
def function(param1, param2):
    """Brief description.

    Longer description if needed.

    Args:
        param1 (type): Description
        param2 (type): Description

    Returns:
        type: Description

    Raises:
        ValueError: When something is wrong
    """
    pass
```

**Type Hints**: Use where appropriate
```python
def process_image(image_path: Path, threshold: float = 0.5) -> np.ndarray:
    """Process image with threshold."""
    pass
```

### Code Organization

**Module Structure**:
```
geoelastix/
├── __init__.py          # Package init
├── module/
│   ├── __init__.py      # Module init, exports
│   ├── core.py          # Core functionality
│   └── utils.py         # Helper functions
```

**Class Design**:
- Use clear, descriptive names
- Keep classes focused (single responsibility)
- Document all public methods
- Use private methods (leading underscore) for internal logic

**Function Design**:
- Keep functions short and focused
- Use clear parameter names
- Validate inputs
- Handle errors gracefully

### Formatting

Use automated tools:

```bash
# Format with black
black geoelastix/

# Sort imports
isort geoelastix/

# Check style
flake8 geoelastix/

# Type check
mypy geoelastix/ --ignore-missing-imports
```

## Testing

### Writing Tests

Place tests in `tests/` directory mirroring source structure:

```
tests/
├── test_io/
│   ├── test_raster_io.py
│   └── test_crs_manager.py
├── test_registration/
│   └── test_elastix_wrapper.py
└── test_displacement/
    └── test_horizontal.py
```

**Test Structure**:
```python
import pytest
from geoelastix.io import RasterIO

def test_read_geotiff():
    """Test reading GeoTIFF files."""
    # Arrange
    test_file = "test_data/sample.tif"

    # Act
    result = RasterIO.read_raster(test_file)

    # Assert
    assert result['array'].shape == (100, 100)
    assert result['crs'] is not None

def test_invalid_file():
    """Test error handling for invalid files."""
    with pytest.raises(FileNotFoundError):
        RasterIO.read_raster("nonexistent.tif")
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=geoelastix --cov-report=html

# Run specific test file
pytest tests/test_io/test_raster_io.py

# Run specific test
pytest tests/test_io/test_raster_io.py::test_read_geotiff

# Run with verbose output
pytest tests/ -v
```

### Test Coverage

Aim for:
- **80%+ overall coverage**
- **100% for critical functions** (registration, displacement calculation)
- **All error paths tested**

Check coverage:
```bash
pytest tests/ --cov=geoelastix --cov-report=term-missing
```

## Documentation

### Docstring Requirements

All public functions, classes, and modules must have docstrings:

```python
def compute_displacement(image_a: np.ndarray, image_b: np.ndarray,
                        mask: np.ndarray = None) -> dict:
    """Compute displacement between two images.

    Calculates pixel-wise displacement from image_a to image_b using
    the specified registration method.

    Args:
        image_a: First image array (reference)
        image_b: Second image array (moving)
        mask: Optional boolean mask (True = valid)

    Returns:
        Dictionary containing:
            - displacement_x: X component displacement
            - displacement_y: Y component displacement
            - magnitude: Total displacement magnitude

    Raises:
        ValueError: If images have different shapes
        TypeError: If inputs are not numpy arrays

    Example:
        >>> displacement = compute_displacement(img_a, img_b)
        >>> print(displacement['magnitude'].mean())
        2.45
    """
    pass
```

### Documentation Files

Update relevant documentation:
- `README.md`: For major features
- `docs/USER_GUIDE.md`: For user-facing changes
- `docs/API.md`: For API changes
- `CHANGELOG.md`: For all changes

### Examples

Include example code for new features:
```python
# In docstring
"""
Example:
    Basic usage:

    >>> from geoelastix.io import RasterIO
    >>> data = RasterIO.read_raster("dem.tif")
    >>> print(data['shape'])
    (1000, 1000)
"""
```

## Pull Request Process

### Before Submitting

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

2. **Run tests**:
   ```bash
   pytest tests/
   ```

3. **Check formatting**:
   ```bash
   black geoelastix/
   flake8 geoelastix/
   ```

4. **Update documentation**:
   - Add docstrings
   - Update relevant docs
   - Add examples

5. **Update CHANGELOG.md**:
   ```markdown
   ## [Unreleased]
   ### Added
   - New feature description (#PR_NUMBER)

   ### Fixed
   - Bug fix description (#PR_NUMBER)
   ```

### Submitting

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub:
   - Clear, descriptive title
   - Reference related issues (#123)
   - Describe changes in detail
   - Include examples if applicable
   - List any breaking changes
   - Add screenshots for UI changes

3. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Motivation
   Why is this change needed?

   ## Changes
   - Change 1
   - Change 2

   ## Testing
   How was this tested?

   ## Checklist
   - [ ] Tests pass
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] Code formatted (black, isort)
   - [ ] No new warnings
   ```

### Review Process

- Maintainers will review your PR
- Address feedback by pushing new commits
- Once approved, PR will be merged
- Your contribution will be credited

## Issue Reporting

### Bug Reports

Use this template:

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.10]
- GeoElastix version: [e.g., 0.1.0]
- GDAL version: [e.g., 3.6.0]

## Error Messages
```
Full error traceback
```

## Additional Context
Any other relevant information
```

### Feature Requests

Use this template:

```markdown
## Problem
What problem does this solve?

## Proposed Solution
Describe your proposed solution

## Alternatives
Other solutions you considered

## Use Case
Example use case or workflow

## Additional Context
Any other relevant information
```

## Development Guidelines

### Branching Strategy

- `master`: Stable releases
- `develop`: Integration branch (if used)
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `docs/*`: Documentation updates

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

**Examples**:
```
feat(displacement): add 3D magnitude calculation

Implements compute_3d_magnitude function that calculates total
displacement magnitude including vertical component.

Closes #123
```

```
fix(io): handle missing CRS in raster files

Previously would crash when CRS undefined. Now logs warning and
continues processing.
```

### Version Numbers

Follow [Semantic Versioning](https://semver.org/):

- MAJOR: Incompatible API changes
- MINOR: Backward-compatible functionality
- PATCH: Backward-compatible bug fixes

Example: `0.1.0` → `0.2.0` (new feature) → `0.2.1` (bug fix)

## Release Process

For maintainers:

1. Update version in `geoelastix/__version__.py`
2. Update `CHANGELOG.md`
3. Create release commit
4. Tag release: `git tag -a v0.2.0 -m "Release 0.2.0"`
5. Push: `git push --tags`
6. Create GitHub release
7. Build and upload to PyPI (if applicable)

## Questions?

- Check existing issues and documentation
- Ask in issue comments
- Open a discussion on GitHub

## Citation

If you use GeoElastix in your research or build upon it, please cite the original methodology paper:

Zhu, Y., Dortch, J. M., & Haneberg, W. C. (2022). Non-affine georectification to improve the topographic fidelity of legacy geologic maps. *International Journal of Applied Earth Observation and Geoinformation*, 115, 103127. https://doi.org/10.1016/j.jag.2022.103127

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Recognition

All contributors will be acknowledged in:
- `CHANGELOG.md` (per contribution)
- Release notes
- GitHub contributors page

Thank you for contributing to GeoElastix!
