# GeoElastix

**Geospatial Image Registration for Landslide Monitoring**

GeoElastix is a professional, open-source geospatial image registration software that analyzes multi-temporal Digital Elevation Models (DEMs) to detect and quantify both horizontal and vertical ground movements for landslide monitoring applications.

## Features

- **Multi-temporal DEM Analysis**: Register and compare DEMs captured at different times
- **Displacement Detection**: Calculate horizontal (X, Y) and vertical (Z) displacement fields
- **Multiple Registration Methods**:
  - Non-Affine (NA) - Deformable registration (default for landslide monitoring)
  - Affine (AF) - Affine transformation
  - Rigid (RG) - Rotation and translation
  - Translation (TS) - Translation only
- **Quality Metrics**: RMSE, Mutual Information, Dice coefficient, and coverage analysis
- **Automatic Warnings**: Quality checks for poor registration or data issues
- **Large Dataset Support**: Automatic tiled processing for images > 5000×5000 pixels
- **Industry-Standard Data Handling**: GDAL-compliant no-data value handling
- **Visualization**: Quiver plots and contour maps for displacement fields
- **Comprehensive Reports**: Automatic PDF report generation with metrics and visualizations
- **Multiple Output Formats**: GeoTIFF and ASCII Grid (ASC) formats

## Technology Stack

- **Registration Engine**: ITK-Elastix
- **Geospatial I/O**: GDAL, Rasterio
- **Scientific Computing**: NumPy, SciPy
- **Visualization**: Matplotlib
- **Configuration**: YAML

## Installation

### Requirements

- Python 3.8 or higher
- Conda (recommended for managing dependencies)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GeoElastix.git
cd GeoElastix
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yaml
conda activate geoelastix
```

3. Install GeoElastix:
```bash
pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Using a configuration file
geoelastix register --config config_wrigley.yaml

# Quick registration with minimal options
geoelastix register --fixed dem_2022.tif --moving dem_2021.tif --job-id my_analysis
```

### Configuration File Example

Create a `config.yaml` file:

```yaml
job:
  id: "landslide_analysis"
  output_dir: "./output"

input:
  fixed_image: "./data/dem_new.tif"
  moving_image: "./data/dem_old.tif"

registration:
  method: "NA"              # Non-Affine (default for landslide)
  metric: "NCC"             # Normalized Cross-Correlation

output:
  formats: ["geotiff", "asc"]
  generate_magnitude: true

visualization:
  generate_plots: true

reporting:
  generate_pdf: true
```

Then run:
```bash
geoelastix register --config config.yaml
```

## Output Structure

GeoElastix generates organized output directories:

```
output/
└── landslide_analysis_20241120_143022/
    ├── displacement/              # Displacement fields (X, Y, Z)
    ├── registered/                # Registered images
    ├── visualization/             # Plots (quiver, contours)
    ├── logs/                      # Processing logs and metrics
    └── report.pdf                 # Comprehensive PDF report
```

## Documentation

- [Installation Guide](docs/installation.md)
- [User Guide](docs/user_guide.md)
- [API Reference](docs/api_reference.md)
- [Methodology](docs/methodology.md)
- [Troubleshooting](docs/troubleshooting.md)

## Examples

See the [examples/wrigley](examples/wrigley) directory for a complete example using the Wrigley dataset.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Citation

If you use GeoElastix in your research, please cite:

```
[Citation information to be added]
```

## Acknowledgments

- Built on [ITK-Elastix](https://github.com/InsightSoftwareConsortium/ITKElastix)
- Uses [GDAL](https://gdal.org/) for geospatial data handling

## Contact

For questions, issues, or contributions, please open an issue on GitHub.

---

**Version**: 0.1.0
**Status**: Development
