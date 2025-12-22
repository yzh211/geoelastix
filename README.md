# GeoElastix

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-stable-green.svg)]()

**Geospatial Image Registration for Landslide Monitoring**

GeoElastix is an open-source software for analyzing multi-temporal Digital Elevation Models (DEMs) to detect and quantify ground displacement in three dimensions. 

![Workflow](docs/workflow.jpg)

## Key Features

### Core Capabilities

- **3D Displacement Analysis**: Calculates horizontal (X, Y) and vertical (Z) displacement fields with millimeter-level accuracy
- **Multiple Registration Methods**: Four transformation models from rigid to free-form deformation
- **Large Dataset Support**: Automatic tiled processing for images exceeding 5000×5000 pixels
- **Professional Quality Assessment**: Comprehensive metrics including Mutual Information, Dice coefficient, among others
- **Rich Visualization**: Quiver plots, contour maps, rose diagrams, and multi-panel displays
- **Automated Reporting**: Text and JSON reports with quality metrics and displacement statistics

### Technical Highlights

- **ITK-Elastix Integration**: Proven medical image registration adapted for geospatial use
- **GDAL-Compliant**: Industry-standard geospatial data handling
- **Smart No-Data Management**: Automatic detection and proper propagation of invalid pixels
- **CRS-Aware**: Automatic coordinate reference system validation and pixel spacing detection
- **Multi-Resolution Optimization**: Pyramid-based coarse-to-fine registration strategy

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yzh211/geoelastix.git
cd geoelastix

# Create and activate conda environment
conda env create -f environment.yaml
conda activate geoelastix
```

For detailed installation instructions, see [Installation Guide](docs/INSTALLATION.md).

### Verify Installation

After installation, test your setup:

```bash
python quick_test.py
```

This validates all dependencies and optionally runs a complete test workflow. See [Testing & Validation](#testing--validation) below.

### Basic Usage

**Command-Line (Fastest)**:
```bash
geoelastix register \
  --fixed GIS/wrigley_30ft_lidar.tif \
  --moving GIS/wrigley_30ft_legacy.tif \
  --job-id landslide_analysis \
  --output ./results
```

**Configuration File (Recommended)**:
```bash
# Create configuration template
geoelastix create-config --output config.yaml

# Edit config.yaml with your settings

# Run analysis
geoelastix register --config config.yaml
```

**Python API**:
```python
from geoelastix.io import RasterIO
from geoelastix.registration import TwoPassRegistration, ParameterManager
from geoelastix.displacement import HorizontalDisplacement, VerticalDisplacement

# Load data
fixed_data = RasterIO.read_raster("GIS/wrigley_30ft_lidar.tif")
moving_data = RasterIO.read_raster("GIS/wrigley_30ft_legacy.tif")

# Register
param_obj = ParameterManager.create_parameter_object(method='NA')
two_pass = TwoPassRegistration(param_obj)
result = two_pass.register(fixed_itk, moving_itk)

# Calculate displacement
displacement = HorizontalDisplacement.compute_from_transform(
    result['registered_image'],
    result['transform_parameters']
)
```

## Registration Methods

GeoElastix provides four registration methods optimized for different scenarios:

| Method | Description | Use Case | Speed |
|--------|-------------|----------|-------|
| **NA** (Non-Affine) | Free-form BSpline deformation | Landslide monitoring (default) | Slower |
| **AF** (Affine) | Linear transformation | Moderate deformations | Medium |
| **RG** (Rigid) | Rotation + translation | Pre-aligned data | Fast |
| **TS** (Translation) | Translation only | Offset correction | Fastest |

**Recommendation**: Use **NA** method for landslide monitoring applications.

## Output Structure

GeoElastix creates organized output directories with descriptive naming:

```
output/
└── landslide_analysis_wrigley_20241120_143022/
    ├── displacement/
    │   ├── displacement_x.tif          # East-West movement (m)
    │   ├── displacement_y.tif          # North-South movement (m)
    │   ├── displacement_z.tif          # Vertical movement (m)
    │   ├── displacement_magnitude.tif  # Horizontal magnitude (m)
    │   └── *.asc                       # ASCII Grid format
    ├── registered/
    │   └── registered_moving.tif       # Aligned moving image
    ├── visualization/
    │   ├── horizontal_quiver.png       # Vector field plot
    │   ├── displacement_x_contour.png  # X displacement contours
    │   ├── displacement_y_contour.png  # Y displacement contours
    │   ├── displacement_z_contour.png  # Vertical displacement
    │   └── displacement_magnitude_contour.png
    ├── logs/
    │   └── geoelastix.log             # Detailed processing log
    ├── parameters/
    │   └── (elastix parameter files)
    ├── report.txt                      # Human-readable report
    └── metrics.json                    # Machine-readable metrics
