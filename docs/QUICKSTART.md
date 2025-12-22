# Quick Start Guide

Get started with GeoElastix in 5 minutes.

## Prerequisites

- GeoElastix installed (see [INSTALLATION.md](INSTALLATION.md))
- Two DEMs (Digital Elevation Models) in GeoTIFF or ASC format
- Activated conda environment: `conda activate geoelastix`

## Method 1: Command-Line Interface (Fastest)

Register two DEMs with a single command:

```bash
geoelastix register \
  --fixed GIS/wrigley_30ft_lidar.tif \
  --moving GIS/wrigley_30ft_legacy.tif \
  --job-id my_analysis \
  --output ./results
```

**What it does**:
- Registers `wrigley_30ft_legacy.tif` (older) to `wrigley_30ft_lidar.tif` (newer)
- Calculates X, Y, Z displacement
- Generates visualization plots
- Saves results to `./results/my_analysis_TIMESTAMP/`

## Method 2: Configuration File (Recommended)

For more control, use a configuration file:

### Step 1: Create Configuration Template

```bash
geoelastix create-config --output myconfig.yaml
```

### Step 2: Edit Configuration

Open `myconfig.yaml` and update these essential fields:

```yaml
job:
  id: "wrigley_analysis"
  output_dir: "./output"

input:
  fixed_image: "./GIS/wrigley_30ft_lidar.tif"    # Your reference DEM
  moving_image: "./GIS/wrigley_30ft_legacy.tif"   # Your moving DEM

registration:
  method: "NA"                           # Use default Non-Affine method
```

### Step 3: Run Analysis

```bash
geoelastix register --config myconfig.yaml
```

## Understanding the Results

After processing completes, find results in the output directory:

```
output/wrigley_analysis_20241120_143022/
├── displacement/
│   ├── displacement_x.tif          # East-West movement
│   ├── displacement_y.tif          # North-South movement
│   ├── displacement_z.tif          # Vertical movement
│   └── displacement_magnitude.tif  # Total horizontal displacement
├── visualization/
│   ├── horizontal_quiver.png       # Vector field showing movement
│   ├── displacement_x_contour.png  # Contour maps
│   ├── displacement_y_contour.png
│   ├── displacement_z_contour.png
│   └── displacement_magnitude_contour.png
├── registered/
│   └── registered_moving.tif       # Registered (aligned) moving image
└── report.txt                       # Quality metrics and statistics
```

### Key Files to Review

1. **report.txt**: Quality metrics and displacement statistics
2. **displacement/*.tif**: Displacement rasters (open in QGIS/ArcGIS)
3. **visualization/*.png**: Visual summary of results

## Interpreting Displacement Values

Open displacement rasters in GIS software:

### displacement_x.tif (East-West)
- **Positive values** (red): Eastward movement
- **Negative values** (blue): Westward movement

### displacement_y.tif (North-South)
- **Positive values** (red): Northward movement
- **Negative values** (blue): Southward movement

### displacement_z.tif (Vertical)
- **Positive values** (red): Uplift
- **Negative values** (blue): Subsidence

### displacement_magnitude.tif
- Shows total horizontal displacement magnitude
- Always positive
- Useful for identifying areas of maximum movement

## Testing Your Installation

Before processing your own data, test the installation with the quick test script:

```bash
python quick_test.py
```

**What it does**:
- Tests all required dependencies (NumPy, GDAL, ITK, Matplotlib)
- Verifies GeoElastix modules load correctly
- Checks for Wrigley example data files
- Optionally runs full registration test with visualization

This interactive script helps identify installation issues and validates your setup.

## Example: Wrigley Landslide

Try the included Wrigley landslide example:

```bash
cd examples/wrigley
geoelastix register --config config_wrigley.yaml
```

Or use the simple test script:

```bash
python test_wrigley_registration.py
```

This processes two DEMs from the Wrigley landslide site and generates complete displacement analysis.

## Common Registration Methods

Choose the method based on expected deformation:

### NA - Non-Affine [DEFAULT]
```bash
geoelastix register -f new.tif -m old.tif --method NA
```
- **Best for**: Landslide monitoring (recommended)
- **Handles**: Complex, non-linear deformations
- **Speed**: Slower but most accurate

### AF - Affine
```bash
geoelastix register -f new.tif -m old.tif --method AF
```
- **Best for**: Moderate deformations
- **Handles**: Linear transformations
- **Speed**: Faster than NA

### RG - Rigid
```bash
geoelastix register -f new.tif -m old.tif --method RG
```
- **Best for**: Minimal deformation
- **Handles**: Rotation and translation only
- **Speed**: Very fast

## Troubleshooting

### "Command not found"
```bash
# Ensure environment is activated
conda activate geoelastix

# Verify installation
geoelastix --version
```

### "File not found"
```bash
# Use absolute paths
geoelastix register \
  --fixed /full/path/to/dem_new.tif \
  --moving /full/path/to/dem_old.tif
```

### Poor registration results
```bash
# Try different method
geoelastix register -f new.tif -m old.tif --method AF

# Check input data quality
gdalinfo dem_new.tif
gdalinfo dem_old.tif
```

### Memory errors
- Large DEMs are automatically tiled (> 5000×5000 pixels)
- Close other applications to free memory
- See [USER_GUIDE.md](USER_GUIDE.md) for tiling options

## Next Steps

1. **Review quality metrics** in `report.txt`
2. **Open displacement maps** in QGIS or ArcGIS
3. **Read the User Guide** for advanced options: [USER_GUIDE.md](USER_GUIDE.md)
4. **Explore examples** in `examples/` directory
5. **Learn about methods** in [METHODOLOGY.md](METHODOLOGY.md)

## Getting Help

- List available methods: `geoelastix list-methods`
- Show parameter details: `geoelastix show-params NA`
- Validate config: `geoelastix validate-config myconfig.yaml`
- Full documentation: See `docs/` directory
- Issues: https://github.com/yzh211/geoelastix/issues

## Tips for Success

1. **Use projected CRS**: Ensure DEMs use projected coordinate system (e.g., UTM)
2. **Start with NA method**: Best for landslide monitoring
3. **Check overlap**: DEMs should overlap by > 70%
4. **Review quality metrics**: Always check RMSE, correlation, and Dice coefficient
5. **Visual inspection**: Review displacement maps and registered image
6. **Save configurations**: Keep YAML files for reproducibility

Happy analyzing!
