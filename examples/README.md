# GeoElastix Examples

This directory contains example workflows demonstrating various GeoElastix features and use cases.

## Examples Overview

| Example | Description | Difficulty |
|---------|-------------|-----------|
| [wrigley/](#wrigley-landslide-example) | Complete landslide monitoring workflow | Beginner |
| [batch_processing.py](#batch-processing) | Process multiple DEM pairs in sequence | Intermediate |
| [python_api_example.py](#python-api-usage) | Use GeoElastix as Python library | Intermediate |

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
        'fixed': 'data/dem_2020.tif',
        'moving': 'data/dem_2019.tif',
        'job_id': 'analysis_2019_2020',
        'description': 'Year 2019 to 2020'
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

## License

All examples are licensed under Apache License 2.0, same as GeoElastix main project.