```

## Documentation

Comprehensive documentation is available:

- **[Installation Guide](docs/INSTALLATION.md)**: Detailed setup instructions for all platforms
- **[Quick Start](docs/QUICKSTART.md)**: Get up and running in 5 minutes
- **[User Guide](docs/USER_GUIDE.md)**: Complete usage documentation with examples
- **[API Reference](docs/API.md)**: Python library documentation
- **[Methodology](docs/METHODOLOGY.md)**: Technical details of algorithms
- **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Solutions to common problems

## Examples


```bash
python quick_test.py
```

This demonstrates complete workflow from input DEMs to displacement analysis.

### Additional Examples

See `examples/` directory for:
- Basic registration workflow
- Custom parameter files
- Batch processing scripts
- Python API usage
- Visualization customization

## Configuration

GeoElastix uses YAML configuration files for flexible control (example):

```yaml
job:
  id: "wrigley_2021_vs_2022"
  description: "Landslide displacement analysis"
  output_dir: "./output"

input:
  fixed_image: "./GIS/wrigley_30ft_lidar.tif"    # Reference (newer)
  moving_image: "./GIS/wrigley_30ft_legacy.tif"   # Moving (older)

registration:
  method: "NA"                           # Non-Affine (BSpline)
  metric: "NCC"                          # Normalized Cross-Correlation

processing:
  tile_threshold: 5000                   # Auto-tile if > 5000 pixels
  tile_overlap: 100                      # Overlap for seamless blending
  num_threads: 4                         # Parallel processing

output:
  formats: ["geotiff", "asc"]
  generate_magnitude: true
  compression: "LZW"

visualization:
  generate_plots: true
  plot_types: ["quiver", "contour_x", "contour_y", "contour_z", "contour_magnitude"]
  dpi: 300
  colormap: "viridis"

quality:
  rmse_warning_threshold: 10.0
  min_overlap_percent: 70.0
  max_nodata_percent: 30.0
  min_dice: 0.7
  min_correlation: 0.5

logging:
  level: "INFO"
  save_to_file: true
```

Generate template: `geoelastix create-config --output myconfig.yaml`

## CLI Commands

GeoElastix provides five main commands:

```bash
# Register DEMs and calculate displacement
geoelastix register --config config.yaml

# List available registration methods
geoelastix list-methods

# Show parameter file details
geoelastix show-params NA

# Create configuration template
geoelastix create-config --output config.yaml

