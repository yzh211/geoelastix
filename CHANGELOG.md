# Changelog

All notable changes to GeoElastix will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-11-20

### Added - Phase 3: Validation & Visualization

- **Quality Metrics Module**
  - `QualityMetrics`: Comprehensive registration quality assessment
    - RMSE (Root Mean Square Error) calculation
    - Mutual Information (MI) and Normalized MI
    - Dice coefficient for mask overlap
    - Coverage statistics (overlap percentages)
    - Pearson correlation coefficient
    - All metrics support masking for valid regions only

- **Quality Checker**
  - `QualityChecker`: Automated quality assessment with thresholds
    - Configurable warning and error thresholds
    - RMSE, overlap, no-data, Dice, correlation, and MI checks
    - Displacement statistics validation
    - Quality report generation (text format)
    - JSON export for machine-readable metrics

- **Visualization Modules**
  - `QuiverPlot`: Vector field visualization for horizontal displacement
    - Standard quiver plots with magnitude coloring
    - Quiver overlay on background images
    - Magnitude and direction side-by-side plots
    - Rose diagrams for displacement direction distribution
    - Configurable subsampling, colormaps, and scaling

  - `ContourPlot`: Contour map visualization
    - Filled contour plots for displacement fields
    - Multi-panel layout (X, Y, Z, magnitude)
    - Hillshade overlay for 3D effect
    - Difference maps between datasets
    - Symmetric colormaps centered at zero
    - Customizable levels, colors, and labels

- **Report Generator**
  - `ReportGenerator`: Automated report creation
    - Text-based comprehensive reports
    - JSON metrics export
    - Summary figures with multiple plots
    - Job information and metadata tracking
    - Quality assessment integration
    - Displacement statistics summaries

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
