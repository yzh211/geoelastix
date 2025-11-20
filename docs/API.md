# API Reference

Complete API reference for using GeoElastix as a Python library.

## Table of Contents

- [Overview](#overview)
- [I/O Module](#io-module)
- [Registration Module](#registration-module)
- [Displacement Module](#displacement-module)
- [Validation Module](#validation-module)
- [Visualization Module](#visualization-module)
- [Utilities Module](#utilities-module)
- [Complete Examples](#complete-examples)

## Overview

GeoElastix can be used as a Python library for custom workflows:

```python
import geoelastix
from geoelastix.io import RasterIO
from geoelastix.registration import TwoPassRegistration
from geoelastix.displacement import HorizontalDisplacement
```

## I/O Module

### RasterIO

Read and write geospatial raster data.

#### read_raster()

Read a GeoTIFF or ASC file.

```python
from geoelastix.io import RasterIO

data = RasterIO.read_raster("dem.tif")
# Returns dict with:
#   'array': numpy array
#   'mask': boolean mask (True = valid)
#   'nodata': no-data value
#   'crs': CRS object
#   'geotransform': GDAL geotransform
#   'shape': (height, width)
```

**Parameters**:
- `file_path` (str or Path): Path to raster file

**Returns**:
- `dict`: Dictionary with raster data and metadata

**Example**:
```python
from pathlib import Path
from geoelastix.io import RasterIO

# Read DEM
dem_path = Path("data/dem_2022.tif")
data = RasterIO.read_raster(dem_path)

# Access data
elevation = data['array']
valid_mask = data['mask']
nodata = data['nodata']
crs = data['crs']

print(f"Shape: {data['shape']}")
print(f"CRS: {crs}")
print(f"No-data value: {nodata}")
print(f"Valid pixels: {valid_mask.sum()} / {valid_mask.size}")
```

#### write_geotiff()

Write numpy array to GeoTIFF file.

```python
RasterIO.write_geotiff(
    output_path="displacement_x.tif",
    array=displacement_x,
    geotransform=geotransform,
    crs=crs,
    nodata_value=-9999,
    compression='LZW'
)
```

**Parameters**:
- `output_path` (str or Path): Output file path
- `array` (numpy.ndarray): Data to write
- `geotransform` (tuple): GDAL geotransform (6 values)
- `crs` (str or CRS): Coordinate reference system
- `nodata_value` (float, optional): No-data value
- `compression` (str, optional): Compression method (LZW, DEFLATE, etc.)

**Example**:
```python
import numpy as np
from geoelastix.io import RasterIO

# Create sample data
displacement = np.random.randn(1000, 1000).astype(np.float32)

# Define geotransform (xmin, xres, 0, ymax, 0, -yres)
geotransform = (500000, 1.0, 0, 4500000, 0, -1.0)

# Write to file
RasterIO.write_geotiff(
    "output.tif",
    displacement,
    geotransform,
    "EPSG:32610",  # UTM Zone 10N
    nodata_value=-9999,
    compression='LZW'
)
```

#### write_asc()

Write numpy array to ESRI ASCII Grid format.

```python
RasterIO.write_asc(
    output_path="displacement_x.asc",
    array=displacement_x,
    geotransform=geotransform,
    nodata_value=-9999
)
```

#### array_to_itk_image()

Convert numpy array to ITK image for registration.

```python
itk_image = RasterIO.array_to_itk_image(
    array,
    spacing=(1.0, 1.0)
)
```

**Parameters**:
- `array` (numpy.ndarray): Input array
- `spacing` (tuple, optional): Pixel spacing (x, y)

**Returns**:
- ITK image object

#### itk_image_to_array()

Convert ITK image back to numpy array.

```python
array = RasterIO.itk_image_to_array(itk_image)
```

### NoDataHandler

Handle no-data values in rasters.

#### detect_nodata()

Automatically detect no-data value from array.

```python
from geoelastix.io import NoDataHandler

nodata = NoDataHandler.detect_nodata(array)
```

#### create_mask()

Create boolean mask from no-data values.

```python
mask = NoDataHandler.create_mask(
    array,
    nodata_value=-9999,
    tolerance=1e-6
)
# mask: True = valid, False = no-data
```

### CRSManager

Manage coordinate reference systems.

#### get_pixel_size()

Extract pixel spacing from dataset.

```python
from geoelastix.io import CRSManager
from osgeo import gdal

ds = gdal.Open("dem.tif")
pixel_spacing = CRSManager.get_pixel_size(ds)
# Returns: (x_spacing, y_spacing)
```

#### validate_crs_pair()

Validate CRS compatibility between two datasets.

```python
ds1 = gdal.Open("dem1.tif")
ds2 = gdal.Open("dem2.tif")

CRSManager.validate_crs_pair(
    ds1, ds2,
    raise_on_mismatch=True  # Raises error if incompatible
)
```

## Registration Module

### ElastixWrapper

Low-level wrapper for ITK-Elastix registration.

```python
from geoelastix.registration import ElastixWrapper

wrapper = ElastixWrapper(parameter_object)
result = wrapper.register(
    fixed_image,
    moving_image,
    fixed_mask=None,
    moving_mask=None
)
```

**Parameters**:
- `parameter_object`: ITK parameter object
- `fixed_image`: ITK image (reference)
- `moving_image`: ITK image (to be registered)
- `fixed_mask` (optional): ITK mask image
- `moving_mask` (optional): ITK mask image

**Returns**:
- `dict`: {'registered_image': ITK image, 'transform_parameters': parameter object}

### TwoPassRegistration

High-level two-pass registration interface.

```python
from geoelastix.registration import TwoPassRegistration, ParameterManager

# Create parameter object
param_obj = ParameterManager.create_parameter_object(method='NA')

# Initialize two-pass registration
two_pass = TwoPassRegistration(param_obj)

# Perform registration
result = two_pass.register(
    fixed_image,
    moving_image,
    fixed_mask=None,
    moving_mask=None,
    log_to_console=False
)
```

**Returns**:
- `dict`: {'registered_image', 'transform_parameters', 'pass1_image', 'pass1_parameters'}

**Complete Example**:
```python
from pathlib import Path
from geoelastix.io import RasterIO, CRSManager
from geoelastix.registration import TwoPassRegistration, ParameterManager
import itk

# Read input data
fixed_data = RasterIO.read_raster("dem_2022.tif")
moving_data = RasterIO.read_raster("dem_2021.tif")

# Get pixel spacing
from osgeo import gdal
ds = gdal.Open("dem_2022.tif")
pixel_spacing = CRSManager.get_pixel_size(ds)

# Convert to ITK
fixed_itk = RasterIO.array_to_itk_image(fixed_data['array'], pixel_spacing)
moving_itk = RasterIO.array_to_itk_image(moving_data['array'], pixel_spacing)

# Create masks
fixed_mask = itk.image_from_array(fixed_data['mask'].astype('uint8'))
moving_mask = itk.image_from_array(moving_data['mask'].astype('uint8'))

# Create parameter object (NA method)
param_obj = ParameterManager.create_parameter_object(method='NA')

# Register
two_pass = TwoPassRegistration(param_obj)
result = two_pass.register(
    fixed_itk,
    moving_itk,
    fixed_mask=fixed_mask,
    moving_mask=moving_mask
)

# Extract result
registered_image = result['registered_image']
transform_params = result['transform_parameters']

# Convert back to numpy
registered_array = RasterIO.itk_image_to_array(registered_image)

# Save result
RasterIO.write_geotiff(
    "registered.tif",
    registered_array,
    fixed_data['geotransform'],
    fixed_data['crs']
)
```

### ParameterManager

Manage elastix parameter files.

#### create_parameter_object()

Create parameter object for registration.

```python
from geoelastix.registration import ParameterManager

# Use default method
param_obj = ParameterManager.create_parameter_object(method='NA')

# Use custom parameter file
param_obj = ParameterManager.create_parameter_object(
    custom_file="custom_params.txt"
)
```

**Parameters**:
- `method` (str, optional): Registration method ('NA', 'AF', 'RG', 'TS')
- `custom_file` (str, optional): Path to custom parameter file

**Returns**:
- ITK parameter object

#### list_available_methods()

List available registration methods.

```python
methods = ParameterManager.list_available_methods()
# Returns: {'NA': 'Non-Affine (BSpline) Registration', ...}
```

## Displacement Module

### HorizontalDisplacement

Calculate horizontal (X, Y) displacement from deformation field.

#### compute_from_transform()

Extract horizontal displacement from elastix transform.

```python
from geoelastix.displacement import HorizontalDisplacement

result = HorizontalDisplacement.compute_from_transform(
    registered_image,
    transform_parameters,
    spacing=(1.0, 1.0)
)

displacement_x = result['displacement_x']
displacement_y = result['displacement_y']
```

**Parameters**:
- `registered_image`: ITK registered image
- `transform_parameters`: ITK transform parameters
- `spacing` (tuple, optional): Pixel spacing

**Returns**:
- `dict`: {'displacement_x': array, 'displacement_y': array, 'deformation_field': ITK image}

#### get_statistics()

Calculate displacement statistics.

```python
stats = HorizontalDisplacement.get_statistics(
    displacement_x,
    displacement_y,
    mask=valid_mask
)

print(f"Mean X displacement: {stats['x_mean']:.2f} m")
print(f"Mean Y displacement: {stats['y_mean']:.2f} m")
print(f"Max X displacement: {stats['x_max']:.2f} m")
```

**Returns**:
- `dict`: Statistics including mean, std, min, max for X and Y

### VerticalDisplacement

Calculate vertical (Z) displacement from elevation difference.

#### compute_from_arrays()

Calculate vertical displacement from fixed and registered DEMs.

```python
from geoelastix.displacement import VerticalDisplacement

result = VerticalDisplacement.compute_from_arrays(
    fixed_array,
    registered_array,
    mask=valid_mask
)

displacement_z = result['displacement_z']
stats = result['statistics']

print(f"Mean uplift: {stats['mean']:.2f} m")
print(f"Max uplift: {stats['max']:.2f} m")
print(f"Max subsidence: {stats['min']:.2f} m")
```

**Formula**: Z = Fixed - Registered
- Positive: Uplift
- Negative: Subsidence

**Returns**:
- `dict`: {'displacement_z': array, 'statistics': dict, 'classification': array}

### DisplacementMagnitude

Calculate displacement magnitudes and directions.

#### compute_horizontal_magnitude()

Calculate horizontal displacement magnitude.

```python
from geoelastix.displacement import DisplacementMagnitude

result = DisplacementMagnitude.compute_horizontal_magnitude(
    displacement_x,
    displacement_y
)

magnitude = result['magnitude']
direction = result['direction']  # Radians
statistics = result['statistics']

print(f"Mean magnitude: {statistics['mean']:.2f} m")
print(f"Max magnitude: {statistics['max']:.2f} m")
```

**Formula**: magnitude = sqrt(x² + y²)

#### compute_3d_magnitude()

Calculate 3D displacement magnitude.

```python
result = DisplacementMagnitude.compute_3d_magnitude(
    displacement_x,
    displacement_y,
    displacement_z
)

magnitude_3d = result['magnitude_3d']
```

**Formula**: magnitude_3d = sqrt(x² + y² + z²)

#### get_direction_name()

Convert direction angle to compass name.

```python
compass_name = DisplacementMagnitude.get_direction_name(
    direction_radians
)
# Returns: 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', or 'NW'
```

## Validation Module

### QualityMetrics

Compute quality metrics for registration assessment.

#### compute_all_metrics()

Compute all available quality metrics.

```python
from geoelastix.validation import QualityMetrics

metrics = QualityMetrics.compute_all_metrics(
    fixed_array,
    registered_array,
    fixed_mask=fixed_mask,
    registered_mask=registered_mask,
    image_shape=(1000, 1000)
)

print(f"RMSE: {metrics['rmse']:.2f}")
print(f"Correlation: {metrics['correlation']:.3f}")
print(f"Dice: {metrics['dice_coefficient']:.3f}")
print(f"MI: {metrics['mutual_information']:.3f}")
```

**Returns**:
- `dict`: All quality metrics

#### compute_rmse()

Calculate Root Mean Square Error.

```python
rmse = QualityMetrics.compute_rmse(
    fixed_array,
    registered_array,
    mask=valid_mask
)
```

#### compute_mutual_information()

Calculate Mutual Information.

```python
mi, nmi = QualityMetrics.compute_mutual_information(
    fixed_array,
    registered_array,
    mask=valid_mask,
    bins=256
)
```

#### compute_dice_coefficient()

Calculate Dice coefficient for mask overlap.

```python
dice = QualityMetrics.compute_dice_coefficient(
    fixed_mask,
    registered_mask
)
```

### QualityChecker

Automated quality assessment with thresholds.

```python
from geoelastix.validation import QualityChecker

# Custom thresholds
thresholds = {
    'rmse_warning': 5.0,
    'min_overlap_percent': 80.0,
    'max_nodata_percent': 20.0,
    'min_dice': 0.8,
    'min_correlation': 0.7,
    'min_mi': 0.2
}

checker = QualityChecker(thresholds=thresholds)

# Check metrics
checks = checker.check_metrics(metrics)

# Check displacement statistics
disp_checks = checker.check_displacement(displacement_stats)

# Generate report
report = checker.generate_report(metrics, displacement_stats)
print(report)
```

## Visualization Module

### QuiverPlot

Create vector field visualizations.

#### create_quiver_plot()

Generate quiver plot for displacement vectors.

```python
from geoelastix.visualization import QuiverPlot

fig = QuiverPlot.create_quiver_plot(
    displacement_x,
    displacement_y,
    subsample=50,        # Show every 50th vector
    dpi=300,
    colormap='viridis',
    mask=valid_mask
)

QuiverPlot.save_plot(fig, "quiver.png")
```

#### create_rose_diagram()

Create rose diagram showing displacement direction distribution.

```python
fig = QuiverPlot.create_rose_diagram(
    displacement_x,
    displacement_y,
    mask=valid_mask,
    bins=16  # 16 direction bins
)

QuiverPlot.save_plot(fig, "rose_diagram.png")
```

### ContourPlot

Create contour map visualizations.

#### create_contour_plot()

Generate filled contour plot.

```python
from geoelastix.visualization import ContourPlot

fig = ContourPlot.create_contour_plot(
    displacement_z,
    title="Vertical Displacement",
    dpi=300,
    colormap='RdBu_r',
    mask=valid_mask,
    center_zero=True     # Symmetric colormap centered at 0
)

ContourPlot.save_plot(fig, "contour_z.png")
```

#### create_displacement_contours()

Create multi-panel contour plots (X, Y, Z, magnitude).

```python
fig = ContourPlot.create_displacement_contours(
    displacement_x,
    displacement_y,
    displacement_z,
    magnitude=displacement_magnitude,
    mask=valid_mask,
    dpi=300
)

ContourPlot.save_plot(fig, "displacement_contours.png")
```

### ReportGenerator

Generate comprehensive reports.

```python
from geoelastix.visualization import ReportGenerator

report_gen = ReportGenerator(output_dir="./results")

# Job information
job_info = {
    'id': 'analysis_001',
    'description': 'Wrigley landslide 2021-2022',
    'timestamp': '2024-11-20 14:30:22',
    'fixed_image': 'dem_2022.tif',
    'moving_image': 'dem_2021.tif',
    'method': 'NA',
    'metric': 'NCC'
}

# Generate text report
report_path = report_gen.generate_text_report(
    job_info,
    metrics,
    displacement_stats,
    quality_checks
)

# Save metrics to JSON
json_path = report_gen.save_metrics_json(
    metrics,
    displacement_stats,
    quality_checks
)
```

## Utilities Module

### Logging

```python
from geoelastix.utils import setup_logging

logger = setup_logging(
    log_level='INFO',
    log_file='geoelastix.log'  # Optional
)

logger.info("Processing started")
logger.warning("Low overlap detected")
logger.error("Registration failed")
```

### Timestamps

```python
from geoelastix.utils import generate_timestamp

timestamp = generate_timestamp()
# Returns: '20241120_143022'
```

### Directory Management

```python
from geoelastix.utils import ensure_dir, get_output_directory

# Create directory if not exists
output_dir = ensure_dir("./results")

# Get output directory with timestamp
output_dir = get_output_directory(
    base_dir="./output",
    job_id="analysis",
    description="wrigley_landslide"
)
# Returns: ./output/analysis_wrigley_landslide_20241120_143022
```

## Complete Examples

### Example 1: Basic Registration Workflow

```python
from pathlib import Path
from geoelastix.io import RasterIO, CRSManager
from geoelastix.registration import TwoPassRegistration, ParameterManager
from geoelastix.displacement import HorizontalDisplacement, VerticalDisplacement
from geoelastix.validation import QualityMetrics
import itk
from osgeo import gdal

# 1. Load data
fixed_data = RasterIO.read_raster("dem_2022.tif")
moving_data = RasterIO.read_raster("dem_2021.tif")

# 2. Get pixel spacing
ds = gdal.Open("dem_2022.tif")
pixel_spacing = CRSManager.get_pixel_size(ds)

# 3. Convert to ITK
fixed_itk = RasterIO.array_to_itk_image(fixed_data['array'], pixel_spacing)
moving_itk = RasterIO.array_to_itk_image(moving_data['array'], pixel_spacing)
fixed_mask = itk.image_from_array(fixed_data['mask'].astype('uint8'))
moving_mask = itk.image_from_array(moving_data['mask'].astype('uint8'))

# 4. Register
param_obj = ParameterManager.create_parameter_object(method='NA')
two_pass = TwoPassRegistration(param_obj)
reg_result = two_pass.register(fixed_itk, moving_itk, fixed_mask, moving_mask)

# 5. Calculate displacement
horiz_result = HorizontalDisplacement.compute_from_transform(
    reg_result['registered_image'],
    reg_result['transform_parameters'],
    pixel_spacing
)

registered_array = RasterIO.itk_image_to_array(reg_result['registered_image'])
vert_result = VerticalDisplacement.compute_from_arrays(
    fixed_data['array'],
    registered_array,
    fixed_data['mask']
)

# 6. Compute quality metrics
metrics = QualityMetrics.compute_all_metrics(
    fixed_data['array'],
    registered_array,
    fixed_data['mask'],
    moving_data['mask'],
    fixed_data['shape']
)

# 7. Save outputs
output_dir = Path("./output")
output_dir.mkdir(exist_ok=True)

RasterIO.write_geotiff(
    output_dir / "displacement_x.tif",
    horiz_result['displacement_x'],
    fixed_data['geotransform'],
    fixed_data['crs']
)

RasterIO.write_geotiff(
    output_dir / "displacement_z.tif",
    vert_result['displacement_z'],
    fixed_data['geotransform'],
    fixed_data['crs']
)

print("Registration complete!")
print(f"RMSE: {metrics['rmse']:.2f}")
print(f"Correlation: {metrics['correlation']:.3f}")
```

### Example 2: Batch Processing

```python
from pathlib import Path
from geoelastix.cli import ConfigParser, WorkflowOrchestrator

# Define analyses
analyses = [
    ("dem_2020.tif", "dem_2019.tif", "analysis_2019_2020"),
    ("dem_2021.tif", "dem_2020.tif", "analysis_2020_2021"),
    ("dem_2022.tif", "dem_2021.tif", "analysis_2021_2022"),
]

# Process each pair
for fixed, moving, job_id in analyses:
    print(f"\nProcessing {job_id}...")

    # Build configuration
    config = ConfigParser.merge_with_defaults({
        'job': {'id': job_id, 'output_dir': './batch_results'},
        'input': {'fixed_image': fixed, 'moving_image': moving},
        'registration': {'method': 'NA'},
        'visualization': {'generate_plots': True}
    })

    # Validate
    ConfigParser.validate_config(config)

    # Run workflow
    orchestrator = WorkflowOrchestrator(config)
    results = orchestrator.run()

    print(f"✓ {job_id} complete")
```

### Example 3: Custom Visualization

```python
import numpy as np
import matplotlib.pyplot as plt
from geoelastix.io import RasterIO
from geoelastix.displacement import DisplacementMagnitude

# Load displacement fields
disp_x_data = RasterIO.read_raster("displacement_x.tif")
disp_y_data = RasterIO.read_raster("displacement_y.tif")
disp_z_data = RasterIO.read_raster("displacement_z.tif")

# Calculate magnitude
mag_result = DisplacementMagnitude.compute_horizontal_magnitude(
    disp_x_data['array'],
    disp_y_data['array']
)

# Create custom plot
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# X displacement
im1 = axes[0, 0].imshow(disp_x_data['array'], cmap='RdBu_r', vmin=-5, vmax=5)
axes[0, 0].set_title('X Displacement (m)')
plt.colorbar(im1, ax=axes[0, 0])

# Y displacement
im2 = axes[0, 1].imshow(disp_y_data['array'], cmap='RdBu_r', vmin=-5, vmax=5)
axes[0, 1].set_title('Y Displacement (m)')
plt.colorbar(im2, ax=axes[0, 1])

# Z displacement
im3 = axes[1, 0].imshow(disp_z_data['array'], cmap='RdBu_r', vmin=-2, vmax=2)
axes[1, 0].set_title('Z Displacement (m)')
plt.colorbar(im3, ax=axes[1, 0])

# Magnitude
im4 = axes[1, 1].imshow(mag_result['magnitude'], cmap='viridis', vmin=0, vmax=10)
axes[1, 1].set_title('Horizontal Magnitude (m)')
plt.colorbar(im4, ax=axes[1, 1])

plt.tight_layout()
plt.savefig('custom_displacement_plot.png', dpi=300)
```

## Additional Resources

- **Source Code**: https://github.com/yzh211/geoelastix
- **User Guide**: [USER_GUIDE.md](USER_GUIDE.md)
- **Examples**: See `examples/` directory
- **Methodology**: [METHODOLOGY.md](METHODOLOGY.md)
