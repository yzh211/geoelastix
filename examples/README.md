# GeoElastix Examples

This directory contains example workflows demonstrating various GeoElastix features and use cases.

## Examples Overview

| Example | Description | Difficulty |
|---------|-------------|-----------|
| [wrigley/](#wrigley-landslide-example) | Complete landslide monitoring workflow | Beginner |
| [batch_processing.py](#batch-processing) | Process multiple DEM pairs in sequence | Intermediate |
| [python_api_example.py](#python-api-usage) | Use GeoElastix as Python library | Intermediate |

## Testing & Validation Scripts

Located in the project root directory:

| Script | Description | Purpose |
|--------|-------------|---------|
| [quick_test.py](#quick-test-script) | Interactive installation validator | Verify setup before processing |
| [test_wrigley_registration.py](#wrigley-test-script) | Automated Wrigley test | Simple workflow validation |
| [benchmark_speed.py](#benchmark-script) | Performance measurement | Analyze processing times |
| [test_itk_workflow.py](#itk-workflow-test) | ITK type validation | Verify ITK integration |

## Wrigley Landslide Example

Complete example using real landslide data.

**Location**: `examples/wrigley/`

**Dataset**: Wrigley landslide site multi-temporal DEMs

**What it demonstrates**:
- Basic configuration file setup
- Default NA-NCC-ASGD registration method
- Complete workflow from input to visualization
- Quality assessment and reporting

**How to run**:

```bash
cd examples/wrigley
geoelastix register --config config_wrigley.yaml
```

**Expected outputs**:
- Displacement fields (X, Y, Z, magnitude)
- Quality metrics and reports
- Visualization plots (quiver, contours)
- Registered DEM

**Processing time**: ~5-10 minutes (depending on hardware)

**Files**:
- `config_wrigley.yaml`: Configuration file
- `data/`: Input DEMs (if included)
- `README.md`: Detailed documentation

## Batch Processing

Process multiple DEM pairs in a time series.

**File**: `batch_processing.py`

**What it demonstrates**:
- Programmatic configuration generation
- Loop through multiple analyses
- Error handling for batch jobs
- Summary reporting

**Use case**: Time series analysis (e.g., annual DEMs from 2019-2022)

**How to use**:

1. Edit the script to define your DEM pairs:

```python
analyses = [
    {
        'fixed': 'GIS/wrigley_30ft_lidar.tif',
        'moving': 'GIS/wrigley_30ft_legacy.tif',
        'job_id': 'analysis_legacy_vs_lidar',
        'description': 'Wrigley Legacy vs LiDAR'
    },
    # Add more pairs...
]
```

2. Run the script:

```bash
python batch_processing.py
```

**Output**: Results organized in `batch_results/` directory with one subdirectory per analysis.

**Key features**:
- Automatic configuration merging with defaults
- Validation before processing
- Error handling continues batch if one fails
- Summary report at end

## Python API Usage

Complete workflow using GeoElastix as a Python library.

**File**: `python_api_example.py`

**What it demonstrates**:
- Step-by-step API usage
- Manual control of each processing stage
- Custom output organization
- Direct access to arrays and objects

**Use case**: Integration with custom workflows or larger applications

**Workflow steps**:

1. Load input data with `RasterIO`
2. Convert to ITK images
3. Perform registration with `TwoPassRegistration`
4. Calculate displacement with displacement modules
5. Compute quality metrics
6. Save outputs
7. Create visualizations
8. Generate custom report

**How to run**:

```bash
python python_api_example.py
```

**Customization ideas**:
- Add custom preprocessing
- Implement different quality thresholds
- Create custom visualizations
- Export to additional formats
- Integrate with database or web service

## Additional Example Ideas

### Method Comparison

Compare different registration methods on same data:

```bash
# Non-Affine (default)
geoelastix register -f dem_new.tif -m dem_old.tif --method NA --job-id comparison_na

# Affine
geoelastix register -f dem_new.tif -m dem_old.tif --method AF --job-id comparison_af

# Rigid
geoelastix register -f dem_new.tif -m dem_old.tif --method RG --job-id comparison_rg
```

Then compare quality metrics and displacement results across methods.

### Custom Parameters

Create and use custom elastix parameter file:

1. Copy default parameter file:
```bash
geoelastix show-params NA > custom_params.txt
```

2. Edit `custom_params.txt` to adjust parameters

3. Use in configuration:
```yaml
registration:
  parameter_file: "./custom_params.txt"
```

### ROI Processing

Process only a region of interest:

```bash
# Clip DEMs to ROI first
gdalwarp -te xmin ymin xmax ymax input.tif roi.tif

# Or use cutline shapefile
gdalwarp -cutline roi_polygon.shp input.tif roi.tif

# Process ROI
geoelastix register -f roi_new.tif -m roi_old.tif --job-id roi_analysis
```

### Time Series Animation

Create animation from multiple time periods:

1. Process all time periods with batch script
2. Extract displacement magnitude maps
3. Use external tools to create animation:

```bash
# Using ImageMagick
convert -delay 100 output_*/visualization/displacement_magnitude_contour.png animation.gif
```

### Integration with QGIS

Load GeoElastix outputs in QGIS:

1. Open QGIS
2. Add raster layers: `displacement_x.tif`, `displacement_y.tif`, `displacement_z.tif`
3. Style with graduated colors
4. Create quiver plot using Vector Field Renderer:
   - Raster → Miscellaneous → Build Virtual Raster (combine X and Y)
   - Style with "Arrow" renderer

### Validation with GPS

Compare displacement results with GPS measurements:

```python
from geoelastix.io import RasterIO
import numpy as np

# Load displacement
disp_data = RasterIO.read_raster("displacement_magnitude.tif")

# GPS coordinates and measurements
gps_points = [
    {'x': 500100, 'y': 4500200, 'measured_displacement': 2.5},
    {'x': 500150, 'y': 4500250, 'measured_displacement': 3.1},
    # ...
]

# Extract displacement at GPS points
# (convert coordinates to pixel indices)
# Compare with GPS measurements
```

## Tips for Creating Your Own Examples

1. **Start Simple**: Begin with basic CLI commands before API
2. **Document Well**: Add comments explaining each step
3. **Handle Errors**: Include try-except blocks
4. **Test First**: Run on small subset before full data
5. **Save Configs**: Keep configuration files for reproducibility
6. **Version Data**: Track which DEMs were used
7. **Validate Results**: Cross-check with known values or independent data

## Example Data

The Wrigley example includes sample data. For your own projects:

**Where to get DEMs**:
- USGS Earth Explorer: https://earthexplorer.usgs.gov/
- OpenTopography: https://opentopography.org/
- National elevation datasets (varies by country)
- Commercial providers (Maxar, Planet, etc.)
- LiDAR data from local agencies

**Data preparation**:
1. Ensure same coordinate reference system
2. Similar spatial resolution (within 2× factor)
3. Overlapping extent (>70% recommended)
4. Properly defined no-data values
5. Single-band elevation rasters

## Getting Help

- **Documentation**: See `docs/` directory
- **User Guide**: Detailed usage instructions
- **API Reference**: Complete API documentation
- **Issues**: https://github.com/yzh211/geoelastix/issues

## Contributing Examples

We welcome example contributions! If you've created a useful workflow:

1. Create a new directory in `examples/`
2. Include:
   - Python script or configuration file
   - README.md explaining the example
   - Sample data (if small) or link to data source
   - Expected output description
3. Submit pull request with clear description

Good examples to contribute:
- Integration with other tools (QGIS, ArcGIS, etc.)
- Specific use cases (glaciers, volcanoes, infrastructure)
- Advanced workflows (uncertainty analysis, time series)
- Performance optimization techniques
- Cloud processing examples

## Quick Test Script

**File**: `quick_test.py` (in project root)

**What it does**:
- Validates installation of all dependencies (NumPy, GDAL, ITK, Matplotlib)
- Tests GeoElastix module imports
- Checks for Wrigley example data files
- Optionally runs full registration workflow with visualization
- Provides interactive prompts and detailed feedback

**How to use**:

```bash
python quick_test.py
```

**Test levels**:

1. **Import Test**: Verifies all required Python packages
2. **Module Test**: Confirms GeoElastix modules load correctly
3. **Data Check**: Validates example data files exist
4. **Registration Test**: (Optional) Runs complete Wrigley workflow

**When to use**:
- After initial installation to verify setup
- After updating dependencies
- Before processing important data
- When troubleshooting installation issues

**Output**: Interactive console output with ✓/✗ indicators and optional visualization plots.

## Wrigley Test Script

**File**: `test_wrigley_registration.py` (in project root)

**What it does**:
- Automated test of complete Wrigley registration workflow
- No user interaction required (non-interactive mode)
- Validates end-to-end pipeline

**How to use**:

```bash
python test_wrigley_registration.py
```

**Use case**: Automated testing, CI/CD validation, quick verification of workflow functionality.

**Output**: Log output to console, results saved to configured output directory.

## Benchmark Script

**File**: `benchmark_speed.py` (in project root)

**What it does**:
- Measures execution time of each workflow component
- Analyzes I/O operations, ITK conversion, registration, and displacement calculation
- Estimates full workflow time based on component measurements
- Provides performance analysis and bottleneck identification

**How to use**:

```bash
python benchmark_speed.py
```

**Benchmark components**:

1. **I/O Operations**: Reading raster files with GDAL
2. **ITK Conversion**: Array to ITK image conversion
3. **Registration**: Two-pass elastix registration (core algorithm)
4. **Displacement Calculation**: Displacement field computation

**Output**: Detailed timing report showing:
- Individual component times
- Core registration percentage of total time
- Estimated full workflow time
- Performance analysis and recommendations

**When to use**:
- Evaluating hardware performance
- Comparing different systems
- Identifying performance bottlenecks
- Planning processing time for large datasets

**Sample output**:
```
BENCHMARK SUMMARY
======================================================================
I/O (read 2 rasters)        :   12.5 sec
ITK conversion (2 images)   :    2.3 sec
Registration (2-pass)       :  145.2 sec  ⭐ CORE ALGORITHM
Displacement calc (1 field) :    5.8 sec
----------------------------------------------------------------------
Core registration total     :  160.0 sec ( 2.67 min)

Estimated full workflow     :  330.0 sec ( 5.50 min)
```

## ITK Workflow Test

**File**: `test_itk_workflow.py` (in project root)

**What it does**:
- Validates ITK type definitions (itk.F for float, itk.UC for unsigned char)
- Tests array-to-ITK-image conversion
- Verifies MHD file read/write with correct types
- Tests parameter object loading

**How to use**:

```bash
python test_itk_workflow.py
```

**Tests performed**:

1. **Type Verification**: Confirms itk.F and itk.UC are available
2. **Array Conversion**: Tests data and mask conversion with correct dtypes
3. **MHD I/O**: Validates MetaImage format handling
4. **Parameter Loading**: Tests elastix parameter object creation

**When to use**:
- After ITK installation to verify correct setup
- When debugging type-related errors
- Before running ITK-dependent workflows
- When troubleshooting MHD file issues

**Output**: Test results with ✓/✗ indicators for each test, creates temporary files in `test_output/` directory.

## Using Test Scripts in Your Workflow

### Recommended Testing Sequence

**1. Initial Setup Validation**:
```bash
# Step 1: Validate ITK installation
python test_itk_workflow.py

# Step 2: Comprehensive installation check
python quick_test.py

# Step 3: (Optional) Performance baseline
python benchmark_speed.py
```

**2. Before Production Processing**:
```bash
# Quick validation
python test_wrigley_registration.py
```

**3. Troubleshooting**:
```bash
# Isolate ITK issues
python test_itk_workflow.py

# Check all dependencies
python quick_test.py
```

### Integration with Development

Test scripts can be integrated into:
- **Pre-commit hooks**: Run `test_itk_workflow.py` before commits
- **CI/CD pipelines**: Execute `test_wrigley_registration.py` in automated builds
- **Performance monitoring**: Track benchmark results over time
- **Installation validation**: Include `quick_test.py` in setup instructions

## License

All examples are licensed under Apache License 2.0, same as GeoElastix main project.