# Validate configuration file
geoelastix validate-config config.yaml
```

For detailed command usage: `geoelastix --help`

## Quality Metrics

GeoElastix computes comprehensive quality metrics:

- **Mutual Information**: Statistical dependency measure
- **Dice Coefficient**: Overlap between valid data regions
- **Coverage Statistics**: Valid pixel percentages and overlap

Automatic warnings alert you to potential quality issues.

## Technology Stack

- **[ITK-Elastix](https://github.com/InsightSoftwareConsortium/ITKElastix)**: Image registration engine
- **[GDAL](https://gdal.org/)**: Geospatial data I/O
- **[NumPy](https://numpy.org/)**: Numerical computing
- **[SciPy](https://scipy.org/)**: Scientific algorithms
- **[Matplotlib](https://matplotlib.org/)**: Visualization
- **[PyYAML](https://pyyaml.org/)**: Configuration parsing

## Performance

Typical processing times (4-core CPU):

| Image Size | Method | Processing Time |
|------------|--------|-----------------|
| 1000×1000 | NA | 1-2 minutes |

Actual times vary based on hardware, overlap amount, and deformation complexity.

## Supported Data Formats

### Input
- **GeoTIFF** (.tif, .tiff) - Recommended
- **ESRI ASCII Grid** (.asc)

### Output
- **GeoTIFF** (.tif) - Compressed (LZW/DEFLATE)
- **ESRI ASCII Grid** (.asc)
- **PNG** (visualizations)
- **JSON** (metrics)
- **TXT** (reports)

## Workflow

1. **Preparation**: Acquire multi-temporal DEMs (same CRS, similar resolution)
2. **Configuration**: Create YAML config or use CLI arguments
3. **Registration**: Align DEMs using appropriate method
4. **Displacement**: Extract X, Y, Z displacement fields
5. **Quality Check**: Review metrics and warnings
6. **Visualization**: Examine plots and contour maps
7. **Analysis**: Interpret displacement patterns
8. **Validation**: Compare with field observations or independent data

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ways to contribute:
- Report bugs or request features via [GitHub Issues](https://github.com/yzh211/geoelastix/issues)
- Submit pull requests for bug fixes or enhancements
- Improve documentation
- Share example workflows
- Add test cases


## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed release history.

**Version 0.1.0** (2024-11-20):
- Initial release
- Complete CLI and workflow orchestration
- Four registration methods (NA, AF, RG, TS)
- 3D displacement calculation
- Quality metrics and validation
- Comprehensive visualization
- Large dataset tiling support
- Professional documentation

## License

GeoElastix is licensed under the **Apache License 2.0**.

This means you can:
- Use commercially
- Modify and distribute
- Use patent claims
- Place warranty

See [LICENSE](LICENSE) file for full terms.

## Citation

If you use GeoElastix in your research, please cite the following paper:

**Primary Citation**:

```bibtex
@article{zhu2022geoelastix,
  title = {Non-affine georectification to improve the topographic fidelity of legacy geologic maps},
  author = {Zhu, Y. and Dortch, J. M. and Haneberg, W. C.},
  journal = {International Journal of Applied Earth Observation and Geoinformation},
  volume = {115},
  pages = {103127},
  year = {2022},
  doi = {https://doi.org/10.1016/j.jag.2022.103127},
  url = {https://www.sciencedirect.com/science/article/pii/S1569843222003089}
}
```

## Acknowledgments

GeoElastix builds upon excellent open-source projects:

- **[ITK-Elastix](https://github.com/InsightSoftwareConsortium/ITKElastix)**: Medical image registration framework
- **[GDAL](https://gdal.org/)**: Geospatial Data Abstraction Library
- **[ITK](https://itk.org/)**: Insight Segmentation and Registration Toolkit

Special thanks to the open-source geospatial and image processing communities.

## Support

### Getting Help

- **Documentation**: Start with [User Guide](docs/USER_GUIDE.md)
- **Quick Start**: See [Quick Start Guide](docs/QUICKSTART.md)
- **Troubleshooting**: Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- **Examples**: Review `examples/` directory
- **GitHub Issues**: Search or create issue for bugs/questions

## Roadmap

Future enhancements under consideration:

- **GUI**: Graphical user interface for easier interaction
- **Cloud Processing**: Integration with cloud platforms
- **Additional Metrics**: More quality and accuracy measures
- **Time Series**: Multi-temporal analysis tools
- **3D Visualization**: Interactive 3D displacement viewing

Vote on features or suggest new ones via GitHub Issues!

## FAQ

**Q: What input data formats are supported?**
A: GeoTIFF and ESRI ASCII Grid. DEMs should be single-band elevation rasters.

**Q: What is the maximum DEM size?**
A: Unlimited with automatic tiling. Successfully tested with 20000×20000 pixel DEMs.

**Q: Do DEMs need to have the same resolution?**
A: Similar resolution recommended (within 2× factor). 

**Q: Can I run batch processing?**
A: Yes, create multiple config files and process in sequence or use Python API.

**Q: Can I customize the registration parameters?**
A: Yes, create custom elastix parameter files and specify in configuration.

For more questions, see [User Guide](docs/USER_GUIDE.md) or open an issue.

## Links

- **Repository**: https://github.com/yzh211/geoelastix
- **Issues**: https://github.com/yzh211/geoelastix/issues
- **Documentation**: https://github.com/yzh211/geoelastix/tree/master/docs
- **Examples**: https://github.com/yzh211/geoelastix/tree/master/examples

## Contact

For questions, collaborations, or commercial inquiries, please open an issue on GitHub.

---

**GeoElastix** - Professional geospatial image registration for ground deformation analysis

Version 0.1.0 | Apache License 2.0 | © 2024 GeoElastix Development Team
