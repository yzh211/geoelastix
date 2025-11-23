# Methodology and Algorithms

Technical documentation of the methods and algorithms used in GeoElastix.

## Table of Contents

- [Overview](#overview)
- [Image Registration](#image-registration)
- [Displacement Calculation](#displacement-calculation)
- [Quality Assessment](#quality-assessment)
- [Large Dataset Processing](#large-dataset-processing)
- [Mathematical Foundations](#mathematical-foundations)
- [Algorithm Performance](#algorithm-performance)

## Overview

GeoElastix implements a comprehensive workflow for analyzing ground displacement from multi-temporal Digital Elevation Models (DEMs). The workflow consists of four main stages:

1. **Image Registration**: Align temporal DEMs using intensity-based registration
2. **Displacement Calculation**: Extract 3D displacement vectors from registration results
3. **Quality Assessment**: Compute metrics to evaluate registration quality
4. **Visualization**: Generate plots and reports for interpretation

## Image Registration

### Registration Framework

GeoElastix uses **ITK-Elastix**, a widely-used medical image registration framework adapted for geospatial applications. The registration process optimizes a transformation that aligns two images by maximizing a similarity metric.

### Registration Components

The registration consists of three key components:

1. **Transformation Model**: Defines how pixels can be moved
2. **Similarity Metric**: Measures how well images are aligned
3. **Optimizer**: Searches for optimal transformation parameters

### Transformation Models

#### Non-Affine (NA) - BSpline [DEFAULT]

**Description**: Free-form deformation using cubic B-splines.

**Mathematical Model**:
```
T(x) = x + Σ B_i(x) * p_i
```
where:
- `x` is the pixel position
- `B_i` are B-spline basis functions
- `p_i` are control point parameters

**Characteristics**:
- Most flexible transformation
- Can model complex, spatially-varying deformations
- Control point grid defines deformation resolution
- Default: 16×16 control point grid

**Best for**: Landslide monitoring with complex, non-linear ground deformation

**Parameters**:
- Grid spacing: Determines deformation smoothness
- Multi-resolution pyramid: Coarse-to-fine optimization
- Iterations: 500-1000 per resolution level

#### Affine (AF)

**Description**: Global linear transformation.

**Mathematical Model**:
```
T(x) = A * x + t
```
where:
- `A` is a 2×2 affine matrix (rotation, scaling, shearing)
- `t` is a translation vector
- `x` is the pixel position

**Degrees of Freedom**: 6 (2 translation, 1 rotation, 2 scaling, 1 shearing)

**Best for**: Regional-scale deformations or initial alignment

#### Rigid/Euler (RG)

**Description**: Rotation and translation only, preserves shape and size.

**Mathematical Model**:
```
T(x) = R(θ) * x + t
```
where:
- `R(θ)` is a rotation matrix
- `t` is a translation vector
- `θ` is rotation angle

**Degrees of Freedom**: 3 (2 translation, 1 rotation)

**Best for**: Pre-aligned data with minimal deformation

#### Translation (TS)

**Description**: Translation only, no rotation or deformation.

**Mathematical Model**:
```
T(x) = x + t
```
where `t` is a translation vector

**Degrees of Freedom**: 2

**Best for**: Already well-aligned images with offset correction only

### Similarity Metrics

#### Normalized Cross-Correlation (NCC) [DEFAULT]

**Description**: Measures linear correlation between image intensities.

**Formula**:
```
NCC(I_fixed, I_moving) = Σ((I_f - μ_f) * (I_m - μ_m)) / (σ_f * σ_m * N)
```
where:
- `I_f`, `I_m` are fixed and moving image intensities
- `μ_f`, `μ_m` are mean intensities
- `σ_f`, `σ_m` are standard deviations
- `N` is number of pixels

**Range**: -1 to 1 (1 = perfect correlation)

**Advantages**:
- Robust to linear intensity differences
- Good for DEMs with consistent illumination
- Fast computation

**Best for**: DEMs from same sensor/processing

#### Mutual Information (MI)

**Description**: Measures statistical dependency between images.

**Formula**:
```
MI(I_fixed, I_moving) = H(I_f) + H(I_m) - H(I_f, I_m)
```
where:
- `H(I_f)` is entropy of fixed image
- `H(I_m)` is entropy of moving image
- `H(I_f, I_m)` is joint entropy

**Normalized MI (NMI)**:
```
NMI = 2 * MI / (H(I_f) + H(I_m))
```

**Advantages**:
- Robust to non-linear intensity relationships
- Handles multi-modal data (different sensors)
- No assumption about intensity distribution

**Best for**: DEMs from different sources or processing methods

### Multi-Resolution Strategy

GeoElastix uses a multi-resolution pyramid approach:

1. **Coarse Level**: Downsampled images for fast, global alignment
2. **Medium Level**: Intermediate resolution for refinement
3. **Fine Level**: Full resolution for detailed alignment

**Benefits**:
- Faster convergence
- Better optimization landscape
- Avoids local minima
- Handles large displacements

**Default Configuration**:
- 4 resolution levels
- Downsampling factors: [8, 4, 2, 1]
- Iterations per level: [500, 500, 500, 500]

### Two-Pass Registration Strategy

GeoElastix automatically performs registration in two passes:

**Pass 1: Initial Alignment**
- Register moving image to fixed image
- Uses full parameter settings
- Produces initially aligned image

**Pass 2: Refinement**
- Register Pass 1 result to fixed image again
- Uses same parameters as Pass 1
- Produces final registered image

**Rationale**:
- Improves convergence for large deformations
- Reduces registration errors
- Increases robustness

**Note**: This is handled internally and transparent to users.

### Optimization Algorithm

**Adaptive Stochastic Gradient Descent (ASGD)**:
- Stochastic sampling of pixels for fast computation
- Adaptive step size for stable convergence
- Automatic parameter tuning

**Parameters**:
- Maximum iterations: 500-1000 per level
- Step size range: 1.0 to 0.1
- Convergence tolerance: 1e-6

## Displacement Calculation

### Horizontal Displacement (X, Y)

**Source**: Deformation field from elastix transformation

**Method**: Extract displacement vectors from transformation parameters

**For BSpline Transform**:
1. Extract deformation field from elastix output
2. Convert ITK vector image to numpy arrays
3. Separate into X (East-West) and Y (North-South) components

**For Affine/Rigid/Translation**:
1. Compute displacement at each pixel from transformation matrix
2. Formula: `displacement = T(x) - x`
3. Separate into X and Y components

**Units**: Same as input CRS (typically meters for projected coordinates)

**Sign Convention**:
- X: Positive = Eastward, Negative = Westward
- Y: Positive = Northward, Negative = Southward

### Vertical Displacement (Z)

**Source**: Direct elevation comparison

**Method**: Subtract registered moving DEM from fixed DEM

**Formula**:
```
Z_displacement = DEM_fixed - DEM_registered
```

**Rationale**:
- Vertical displacement not captured by horizontal registration
- Direct elevation comparison more accurate than transformation-based
- Accounts for true uplift/subsidence

**Units**: Same as input DEM elevation units (typically meters)

**Sign Convention**:
- Positive = Uplift (ground moved up)
- Negative = Subsidence (ground moved down)

**Classification**:
- Uplift: Z > threshold (e.g., 0.5 m)
- Subsidence: Z < -threshold
- Stable: |Z| ≤ threshold

### Displacement Magnitude

**Horizontal Magnitude**:
```
magnitude_h = sqrt(X² + Y²)
```

**3D Magnitude** (optional):
```
magnitude_3d = sqrt(X² + Y² + Z²)
```

**Direction** (azimuth):
```
θ = atan2(Y, X)  # Radians, 0 = East, π/2 = North
```

**Compass Naming**:
- N: 337.5° to 22.5°
- NE: 22.5° to 67.5°
- E: 67.5° to 112.5°
- SE: 112.5° to 157.5°
- S: 157.5° to 202.5°
- SW: 202.5° to 247.5°
- W: 247.5° to 292.5°
- NW: 292.5° to 337.5°

### Statistics

For each displacement component (X, Y, Z, magnitude):
- **Mean**: Average displacement
- **Median**: 50th percentile
- **Std Dev**: Standard deviation
- **Min/Max**: Range of values
- **P10/P90**: 10th and 90th percentiles

**Calculation**: All statistics computed only on valid pixels (excluding no-data)

## Quality Assessment

### Root Mean Square Error (RMSE)

**Formula**:
```
RMSE = sqrt(Σ(I_fixed - I_registered)² / N)
```

**Interpretation**:
- Lower is better
- Units: Same as input data (e.g., meters for DEMs)
- Typical good values: < 5 m for 1-m resolution DEMs

**Purpose**: Measures pixel-wise agreement between images

### Mutual Information (MI)

**Formula**: See [Similarity Metrics](#similarity-metrics) section

**Interpretation**:
- Higher is better
- Dimensionless (depends on image entropy)
- Typical good values: > 0.5 for NMI

**Purpose**: Measures statistical dependency (how much information images share)

### Dice Coefficient

**Formula**:
```
Dice = 2 * |A ∩ B| / (|A| + |B|)
```
where A and B are valid pixel regions

**Interpretation**:
- Range: 0 to 1 (1 = perfect overlap)
- Typical good values: > 0.8

**Purpose**: Measures overlap of valid data regions

### Pearson Correlation

**Formula**:
```
r = Σ((I_f - μ_f) * (I_m - μ_m)) / sqrt(Σ(I_f - μ_f)² * Σ(I_m - μ_m)²)
```

**Interpretation**:
- Range: -1 to 1 (1 = perfect positive correlation)
- Typical good values: > 0.7

**Purpose**: Measures linear relationship between image intensities

### Coverage Statistics

**Metrics**:
- Fixed valid percent: % of non-no-data pixels in fixed image
- Registered valid percent: % in registered image
- Overlap percent: % of pixels valid in both images

**Interpretation**:
- Higher overlap is better
- Typical good values: > 70% overlap

### Quality Thresholds

Default warning thresholds:
- RMSE > 10.0 (map units)
- Overlap < 70%
- No-data > 30%
- Dice < 0.7
- Correlation < 0.5
- Normalized MI < 0.1

**Note**: These are conservative defaults. Adjust based on your data and application.

## Large Dataset Processing

### Automatic Tiling

**Trigger**: Automatically enabled when max(height, width) > 5000 pixels

**Strategy**:
1. Divide image into overlapping tiles
2. Process each tile independently
3. Blend overlapping regions
4. Reconstruct full image

### Tile Layout

**Tile Size**: Configurable (default: 5000×5000 pixels)

**Overlap**: Configurable (default: 100 pixels)

**Grid Calculation**:
```
n_tiles_x = ceil((width - overlap) / (tile_size - overlap))
n_tiles_y = ceil((height - overlap) / (tile_size - overlap))
```

**Example**:
- Image: 12000×10000 pixels
- Tile size: 5000×5000
- Overlap: 100
- Result: 3×2 = 6 tiles

### Blending Methods

#### Average Blending (Default)
Average pixel values in overlap regions:
```
result = (tile1 + tile2) / 2
```

**Pros**: Simple, no artifacts for homogeneous regions

**Cons**: May blur edges

#### Feather Blending
Distance-weighted blending with smooth transition:
```
weight = distance_to_tile_center / max_distance
result = tile1 * weight1 + tile2 * weight2
```

**Pros**: Smooth transitions, minimal edge artifacts

**Cons**: Slightly more computation

#### First-Tile Priority
Use first tile values, discard second:
```
result = tile1  # In overlap region
```

**Pros**: Fastest, no blending artifacts

**Cons**: Potential discontinuities at tile boundaries

### Memory Optimization

**Tile Processing**:
- Process one tile at a time
- Release memory after each tile
- Reduce peak memory usage by ~N_tiles factor

**Disk I/O**:
- Read/write tiles on-demand
- Use memory-mapped arrays for large files
- Streaming processing for displacement calculation

## Mathematical Foundations

### Coordinate Systems

**Image Coordinates** (i, j):
- Origin: Top-left corner
- i: Row index (vertical, top to bottom)
- j: Column index (horizontal, left to right)

**Map Coordinates** (x, y):
- Origin: Defined by CRS
- x: Easting (horizontal, west to east)
- y: Northing (vertical, south to north)

**Geotransform**: Converts image to map coordinates
```
x = GT[0] + j * GT[1] + i * GT[2]
y = GT[3] + j * GT[4] + i * GT[5]
```
where GT = [x_origin, x_pixel_size, x_rotation, y_origin, y_rotation, y_pixel_size]

For typical north-up images:
- GT[2] = GT[4] = 0 (no rotation)
- GT[1] > 0 (x increases to east)
- GT[5] < 0 (y decreases to south)

### No-Data Handling

**Detection**:
1. Read no-data value from file metadata
2. If not specified, detect from common values: -9999, -3.4e38, NaN
3. Create boolean mask: True = valid, False = no-data

**Propagation**:
- Operations on no-data pixels produce no-data
- Masks combined using logical AND for overlapping regions
- Statistics computed only on valid pixels

**Formula**:
```
mask_result = mask_fixed AND mask_moving AND mask_registered
```

### Interpolation

**During Registration**: Linear interpolation used by elastix

**For Displacement Fields**: No interpolation, direct pixel-level calculation

**For Resampling**: Bilinear interpolation for smooth results

## Algorithm Performance

### Computational Complexity

**Registration**:
- BSpline (NA): O(N * M * K) where N=pixels, M=iterations, K=control points
- Affine (AF): O(N * M)
- Rigid (RG): O(N * M)
- Translation (TS): O(N * M)

**Displacement Calculation**:
- Horizontal: O(N) for extraction from deformation field
- Vertical: O(N) for pixel-wise subtraction
- Magnitude: O(N) for element-wise operations

**Tiling Overhead**:
- Processing: ~10-20% overhead for tile management
- Memory: Reduces peak usage by ~N_tiles factor

### Typical Processing Times

**Small Dataset** (1000×1000 pixels):
- NA: 1-2 minutes
- AF: 30-60 seconds
- RG: 20-40 seconds
- TS: 10-20 seconds

**Medium Dataset** (5000×5000 pixels):
- NA: 10-15 minutes
- AF: 5-8 minutes
- RG: 3-5 minutes
- TS: 2-3 minutes

**Large Dataset** (10000×10000 pixels, tiled):
- NA: 30-60 minutes (4 tiles)
- AF: 15-25 minutes
- RG: 10-15 minutes
- TS: 5-10 minutes

**Note**: Times vary based on CPU, overlap amount, deformation complexity

### Optimization Strategies

1. **Multi-threading**: Parallelize tile processing
2. **Resolution reduction**: Use coarser resolution for initial tests
3. **Method selection**: Use faster methods (AF, RG) when appropriate
4. **ROI extraction**: Clip to region of interest before processing
5. **Disable visualization**: Skip plot generation for batch processing

## Accuracy and Limitations

### Theoretical Accuracy

**Horizontal Displacement**:
- Limited by pixel size and registration accuracy
- Typical: 0.1-0.5 pixels (0.1-0.5 m for 1-m DEMs)
- Best case: 0.05 pixels with high-quality data

**Vertical Displacement**:
- Limited by DEM vertical accuracy
- Typical: 2-5× vertical accuracy of input DEMs
- Affected by registration errors in steep terrain

### Error Sources

1. **DEM Quality**: Input data accuracy, artifacts, noise
2. **Co-registration**: Horizontal alignment errors
3. **Illumination**: Different lighting conditions in optical DEMs
4. **Seasonal Effects**: Vegetation changes, snow cover
5. **Processing Artifacts**: Interpolation, filtering, resampling

### Limitations

1. **Large Deformation**: Very large displacements (> 50% image size) may fail
2. **Low Texture**: Homogeneous regions lack features for registration
3. **Steep Terrain**: Vertical slopes can introduce errors
4. **Temporal Aliasing**: Rapid changes between acquisitions may be missed
5. **CRS Accuracy**: Incorrect CRS metadata leads to wrong displacement units

### Best Practices for Accuracy

1. Use high-quality, well-processed DEMs
2. Ensure good temporal spacing (not too close, not too far)
3. Minimize seasonal differences (same season preferred)
4. Use appropriate registration method for expected deformation
5. Validate with ground truth (GPS, field measurements)
6. Cross-check with independent data (InSAR, optical correlation)

## References

### GeoElastix Methodology

1. **GeoElastix Application**: Zhu, Y., Dortch, J. M., & Haneberg, W. C. (2022). Non-affine georectification to improve the topographic fidelity of legacy geologic maps. International Journal of Applied Earth Observation and Geoinformation, 115, 103127. https://doi.org/10.1016/j.jag.2022.103127

### Core Algorithms

2. **Elastix**: Klein, S., Staring, M., Murphy, K., Viergever, M. A., & Pluim, J. P. (2010). elastix: a toolbox for intensity-based medical image registration. IEEE transactions on medical imaging, 29(1), 196-205.

3. **ITK**: Yoo, T. S., et al. (2002). Engineering and algorithm design for an image processing API: a technical report on ITK-the insight toolkit. Studies in health technology and informatics, 586-592.

4. **B-Spline Registration**: Rueckert, D., et al. (1999). Nonrigid registration using free-form deformations: application to breast MR images. IEEE Transactions on Medical Imaging, 18(8), 712-721.

### Geospatial Applications

5. **DEM Co-registration**: Nuth, C., & Kääb, A. (2011). Co-registration and bias corrections of satellite elevation data sets for quantifying glacier thickness change. The Cryosphere, 5(1), 271-290.

6. **Landslide Monitoring**: Stumpf, A., et al. (2014). Image-based mapping of surface fissures for the investigation of landslide dynamics. Geomorphology, 186, 12-27.

### Quality Metrics

7. **Mutual Information**: Viola, P., & Wells III, W. M. (1997). Alignment by maximization of mutual information. International journal of computer vision, 24(2), 137-154.

8. **Dice Coefficient**: Dice, L. R. (1945). Measures of the amount of ecologic association between species. Ecology, 26(3), 297-302.

## Appendix: Parameter Files

### Parameter File Structure

Elastix parameter files use a simple text format:

```
(Transform "BSplineTransform")
(Metric "NormalizedCorrelation")
(Optimizer "AdaptiveStochasticGradientDescent")
(NumberOfResolutions 4)
(FinalGridSpacingInPhysicalUnits 16.0)
(MaximumNumberOfIterations 500 500 500 500)
...
```

### Key Parameters

**Transform Parameters**:
- `Transform`: Type of transformation
- `FinalGridSpacingInPhysicalUnits`: B-spline grid spacing (smaller = more flexible)

**Metric Parameters**:
- `Metric`: Similarity measure
- `NumberOfHistogramBins`: Bins for MI calculation (256 typical)

**Optimizer Parameters**:
- `Optimizer`: Optimization algorithm
- `MaximumNumberOfIterations`: Iterations per resolution
- `MaximumStepLength`: Initial step size

**Multi-Resolution**:
- `NumberOfResolutions`: Pyramid levels
- `ImagePyramidSchedule`: Downsampling at each level

### Custom Parameter Files

Users can create custom parameter files by:
1. Starting from default parameter file
2. Modifying specific parameters
3. Testing with small dataset
4. Specifying custom file in configuration:

```yaml
registration:
  parameter_file: "./my_custom_params.txt"
```

**Warning**: Incorrect parameters may cause registration failure. Always test on small datasets first.

## Glossary

**Affine**: Linear transformation with rotation, translation, scaling, and shearing

**BSpline**: Basis spline, a piecewise polynomial function used for free-form deformation

**CRS**: Coordinate Reference System, defines how coordinates map to Earth positions

**Deformation Field**: Vector field representing displacement at each pixel

**Elastix**: Medical image registration software used by GeoElastix

**Geotransform**: GDAL structure mapping image to map coordinates

**ITK**: Insight Toolkit, medical image processing library

**Mutual Information**: Statistical measure of dependency between variables

**No-Data**: Invalid or missing pixel values in raster

**Registration**: Process of aligning two or more images

**RMSE**: Root Mean Square Error, measure of pixel-wise difference

**Subsidence**: Downward ground movement (negative Z displacement)

**Transformation**: Mathematical function mapping points from one coordinate system to another

**Uplift**: Upward ground movement (positive Z displacement)
