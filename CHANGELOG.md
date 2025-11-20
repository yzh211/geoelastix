# Changelog

All notable changes to GeoElastix will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-11-20

### Added - Phase 2: Displacement & Tiling

- **Displacement Calculation Modules**
  - `HorizontalDisplacement`: Extract X, Y displacement from elastix deformation fields
    - Support for BSpline, Affine, Rigid, and Translation transforms
    - Automatic deformation field extraction
    - Displacement statistics and masking
  - `VerticalDisplacement`: Compute Z displacement from elevation difference
    - Direct elevation comparison (Fixed - Registered)
    - Uplift/subsidence classification
    - Gradient computation for rapid change detection
  - `DisplacementMagnitude`: Calculate displacement magnitudes
    - Horizontal magnitude (√(x² + y²))
    - 3D magnitude (√(x² + y² + z²))
    - Direction calculation and compass naming
    - Strain rate computation
    - Vector field preparation for visualization

- **Tiling System for Large Datasets**
  - `TileManager`: Automatic tiling for images > 5000x5000 pixels
    - Intelligent tile layout with overlap
    - Tile extraction and reconstruction
    - Multiple blend methods (average, feather, first)
    - Tile layout save/load functionality
  - `EdgeHandler`: Seamless tile blending
    - Feathering masks for smooth transitions
    - Distance-based and Gaussian weight masks
    - Edge artifact detection
    - Overlap region blending

- **Tests**
  - Comprehensive displacement module tests
  - Vertical displacement with synthetic subsidence data
  - Magnitude and direction calculation tests
  - Tiling functionality tests

### Added - Phase 1: Core Foundation

- **Project Structure**
  - Modular package architecture
  - Apache 2.0 license
  - Conda environment with GDAL support
  - Git repository initialization

- **I/O Module**
  - `RasterIO`: GeoTIFF and ASC file reading/writing
  - `NoDataHandler`: GDAL-compliant no-data value handling
  - `CRSManager`: CRS detection, validation, and comparison
  - ITK image conversion utilities

- **Registration Module**
  - `ElastixWrapper`: Simplified ITK-Elastix interface
  - `TwoPassRegistration`: Automated two-pass registration strategy
  - `ParameterManager`: Parameter file management

- **Parameter Files**
  - NA_NCC_ASGD.txt - Non-Affine (default for landslide monitoring)
  - AF_MI_ASGD.txt - Affine transform
  - RG_MI_ASGD.txt - Rigid/Euler transform
  - TS_MI_ASGD.txt - Translation only

- **Utilities**
  - Professional logging configuration
  - Timestamp generation
  - Directory management helpers
  - File size formatting

- **Examples**
  - Wrigley landslide dataset
  - Configuration file template
  - I/O module test script

- **Documentation**
  - README with quick start guide
  - Wrigley example documentation
  - Installation instructions

## [0.0.0] - 2024-11-20

### Added
- Initial project scaffolding
- Git repository setup
