# Troubleshooting Guide

Solutions to common problems encountered when using GeoElastix.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Data Loading Problems](#data-loading-problems)
- [Registration Failures](#registration-failures)
- [Memory and Performance](#memory-and-performance)
- [Output and Visualization](#output-and-visualization)
- [Quality and Accuracy](#quality-and-accuracy)
- [Platform-Specific Issues](#platform-specific-issues)

## Installation Issues

### Problem: `ImportError: No module named 'osgeo'`

**Symptoms**: Cannot import GDAL/osgeo

**Cause**: GDAL not installed or not in Python path

**Solutions**:

```bash
# Solution 1: Install via conda (recommended)
conda install -c conda-forge gdal

# Solution 2: Reinstall with force
conda install -c conda-forge gdal --force-reinstall

# Solution 3: Set GDAL environment variable
export GDAL_DATA=$(gdal-config --datadir)

# Verify installation
python -c "from osgeo import gdal; print(gdal.__version__)"
```

### Problem: `ModuleNotFoundError: No module named 'itk'`

**Symptoms**: ITK or itk-elastix not found

**Cause**: ITK packages not installed

**Solutions**:

```bash
# Install ITK and itk-elastix
conda install -c conda-forge itk itk-elastix

# Verify installation
python -c "import itk; print(itk.Version.GetITKVersion())"
```

### Problem: `geoelastix: command not found`

**Symptoms**: CLI command not available after installation

**Cause**: Environment not activated or package not properly installed

**Solutions**:

```bash
# Solution 1: Activate environment
conda activate geoelastix

# Solution 2: Reinstall package
pip install -e . --force-reinstall

# Solution 3: Use full path
python -m geoelastix.cli.main --version

# Solution 4: Add to PATH (adjust path)
export PATH=$PATH:$HOME/anaconda3/envs/geoelastix/bin
```

### Problem: Package installation fails with dependency conflicts

**Symptoms**: Conda/pip reports conflicting package requirements

**Solutions**:

```bash
# Solution 1: Create fresh environment
conda create -n geoelastix_new python=3.10
conda activate geoelastix_new
# Install dependencies fresh

# Solution 2: Use mamba (faster solver)
conda install mamba -c conda-forge
mamba install gdal itk itk-elastix -c conda-forge

# Solution 3: Install packages one at a time
conda install -c conda-forge gdal
conda install -c conda-forge itk
conda install -c conda-forge itk-elastix
```

## Data Loading Problems

### Problem: `FileNotFoundError: Input file not found`

**Symptoms**: Cannot find input DEM files

**Solutions**:

```bash
# Use absolute paths
geoelastix register \
  --fixed /full/path/to/dem_new.tif \
  --moving /full/path/to/dem_old.tif

# Verify files exist
ls -lh /path/to/dem_new.tif

# Check working directory
pwd
```

### Problem: `ERROR 4: ... not recognized as a supported file format`

**Symptoms**: GDAL cannot open input file

**Cause**: Unsupported format or corrupted file

**Solutions**:

```bash
# Check file with gdalinfo
gdalinfo dem.tif

# Check file is not corrupted
file dem.tif

# Convert to GeoTIFF if needed
gdal_translate input.xyz output.tif -of GTiff

# Verify file is readable
python -c "from osgeo import gdal; ds = gdal.Open('dem.tif'); print(ds is not None)"
```

### Problem: `Warning: CRS not defined`

**Symptoms**: Warning about missing coordinate reference system

**Cause**: Input rasters lack CRS metadata

**Solutions**:

```bash
# Check CRS
gdalinfo dem.tif | grep "Coordinate System"

# Assign CRS if missing (adjust EPSG code)
gdal_edit.py -a_srs EPSG:32610 dem.tif

# Or create new file with CRS
gdalwarp -t_srs EPSG:32610 input.tif output_with_crs.tif
```

### Problem: `Error: CRS mismatch between fixed and moving images`

**Symptoms**: Different CRS in input files

**Cause**: DEMs have incompatible coordinate systems

**Solutions**:

```bash
# Check CRS of both files
gdalinfo dem_new.tif | grep "PROJCS\|GEOGCS"
gdalinfo dem_old.tif | grep "PROJCS\|GEOGCS"

# Reproject moving image to match fixed image
gdalwarp -t_srs EPSG:32610 dem_old.tif dem_old_reprojected.tif

# Then use reprojected file
geoelastix register \
  --fixed dem_new.tif \
  --moving dem_old_reprojected.tif
```

### Problem: `Error: Input images have different dimensions`

**Symptoms**: Fixed and moving images have different sizes

**Cause**: DEMs have different extents or resolutions

**Solutions**:

```bash
# Check dimensions
gdalinfo dem_new.tif | grep "Size is"
gdalinfo dem_old.tif | grep "Size is"

# Option 1: Resample to match resolution
gdalwarp -tr 1.0 1.0 -r bilinear dem_old.tif dem_old_resampled.tif

# Option 2: Clip to common extent (find extent first)
gdalinfo dem_new.tif  # Note corner coordinates
gdalwarp -te xmin ymin xmax ymax dem_old.tif dem_old_clipped.tif

# Option 3: Let GeoElastix handle it (may take longer)
# Just run registration - different sizes are supported
```

## Registration Failures

### Problem: Registration produces poor results

**Symptoms**: Displacement maps show unrealistic patterns, registered image poorly aligned

**Diagnosis**:
1. Check quality metrics in report.txt
2. Visual inspection of registered image
3. Review displacement contour plots

**Solutions**:

```yaml
# Solution 1: Try different registration method
registration:
  method: "AF"  # Try Affine instead of NA

# Solution 2: Check input data quality
# - Are DEMs from same source/processing?
# - Is there sufficient overlap (>70%)?
# - Are there large no-data regions?

# Solution 3: Adjust metric
registration:
  method: "NA"
  metric: "MI"  # Try MI instead of NCC

# Solution 4: Check for outliers
# Use gdalinfo to check min/max values
gdalinfo -stats dem.tif
```

### Problem: Registration fails with "Optimization terminated early"

**Symptoms**: Registration stops before completing

**Cause**: Optimizer cannot find good solution

**Solutions**:

```bash
# Solution 1: Try simpler transformation
geoelastix register --fixed dem_new.tif --moving dem_old.tif --method AF

# Solution 2: Pre-align data using rigid registration
# Run RG first, then use result for NA registration
geoelastix register --fixed dem_new.tif --moving dem_old.tif --method RG --job-id prealign
geoelastix register --fixed dem_new.tif --moving ./output/prealign_*/registered/registered_moving.tif --method NA

# Solution 3: Check for extreme values
# Clip to reasonable elevation range
gdal_calc.py -A dem.tif --outfile dem_clipped.tif --calc="A*(A>0)*(A<5000)"
```

### Problem: `Error: No valid pixels in overlap region`

**Symptoms**: Registration cannot proceed due to no-data

**Cause**: Input images don't overlap or have extensive no-data

**Solutions**:

```bash
# Check overlap visually in QGIS or similar

# Check no-data coverage
gdalinfo -stats dem_new.tif  # Look at STATISTICS_VALID_PERCENT
gdalinfo -stats dem_old.tif

# Fill small no-data gaps
gdal_fillnodata.py -md 100 input.tif output_filled.tif

# Clip to region with good overlap
gdalwarp -te xmin ymin xmax ymax -cutline overlap_polygon.shp input.tif output_clipped.tif
```

### Problem: Registration is extremely slow

**Symptoms**: Registration takes hours or hangs

**Cause**: Large dataset, complex deformation, or parameter issues

**Solutions**:

```yaml
# Solution 1: Enable tiling (automatic for large images)
processing:
  tile_threshold: 3000  # Lower threshold to force tiling
  tile_overlap: 50      # Reduce overlap

# Solution 2: Use faster method
registration:
  method: "AF"  # Much faster than NA

# Solution 3: Reduce iterations (custom parameter file)
# Edit parameter file to reduce MaximumNumberOfIterations

# Solution 4: Test on subset first
# Clip to small region for testing
gdalwarp -te xmin ymin xmax ymax input.tif test_subset.tif
```

## Memory and Performance

### Problem: `MemoryError` during processing

**Symptoms**: Python crashes with out of memory error

**Cause**: Insufficient RAM for dataset size

**Solutions**:

```yaml
# Solution 1: Enable/force tiling
processing:
  tile_threshold: 3000
  tile_size: 3000

# Solution 2: Close other applications

# Solution 3: Increase system swap space

# Solution 4: Process at lower resolution
# Downsample temporarily for testing
gdalwarp -tr 5.0 5.0 -r average input.tif input_downsampled.tif
```

### Problem: Processing uses too much disk space

**Symptoms**: Disk fills up during processing

**Cause**: Large intermediate files or uncompressed outputs

**Solutions**:

```yaml
# Use compression
output:
  compression: "LZW"  # Or "DEFLATE"

# Disable large outputs if not needed
visualization:
  generate_plots: false

# Clean up intermediate files after processing
# Delete registered/ directory if only displacement needed
```

### Problem: Multi-threading not working

**Symptoms**: CPU usage low, processing slow

**Cause**: Threading not enabled or limited

**Solutions**:

```yaml
# Increase thread count
processing:
  num_threads: 8  # Set to number of CPU cores

# Check CPU usage during processing
# In another terminal:
top  # or htop on Linux

# Verify ITK threading
python -c "import itk; print(itk.MultiThreaderBase.GetGlobalMaximumNumberOfThreads())"
```

## Output and Visualization

### Problem: `Error writing output file: Permission denied`

**Symptoms**: Cannot write to output directory

**Cause**: Insufficient permissions or disk full

**Solutions**:

```bash
# Check permissions
ls -ld ./output

# Create output directory with correct permissions
mkdir -p ./output
chmod 755 ./output

# Check disk space
df -h .

# Use different output directory
geoelastix register --config config.yaml --output /tmp/geoelastix_output
```

### Problem: Visualization plots are blank or corrupted

**Symptoms**: PNG files are empty or show errors

**Cause**: Matplotlib backend issues or data range problems

**Solutions**:

```python
# Check data range
from geoelastix.io import RasterIO
data = RasterIO.read_raster("displacement_x.tif")
print(f"Min: {data['array'].min()}, Max: {data['array'].max()}")

# If all values are the same, no displacement detected
# Check registration quality

# Matplotlib backend issue
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
```

```yaml
# Disable problematic plot types
visualization:
  plot_types: ["quiver"]  # Only generate quiver plots
```

### Problem: Output files have wrong geospatial metadata

**Symptoms**: Output TIFFs don't align with input in GIS

**Cause**: Geotransform or CRS not properly copied

**Solutions**:

```bash
# Check geospatial metadata
gdalinfo displacement_x.tif

# If CRS missing, assign manually
gdal_edit.py -a_srs EPSG:32610 displacement_x.tif

# If geotransform wrong, recreate output using API
# (See API.md for manual workflow example)
```

### Problem: Cannot open output files in GIS software

**Symptoms**: QGIS/ArcGIS cannot read output files

**Cause**: Corrupt file or unsupported format variant

**Solutions**:

```bash
# Verify file integrity
gdalinfo displacement_x.tif

# If corrupt, regenerate from ASC file
gdal_translate displacement_x.asc displacement_x_fixed.tif

# Or ensure GeoTIFF compatibility
gdal_translate -co "TILED=YES" -co "COMPRESS=LZW" input.tif output_compatible.tif
```

## Quality and Accuracy

### Problem: Large RMSE in quality metrics

**Symptoms**: RMSE > 10 m in report

**Cause**: Poor registration or low input data quality

**Solutions**:

```bash
# Check input data quality
gdalinfo -stats dem_new.tif
gdalinfo -stats dem_old.tif

# Check for artifacts or anomalies
# View in QGIS with hillshade

# Try different method
geoelastix register --config config.yaml --method AF

# Check elevation units
# Ensure both DEMs use same units (meters, not feet)
```

### Problem: Low correlation or Dice coefficient

**Symptoms**: Correlation < 0.5 or Dice < 0.7

**Cause**: Poor overlap, excessive no-data, or failed registration

**Solutions**:

```bash
# Check overlap
# View both DEMs in QGIS to verify spatial overlap

# Check no-data coverage
gdalinfo -stats dem_new.tif | grep VALID_PERCENT
gdalinfo -stats dem_old.tif | grep VALID_PERCENT

# If <70% valid, consider filling no-data or clipping
gdal_fillnodata.py input.tif output_filled.tif
```

### Problem: Displacement values seem unrealistic

**Symptoms**: Extremely large or small displacement values

**Diagnosis**:

```bash
# Check units of CRS
gdalinfo dem_new.tif | grep "UNIT"

# Check displacement statistics
# In report.txt, review mean, max displacement values

# View displacement maps in QGIS
# Use graduated symbology to check value distribution
```

**Common Causes**:
1. **Wrong CRS**: Geographic (degrees) instead of projected (meters)
   - Solution: Reproject to UTM or other projected CRS

2. **Registration Failure**: Poor alignment
   - Solution: Try different method or check input quality

3. **Scale Issues**: DEMs have different units (meters vs feet)
   - Solution: Ensure both DEMs use same elevation units

4. **Large Actual Deformation**: Landslide with genuinely large displacement
   - This is acceptable for landslide monitoring
   - Validate with field observations if available

### Problem: No displacement detected (all zeros)

**Symptoms**: Displacement maps show zero values everywhere

**Cause**: Images identical or registration not applied

**Solutions**:

```bash
# Check if input images are actually different
gdalinfo -stats dem_new.tif
gdalinfo -stats dem_old.tif
# Compare STATISTICS_MEAN, _MIN, _MAX

# If truly identical, no displacement expected

# Check acquisition dates
# Ensure DEMs are from different time periods

# Try manual verification in QGIS
# Load both DEMs, toggle visibility to see differences
```

## Platform-Specific Issues

### Windows

#### Problem: Long path names cause errors

**Symptoms**: `FileNotFoundError` with long paths

**Solution**:

```bash
# Use shorter paths
# Move data closer to C:\ drive root
mkdir C:\geoelastix_data
# Copy DEMs there

# Or enable long path support (Windows 10+)
# Modify registry: LongPathsEnabled = 1
```

#### Problem: DLL load failed

**Symptoms**: `ImportError: DLL load failed`

**Solution**:

```bash
# Install Visual C++ Redistributable
# Download from Microsoft website

# Reinstall packages
conda install -c conda-forge gdal --force-reinstall
```

### Linux

#### Problem: `libgdal.so: cannot open shared object file`

**Symptoms**: GDAL library not found

**Solution**:

```bash
# Install system GDAL libraries
sudo apt-get install libgdal-dev

# Or ensure conda libraries in LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# Add to ~/.bashrc for persistence
echo 'export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
```

#### Problem: Permission denied errors

**Symptoms**: Cannot write files or execute commands

**Solution**:

```bash
# Check directory permissions
ls -ld output/

# Create with proper permissions
mkdir -p output
chmod 755 output

# Don't run as root unless necessary
# Use regular user account
```

### macOS

#### Problem: `xcrun: error: invalid active developer path`

**Symptoms**: Error when running commands

**Solution**:

```bash
# Install Xcode command line tools
xcode-select --install
```

#### Problem: GDAL cannot find proj.db

**Symptoms**: `PROJ: proj_create_from_database: Cannot find proj.db`

**Solution**:

```bash
# Set PROJ_LIB environment variable
export PROJ_LIB=$CONDA_PREFIX/share/proj

# Add to shell profile
echo 'export PROJ_LIB=$CONDA_PREFIX/share/proj' >> ~/.zshrc  # or ~/.bash_profile
```

## Getting Additional Help

### Diagnostic Information

When reporting issues, include:

```bash
# GeoElastix version
geoelastix --version

# Python and package versions
python --version
conda list gdal
conda list itk
conda list numpy

# System information
uname -a  # Linux/macOS
systeminfo  # Windows

# GDAL configuration
gdalinfo --version
gdalinfo --formats

# Error messages (full traceback)
geoelastix register --config config.yaml --log-level DEBUG
```

### Where to Get Help

1. **Documentation**: Read the [User Guide](USER_GUIDE.md) and [API Reference](API.md)

2. **Examples**: Review working examples in `examples/` directory

3. **GitHub Issues**: Search or create issue at https://github.com/yzh211/geoelastix/issues
   - Search existing issues first
   - Provide diagnostic information
   - Include minimal reproducible example

4. **Community**: Check ITK and elastix documentation for registration-specific issues
   - ITK: https://itk.org/
   - Elastix: https://elastix.lumc.nl/

### Debug Mode

Run with debug logging for detailed output:

```bash
geoelastix register --config config.yaml --log-level DEBUG
```

Check log file in output directory:
```bash
cat output/job_id_*/logs/geoelastix.log
```

## Common Error Messages

### `ValueError: Configuration validation failed`

Check configuration file syntax and required fields:

```bash
geoelastix validate-config config.yaml
```

### `RuntimeError: Registration optimization failed`

Try different registration method or check input data quality.

### `KeyError: 'displacement_x'`

Displacement calculation failed. Check registration completed successfully.

### `OSError: [Errno 28] No space left on device`

Free up disk space or use different output directory.

## Preventing Issues

### Best Practices

1. **Test First**: Always test on small subset before processing large datasets

2. **Check Inputs**: Verify input files with `gdalinfo` before processing

3. **Use Absolute Paths**: Avoid relative paths that may change

4. **Save Configurations**: Keep YAML config files for reproducibility

5. **Monitor Resources**: Check memory and disk space during processing

6. **Validate Outputs**: Review quality metrics and visualizations after processing

7. **Version Control**: Document GeoElastix version and parameters used

8. **Backup Data**: Keep original DEMs safe, work on copies

### Recommended Workflow

```bash
# 1. Verify environment
conda activate geoelastix
geoelastix --version

# 2. Check input data
gdalinfo dem_new.tif
gdalinfo dem_old.tif

# 3. Test on small region
gdalwarp -te xmin ymin xmax ymax dem_new.tif test_new.tif
gdalwarp -te xmin ymin xmax ymax dem_old.tif test_old.tif
geoelastix register -f test_new.tif -m test_old.tif --job-id test

# 4. Review test results
# Check quality metrics, visualizations

# 5. Process full dataset
geoelastix register --config production_config.yaml

# 6. Validate outputs
# Review reports, load outputs in GIS
```

## Still Having Problems?

If you've tried the solutions above and still have issues:

1. Check if it's a known issue: https://github.com/yzh211/geoelastix/issues

2. Create a new issue with:
   - Clear description of problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Diagnostic information (versions, system info)
   - Minimal example data (if possible)

3. Consider consulting with:
   - GIS/remote sensing experts for data preparation
   - System administrators for installation/environment issues
   - Domain experts for interpretation of results
