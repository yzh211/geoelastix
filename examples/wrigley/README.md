# Wrigley Landslide Monitoring Example

This example demonstrates using GeoElastix to register multi-temporal DEMs for landslide monitoring at the Wrigley site.

## Dataset

The Wrigley dataset contains two Digital Elevation Models (DEMs) at 30-foot resolution:

- **wrigley_30ft_lidar.tif**: Newer LiDAR-derived DEM (used as fixed/reference image)
- **wrigley_30ft_legacy.tif**: Older legacy DEM (used as moving image to be registered)

## Objective

Register the legacy DEM to the LiDAR DEM and calculate:
- Horizontal displacement (X and Y directions)
- Vertical displacement (Z direction)
- Total horizontal displacement magnitude

## Running the Example

### Using the Configuration File

```bash
geoelastix register --config examples/wrigley/config_wrigley.yaml
```

### Using Command-Line Arguments

```bash
geoelastix register \
  --fixed examples/wrigley/data/wrigley_30ft_lidar.tif \
  --moving examples/wrigley/data/wrigley_30ft_legacy.tif \
  --job-id wrigley_landslide \
  --method NA \
  --output ./output
```

## Expected Output

The registration will create an output directory with the following structure:

```
output/wrigley_landslide_legacy_vs_lidar_YYYYMMDD_HHMMSS/
├── displacement/
│   ├── displacement_x.tif          # East-West displacement
│   ├── displacement_x.asc
│   ├── displacement_y.tif          # North-South displacement
│   ├── displacement_y.asc
│   ├── displacement_z.tif          # Vertical displacement
│   ├── displacement_z.asc
│   └── displacement_magnitude.tif  # Total horizontal displacement
│
├── registered/
│   ├── registered_moving.tif       # Registered legacy DEM
│   └── residual.tif                # Elevation difference
│
├── visualization/
│   ├── horizontal_quiver.png       # Vector field plot
│   ├── displacement_x_contour.png
│   ├── displacement_y_contour.png
│   ├── displacement_z_contour.png
│   └── displacement_magnitude_contour.png
│
├── logs/
│   ├── geoelastix.log
│   └── metrics.json
│
└── report.pdf                      # Comprehensive analysis report
```

## Registration Method

This example uses:
- **Transform**: Non-Affine (BSpline deformable registration)
- **Metric**: Normalized Cross-Correlation (NCC)
- **Optimizer**: Adaptive Stochastic Gradient Descent (ASGD)
- **Strategy**: Two-pass registration for improved accuracy

## Interpreting Results

### Displacement Fields

- **displacement_x.tif**: Positive values indicate eastward movement, negative values indicate westward movement
- **displacement_y.tif**: Positive values indicate northward movement, negative values indicate southward movement
- **displacement_z.tif**: Positive values indicate uplift, negative values indicate subsidence
- **displacement_magnitude.tif**: Total horizontal displacement (√(x² + y²))

### Quality Metrics

The analysis will report:
- **RMSE**: Root Mean Square Error of registration
- **Mutual Information**: Similarity measure between registered images
- **Coverage**: Percentage of valid overlapping area
- **Displacement Statistics**: Mean, standard deviation, and range of displacements

## Notes

- The two-pass registration strategy is applied automatically to improve accuracy
- No-data values are handled according to GDAL standards
- All outputs preserve the CRS from the input files
- Processing time depends on image size and available computational resources

## Troubleshooting

If you encounter issues:

1. **CRS mismatch warning**: Ensure both DEMs are in the same coordinate reference system
2. **High RMSE**: May indicate poor registration quality; try adjusting parameters
3. **Large no-data regions**: Check input data quality and mask validity

For more information, see the [main documentation](../../docs/user_guide.md).
