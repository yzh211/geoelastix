# GeoElastix User Guide

Comprehensive guide for using GeoElastix for landslide monitoring and ground displacement analysis.

## Table of Contents

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [CLI Commands](#cli-commands)
- [Configuration Files](#configuration-files)
- [Registration Methods](#registration-methods)
- [Input Data Preparation](#input-data-preparation)
- [Understanding Outputs](#understanding-outputs)
- [Visualization Options](#visualization-options)
- [Quality Assessment](#quality-assessment)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)

## Introduction

GeoElastix is a professional tool for geospatial image registration designed specifically for landslide monitoring. It analyzes multi-temporal Digital Elevation Models (DEMs) to quantify ground displacement in three dimensions:

- **X displacement**: East-West horizontal movement
- **Y displacement**: North-South horizontal movement
- **Z displacement**: Vertical movement (uplift/subsidence)
- **Magnitude**: Total displacement magnitude

## Quick Start

### Basic Usage with CLI Arguments

Register two DEMs with minimal configuration:

```bash
geoelastix register \
  --fixed GIS/wrigley_30ft_lidar.tif \
  --moving GIS/wrigley_30ft_legacy.tif \
  --job-id landslide_analysis \
  --output ./results
```

### Using Configuration File

For more control, create and use a configuration file:

```bash
# Create template
geoelastix create-config --output my_config.yaml

# Edit my_config.yaml with your settings
# Then run registration
geoelastix register --config my_config.yaml
```

## CLI Commands

GeoElastix provides five main commands:

### 1. register

Perform image registration and displacement analysis.

```bash
geoelastix register --config config.yaml
```

**Options**:
- `--config, -c`: Path to YAML configuration file
- `--fixed, -f`: Path to fixed (reference) image
- `--moving, -m`: Path to moving image
- `--job-id`: Job identifier (default: geoelastix_job)
- `--output, -o`: Output directory (default: ./output)
- `--method`: Registration method: NA, AF, RG, or TS (default: NA)
- `--log-level`: Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)

**Examples**:

```bash
# Minimal usage
geoelastix register -f dem_new.tif -m dem_old.tif --job-id test

# With specific method
geoelastix register -f dem_new.tif -m dem_old.tif --method AF

# Custom output directory
geoelastix register -f dem_new.tif -m dem_old.tif -o /path/to/results
```

### 2. list-methods

Display available registration methods and descriptions.

```bash
geoelastix list-methods
```

**Output**:
```
Available Registration Methods:
======================================================================

  NA: Non-Affine (BSpline) Registration
      - Deformable registration for complex deformations
      - Recommended for landslide monitoring

  AF: Affine Registration
      - Linear transformation (rotation, translation, scaling, shearing)
      - Good for moderate deformations

  RG: Rigid/Euler Registration
      - Rotation and translation only
      - Suitable for datasets with minimal deformation

  TS: Translation-only Registration
      - Translation only, no rotation or scaling
      - Use when images are already well-aligned
```

### 3. show-params

Display contents of a parameter file.

```bash
geoelastix show-params NA
```

**Usage**: Useful for understanding registration parameters or creating custom parameter files.

### 4. create-config

Generate a configuration template with all options and documentation.

```bash
geoelastix create-config --output my_config.yaml
```

**Output**: Creates a YAML file with comprehensive comments explaining each option.

### 5. validate-config

Validate a configuration file before running registration.

```bash
geoelastix validate-config config.yaml
```

**Checks**:
- Required fields present
- Input files exist
- Valid registration method
- Valid output formats
- Valid plot types
- Numeric thresholds in valid ranges

## Configuration Files

Configuration files use YAML format for human-readable settings.

### Basic Configuration

Minimum required configuration:

```yaml
job:
  id: "my_analysis"
  output_dir: "./output"

input:
  fixed_image: "./GIS/wrigley_30ft_lidar.tif"
  moving_image: "./GIS/wrigley_30ft_legacy.tif"

registration:
  method: "NA"
```

### Complete Configuration

Full configuration with all options:

```yaml
# Job information
job:
  id: "wrigley_2021_vs_2022"
  description: "Landslide monitoring analysis"
  output_dir: "./output"

# Input data
input:
  fixed_image: "./GIS/wrigley_30ft_lidar.tif"    # Reference (newer) DEM
  moving_image: "./GIS/wrigley_30ft_legacy.tif"   # Moving (older) DEM

# Registration settings
registration:
  method: "NA"                           # NA, AF, RG, or TS
  metric: "NCC"                          # NCC or MI
  parameter_file: null                   # Custom parameter file (optional)

# Processing options
processing:
  tile_threshold: 5000                   # Enable tiling if dimension > this
  tile_overlap: 100                      # Pixel overlap between tiles
  num_threads: 4                         # Number of parallel threads

# Output settings
output:
  formats: ["geotiff", "asc"]           # Output formats
  generate_magnitude: true               # Generate horizontal magnitude
  compression: "LZW"                     # GeoTIFF compression

# Visualization
visualization:
  generate_plots: true
  plot_types:
    - "quiver"                           # Vector field
    - "contour_x"                        # X displacement contour
    - "contour_y"                        # Y displacement contour
    - "contour_z"                        # Z displacement contour
    - "contour_magnitude"                # Magnitude contour
  dpi: 300
  colormap: "viridis"
  quiver_subsample: 50

# Quality thresholds
quality:
  rmse_warning_threshold: 10.0           # Warning if RMSE > this (map units)
  min_overlap_percent: 70.0              # Warning if overlap < this
  max_nodata_percent: 30.0               # Warning if no-data > this
  min_dice: 0.7                          # Warning if Dice < this
  min_correlation: 0.5                   # Warning if correlation < this
  min_mi: 0.1                            # Warning if MI < this

# Logging
logging:
  level: "INFO"                          # DEBUG, INFO, WARNING, ERROR
  save_to_file: true
```

## Registration Methods

Choose the appropriate method based on expected deformation:

### NA - Non-Affine (BSpline) [DEFAULT]

**When to use**:
- **Landslide monitoring** (recommended)
- Complex, non-linear deformations
- Large or spatially varying displacements

**Characteristics**:
- Most flexible transformation
- Can handle complex deformation patterns
- Longer computation time
- Best for landslide applications

**Example**:
```yaml
registration:
  method: "NA"
  metric: "NCC"
```

### AF - Affine

**When to use**:
- Moderate deformations
- Linear transformations sufficient
- Faster processing needed

**Characteristics**:
- Rotation, translation, scaling, shearing
- Faster than Non-Affine
- Good for regional-scale deformations

**Example**:
```yaml
registration:
  method: "AF"
  metric: "MI"
```

### RG - Rigid/Euler

**When to use**:
- Minimal deformation expected
- Mainly alignment correction
- Very fast processing needed

**Characteristics**:
- Rotation and translation only
- No scaling or shearing
- Fastest method
- Use when shape preservation is critical

**Example**:
```yaml
registration:
  method: "RG"
  metric: "MI"
```

### TS - Translation Only

**When to use**:
- Images already well-aligned
- Only offset correction needed
- Fastest possible processing

**Characteristics**:
- Translation only
- No rotation, scaling, or deformation
- Extremely fast
- Very limited use cases

**Example**:
```yaml
registration:
  method: "TS"
  metric: "MI"
```

## Input Data Preparation

### Supported Formats

- **GeoTIFF** (.tif, .tiff) - Recommended
- **ASC** (.asc) - ESRI ASCII Grid

### Data Requirements

1. **Spatial Resolution**: Both DEMs should have similar spatial resolution (within 2x factor)

2. **Coordinate Reference System (CRS)**:
   - Both DEMs should use the same CRS
   - If CRS not defined, assumes same CRS
   - Use projected CRS (e.g., UTM) for accurate displacement measurements

3. **Overlap**: DEMs must have sufficient overlap (recommended > 70%)

4. **Data Type**: Single-band rasters (elevation/height values)

5. **No-Data Values**: Properly defined no-data values (automatically detected)

### Pre-processing Recommendations

1. **Reproject to Common CRS**: If DEMs have different CRS, reproject to match:
   ```bash
   gdalwarp -t_srs EPSG:32610 input.tif output_reprojected.tif
   ```

2. **Resample to Common Resolution**: If resolutions differ significantly:
   ```bash
   gdalwarp -tr 1.0 1.0 -r bilinear input.tif output_resampled.tif
   ```

3. **Clip to Common Extent**: For faster processing, clip to overlapping region:
   ```bash
   gdalwarp -te xmin ymin xmax ymax input.tif output_clipped.tif
   ```

4. **Fill Small Gaps**: Fill small no-data gaps if appropriate:
   ```bash
   gdal_fillnodata.py input.tif output_filled.tif
   ```

## Understanding Outputs

GeoElastix creates organized output directories:

```
output/
└── jobid_description_20241120_143022/
    ├── displacement/
    │   ├── displacement_x.tif          # East-West displacement
    │   ├── displacement_x.asc
    │   ├── displacement_y.tif          # North-South displacement
    │   ├── displacement_y.asc
    │   ├── displacement_z.tif          # Vertical displacement
    │   ├── displacement_z.asc
    │   ├── displacement_magnitude.tif  # Horizontal magnitude
    │   └── displacement_magnitude.asc
    ├── registered/
    │   └── registered_moving.tif       # Registered moving image
    ├── visualization/
    │   ├── horizontal_quiver.png       # Vector field plot
    │   ├── displacement_x_contour.png
    │   ├── displacement_y_contour.png
    │   ├── displacement_z_contour.png
    │   └── displacement_magnitude_contour.png
    ├── logs/
    │   └── geoelastix.log             # Detailed log file
    ├── parameters/
    │   └── (elastix parameter files)
    ├── report.txt                      # Text summary report
    └── metrics.json                    # Machine-readable metrics
```

### Displacement Interpretation

**displacement_x.tif** (East-West):
- Positive values: Eastward movement
- Negative values: Westward movement
- Units: Same as input CRS (typically meters)

**displacement_y.tif** (North-South):
- Positive values: Northward movement
- Negative values: Southward movement
- Units: Same as input CRS (typically meters)

**displacement_z.tif** (Vertical):
- Positive values: Uplift
- Negative values: Subsidence
- Calculated as: Fixed - Registered
- Units: Same as input data (typically meters)

**displacement_magnitude.tif** (Horizontal Magnitude):
- Always positive
- Formula: sqrt(x² + y²)
- Total horizontal displacement
- Units: Same as input CRS (typically meters)

## Visualization Options

### Quiver Plots

Vector field visualization showing displacement direction and magnitude:

```yaml
visualization:
  plot_types: ["quiver"]
  quiver_subsample: 50    # Show every 50th vector
  colormap: "viridis"
```

**Features**:
- Arrows show displacement direction
- Arrow color shows magnitude
- Automatic subsampling for clarity
- Rose diagram showing direction distribution

### Contour Plots

Filled contour maps for displacement components:

```yaml
visualization:
  plot_types:
    - "contour_x"         # X displacement
    - "contour_y"         # Y displacement
    - "contour_z"         # Z displacement
    - "contour_magnitude" # Magnitude
  colormap: "RdBu_r"      # Red-Blue diverging
  dpi: 300                # High resolution
```

**Features**:
- Smooth contour lines
- Color-coded displacement values
- Symmetric colormaps for X, Y, Z (centered at zero)
- Sequential colormap for magnitude

### Customizing Visualizations

**Change colormap**:
```yaml
visualization:
  colormap: "jet"      # Or: viridis, plasma, coolwarm, seismic
```

**Adjust resolution**:
```yaml
visualization:
  dpi: 150    # Lower for faster generation
  dpi: 600    # Higher for publication quality
```

**Disable visualizations**:
```yaml
visualization:
  generate_plots: false
```

## Quality Assessment

GeoElastix automatically computes quality metrics:

### Metrics Computed

1. **RMSE (Root Mean Square Error)**
   - Pixel-wise difference between fixed and registered images
   - Lower is better
   - Units: Same as input data

2. **Mutual Information (MI)**
   - Statistical dependency between images
   - Higher is better
   - Normalized MI also computed

3. **Dice Coefficient**
   - Overlap between valid data regions
   - Range: 0 to 1 (1 = perfect overlap)

4. **Coverage Statistics**
   - Percentage of valid pixels
   - Overlap percentages

5. **Pearson Correlation**
   - Linear correlation between images
   - Range: -1 to 1 (1 = perfect positive correlation)

### Quality Warnings

Automatic warnings triggered when:
- RMSE exceeds threshold (default: 10.0 map units)
- Overlap < 70%
- No-data > 30%
- Dice coefficient < 0.7
- Correlation < 0.5
- MI < 0.1

**Configure thresholds**:
```yaml
quality:
  rmse_warning_threshold: 5.0
  min_overlap_percent: 80.0
  max_nodata_percent: 20.0
```

### Interpreting Quality Reports

Example report output:
```
QUALITY METRICS
==================================================
RMSE:                 2.345 m
Mutual Information:   0.856
Normalized MI:        0.912
Dice Coefficient:     0.923
Correlation:          0.887

COVERAGE STATISTICS
--------------------------------------------------
Fixed Valid:          95.2%
Registered Valid:     94.8%
Overlap:              93.5%
```

**Good registration indicators**:
- Low RMSE (< 5m for typical landslide monitoring)
- High MI (> 0.5)
- High Dice (> 0.8)
- High correlation (> 0.7)
- High overlap (> 80%)

## Advanced Usage

### Large Dataset Processing

For large DEMs (> 5000×5000 pixels), automatic tiling is triggered:

```yaml
processing:
  tile_threshold: 5000    # Enable tiling above this size
  tile_overlap: 100       # Overlap for seamless blending
```

**Manual tiling control**:
```yaml
processing:
  tile_threshold: 3000    # Force tiling at smaller size
  tile_overlap: 200       # Larger overlap for better blending
```

### Custom Parameter Files

For advanced users, create custom elastix parameter files:

```yaml
registration:
  method: "NA"
  parameter_file: "./custom_params.txt"
```

See existing parameter files in `parameters/` directory for templates.

### Multi-threaded Processing

Adjust thread count for performance:

```yaml
processing:
  num_threads: 8    # Use 8 CPU cores
```

**Recommendation**: Set to number of physical CPU cores.

### Output Format Selection

Choose output formats based on needs:

```yaml
output:
  formats: ["geotiff"]    # GeoTIFF only
  # formats: ["asc"]       # ASC only
  # formats: ["geotiff", "asc"]  # Both
```

**GeoTIFF** (.tif):
- Pros: Smaller file size, compression support, widely supported
- Cons: Binary format

**ASC** (.asc):
- Pros: Human-readable text format, simple structure
- Cons: Larger file size, no compression

## Best Practices

### 1. Data Preparation
- Always use projected CRS (e.g., UTM) for accurate measurements
- Ensure DEMs have good quality and minimal artifacts
- Preprocess to remove large no-data regions if possible

### 2. Method Selection
- Start with **NA method** for landslide monitoring
- Use **AF method** if NA is too slow or produces artifacts
- Use **RG method** only for pre-aligned data
- Avoid **TS method** unless you know images differ only by translation

### 3. Quality Control
- Always review quality metrics in report
- Visually inspect displacement maps and registered image
- Check for unrealistic displacement patterns
- Validate results against field observations if available

### 4. Performance Optimization
- Use tiling for large datasets (automatically enabled)
- Adjust thread count based on your CPU
- Disable visualization generation for batch processing:
  ```yaml
  visualization:
    generate_plots: false
  ```

### 5. Reproducibility
- Save configuration files for each analysis
- Document method selection rationale
- Archive quality reports with results
- Version control configuration files

### 6. Batch Processing
Create configuration files for multiple analyses:

```bash
# Create configs for multiple time periods
geoelastix register --config config_2020_2021.yaml
geoelastix register --config config_2021_2022.yaml
geoelastix register --config config_2022_2023.yaml
```

### 7. Result Validation
- Compare results with independent measurements (GPS, InSAR)
- Check consistency across time series
- Verify displacement magnitudes are physically reasonable
- Cross-validate with different registration methods

## Common Workflows

### Workflow 1: Single Time Period Analysis

```bash
# 1. Create configuration
geoelastix create-config -o config.yaml

# 2. Edit configuration with your data paths
# (edit config.yaml)

# 3. Validate configuration
geoelastix validate-config config.yaml

# 4. Run analysis
geoelastix register --config config.yaml

# 5. Review outputs in output directory
```

### Workflow 2: Time Series Analysis

```bash
# Register multiple time periods
for year in 2020 2021 2022 2023; do
  geoelastix register \
    --fixed dem_${year}.tif \
    --moving dem_$((year-1)).tif \
    --job-id "landslide_${year}" \
    --output ./results_timeseries
done
```

### Workflow 3: Method Comparison

```bash
# Compare different registration methods
for method in NA AF RG; do
  geoelastix register \
    --fixed dem_new.tif \
    --moving dem_old.tif \
    --method $method \
    --job-id "comparison_${method}" \
    --output ./method_comparison
done
```

## Getting Help

- **Command help**: `geoelastix --help` or `geoelastix <command> --help`
- **Documentation**: See docs/ directory
- **Examples**: See examples/ directory
- **Issues**: https://github.com/yzh211/geoelastix/issues
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Next Steps

- Explore [API documentation](API.md) for Python library usage
- Read [Methodology](METHODOLOGY.md) to understand algorithms
- Try [example workflows](../examples/)
- Review [troubleshooting guide](TROUBLESHOOTING.md) for common issues
