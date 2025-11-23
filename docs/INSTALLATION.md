# Installation Guide

This guide provides detailed instructions for installing GeoElastix on various platforms.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [Recommended Installation](#recommended-installation)
- [Verify Installation](#verify-installation)
- [Platform-Specific Notes](#platform-specific-notes)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, Linux (Ubuntu 18.04+, CentOS 7+), macOS 10.14+
- **Python**: 3.8 or higher
- **RAM**: 8 GB (16 GB recommended for large datasets)
- **Disk Space**: 2 GB for software + storage for data

### Recommended Requirements
- **RAM**: 16 GB or more
- **CPU**: Multi-core processor (4+ cores)
- **Disk Space**: SSD with sufficient space for input/output data

## Installation Methods

### Recommended Installation

The recommended installation method uses the provided `environment.yml` file, which automatically handles all dependencies including GDAL, ITK, and other complex packages.

#### Step 1: Install Conda

If you don't have Conda installed, download and install either:
- **Miniconda** (minimal installation, recommended): https://docs.conda.io/en/latest/miniconda.html
- **Anaconda** (includes many scientific packages): https://www.anaconda.com/download

#### Step 2: Clone Repository and Create Environment

```bash
# Clone the repository
git clone https://github.com/yzh211/geoelastix.git
cd geoelastix

# Create and activate conda environment
conda env create -f environment.yml
conda activate geoelastix
```

The `environment.yml` file automatically installs:
- Python 3.10
- GDAL (geospatial data I/O)
- ITK and itk-elastix (registration engine)
- NumPy, SciPy, Matplotlib (scientific computing and visualization)
- PyYAML (configuration parsing)
- All other required dependencies

#### Step 3: Verify Installation

```bash
# Check version
geoelastix --version

# List available methods
geoelastix list-methods

# Run quick test
python quick_test.py
```

## Verify Installation

After installation, verify that GeoElastix is working correctly:

### Basic Verification

```bash
# Check version
geoelastix --version
# Expected output: GeoElastix 0.1.0

# Display help
geoelastix --help

# List available registration methods
geoelastix list-methods
# Expected output:
#   NA: Non-Affine (BSpline) Registration
#   AF: Affine Registration
#   RG: Rigid/Euler Registration
#   TS: Translation-only Registration
```

### Comprehensive Testing

Run the quick test script to validate all components:

```bash
python quick_test.py
```

This will:
- Test all dependency imports (NumPy, GDAL, ITK, Matplotlib)
- Verify GeoElastix modules load correctly
- Check for example data files
- Optionally run a complete registration workflow

See the [Testing & Validation](../examples/README.md#testing--validation-scripts) section for more testing options.

## Platform-Specific Notes

### Windows

1. **Install Visual C++ Redistributable**: Some dependencies may require the [Microsoft Visual C++ Redistributable](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads)

2. **Path Issues**: If `geoelastix` command is not found, ensure your Python Scripts directory is in PATH:
   ```cmd
   # Add to PATH (adjust path to your Python installation)
   set PATH=%PATH%;C:\Users\<username>\Anaconda3\envs\geoelastix\Scripts
   ```

### Linux

1. **System Dependencies**: Install system libraries for GDAL:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install libgdal-dev gdal-bin

   # CentOS/RHEL
   sudo yum install gdal gdal-devel
   ```

2. **Permission Issues**: If you encounter permission errors, use a virtual environment or install with `--user` flag

### macOS

1. **Xcode Command Line Tools**: Ensure Xcode command line tools are installed:
   ```bash
   xcode-select --install
   ```

2. **Homebrew GDAL**: If using Homebrew for GDAL:
   ```bash
   brew install gdal
   ```

## Troubleshooting

### GDAL Import Errors

**Problem**: `ImportError: No module named 'osgeo'`

**Solution**:
```bash
# Reinstall GDAL via conda
conda install -c conda-forge gdal --force-reinstall

# Or set GDAL_DATA environment variable
export GDAL_DATA=$(gdal-config --datadir)
```

### ITK/Elastix Errors

**Problem**: `ModuleNotFoundError: No module named 'itk'`

**Solution**:
```bash
# Install ITK and itk-elastix
conda install -c conda-forge itk itk-elastix
```

### Command Not Found

**Problem**: `geoelastix: command not found`

**Solution**:
```bash
# Ensure environment is activated
conda activate geoelastix

# Or use full path to script
python -m geoelastix.cli.main --version

# Reinstall package
pip install -e . --force-reinstall
```

### Memory Errors with Large Datasets

**Problem**: `MemoryError` when processing large DEMs

**Solution**:
- Use tiled processing (automatically triggered for images > 5000×5000)
- Reduce tile size in configuration:
  ```yaml
  processing:
    tile_threshold: 3000
  ```
- Close other applications to free up memory

### Registration Failures

**Problem**: Registration produces poor results or fails

**Solution**:
- Try different registration methods (NA, AF, RG, TS)
- Check input data quality and no-data values
- Ensure DEMs have sufficient overlap
- Verify CRS compatibility
- See [USER_GUIDE.md](USER_GUIDE.md) for method selection guidance

## Getting Help

If you encounter issues not covered here:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review the [User Guide](USER_GUIDE.md)
3. Search or create an issue on [GitHub Issues](https://github.com/yzh211/geoelastix/issues)
4. Contact the development team

## Next Steps

After successful installation:
- Read the [User Guide](USER_GUIDE.md) for usage instructions
- Try the [Quick Start Tutorial](QUICKSTART.md)
- Explore the [Example Workflows](../examples/)
