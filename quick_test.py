"""Quick test script for GeoElastix with Wrigley dataset."""

import sys
from pathlib import Path
import io

# Add geoelastix to path
sys.path.insert(0, str(Path(__file__).parent))

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        import numpy as np
        print("  ✓ NumPy:", np.__version__)
    except ImportError as e:
        print("  ✗ NumPy not found:", e)
        return False

    try:
        from osgeo import gdal
        print("  ✓ GDAL:", gdal.__version__)
    except ImportError as e:
        print("  ✗ GDAL not found:", e)
        return False

    try:
        import itk
        print("  ✓ ITK:", itk.Version.GetITKVersion())
    except ImportError as e:
        print("  ✗ ITK not found:", e)
        return False

    try:
        import matplotlib
        print("  ✓ Matplotlib:", matplotlib.__version__)
    except ImportError as e:
        print("  ✗ Matplotlib not found:", e)
        return False

    print("\n✓ All required modules found!\n")
    return True

def test_geoelastix_modules():
    """Test that GeoElastix modules can be imported."""
    print("Testing GeoElastix modules...")

    try:
        from geoelastix.io import RasterIO
        print("  ✓ geoelastix.io")
    except ImportError as e:
        print("  ✗ geoelastix.io:", e)
        return False

    try:
        from geoelastix.registration import TwoPassRegistration
        print("  ✓ geoelastix.registration")
    except ImportError as e:
        print("  ✗ geoelastix.registration:", e)
        return False

    try:
        from geoelastix.displacement import HorizontalDisplacement
        print("  ✓ geoelastix.displacement")
    except ImportError as e:
        print("  ✗ geoelastix.displacement:", e)
        return False

    try:
        from geoelastix.cli import ConfigParser, WorkflowOrchestrator
        print("  ✓ geoelastix.cli")
    except ImportError as e:
        print("  ✗ geoelastix.cli:", e)
        return False

    print("\n✓ All GeoElastix modules loaded successfully!\n")
    return True

def check_data_files():
    """Check that Wrigley data files exist."""
    print("Checking Wrigley data files...")

    files_to_check = [
        "GIS/wrigley_30ft_lidar.tif",
        "GIS/wrigley_30ft_legacy.tif",
        "examples/wrigley/config_wrigley.yaml"
    ]

    all_exist = True
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"  ✓ {file_path} ({size_mb:.2f} MB)")
        else:
            print(f"  ✗ {file_path} NOT FOUND")
            all_exist = False

    if all_exist:
        print("\n✓ All data files found!\n")
    else:
        print("\n✗ Some data files missing!\n")

    return all_exist

def visualize_results(output_dir, spacing=30.0):
    """
    Visualize registration results with proper geo raster conventions.

    Parameters
    ----------
    output_dir : Path
        Output directory containing displacement files
    spacing : float
        Pixel spacing in feet (default: 30.0 ft)
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from osgeo import gdal

    print("\n" + "="*70)
    print("Visualizing Results")
    print("="*70)

    # Find displacement files
    disp_x_file = None
    disp_y_file = None
    disp_z_file = None

    for file in output_dir.glob("*.tif"):
        if "displacement_x" in file.name.lower():
            disp_x_file = file
        elif "displacement_y" in file.name.lower():
            disp_y_file = file
        elif "displacement_z" in file.name.lower():
            disp_z_file = file

    if not all([disp_x_file, disp_y_file, disp_z_file]):
        print("  ⚠ Displacement files not found, skipping visualization")
        return

    print(f"  Loading displacement fields...")
    print(f"    Resolution: {spacing} ft/pixel")

    # Load displacement data
    ds_x = gdal.Open(str(disp_x_file))
    ds_y = gdal.Open(str(disp_y_file))
    ds_z = gdal.Open(str(disp_z_file))

    disp_x = ds_x.ReadAsArray()
    disp_y = ds_y.ReadAsArray()
    disp_z = ds_z.ReadAsArray()

    # Get geotransform for spatial coordinates
    gt = ds_x.GetGeoTransform()

    # Close datasets
    ds_x = None
    ds_y = None
    ds_z = None

    # Create coordinate arrays in feet
    height, width = disp_x.shape
    x_coords = np.arange(width) * spacing
    y_coords = np.arange(height) * spacing

    # Compute magnitude
    magnitude = np.sqrt(disp_x**2 + disp_y**2)

    # Create visualization with 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # X Displacement (East-West)
    im1 = axes[0, 0].imshow(disp_x, cmap='RdBu_r', extent=[x_coords[0], x_coords[-1],
                                                             y_coords[-1], y_coords[0]],
                            aspect='equal', origin='upper')
    axes[0, 0].set_title('X Displacement (East-West)', fontweight='bold', fontsize=12)
    axes[0, 0].set_xlabel('X (ft)')
    axes[0, 0].set_ylabel('Y (ft)')
    cbar1 = plt.colorbar(im1, ax=axes[0, 0], label='Displacement (ft)')

    # Y Displacement (North-South) - flip Y axis for geo convention
    im2 = axes[0, 1].imshow(disp_y, cmap='RdBu_r', extent=[x_coords[0], x_coords[-1],
                                                             y_coords[-1], y_coords[0]],
                            aspect='equal', origin='upper')
    axes[0, 1].set_title('Y Displacement (North-South)', fontweight='bold', fontsize=12)
    axes[0, 1].set_xlabel('X (ft)')
    axes[0, 1].set_ylabel('Y (ft)')
    cbar2 = plt.colorbar(im2, ax=axes[0, 1], label='Displacement (ft)')

    # Z Displacement (Vertical)
    im3 = axes[1, 0].imshow(disp_z, cmap='RdBu_r', extent=[x_coords[0], x_coords[-1],
                                                             y_coords[-1], y_coords[0]],
                            aspect='equal', origin='upper')
    axes[1, 0].set_title('Z Displacement (Vertical)', fontweight='bold', fontsize=12)
    axes[1, 0].set_xlabel('X (ft)')
    axes[1, 0].set_ylabel('Y (ft)')
    cbar3 = plt.colorbar(im3, ax=axes[1, 0], label='Displacement (ft)')

    # Horizontal Magnitude
    im4 = axes[1, 1].imshow(magnitude, cmap='viridis', extent=[x_coords[0], x_coords[-1],
                                                                y_coords[-1], y_coords[0]],
                            aspect='equal', origin='upper')
    axes[1, 1].set_title('Horizontal Displacement Magnitude', fontweight='bold', fontsize=12)
    axes[1, 1].set_xlabel('X (ft)')
    axes[1, 1].set_ylabel('Y (ft)')
    cbar4 = plt.colorbar(im4, ax=axes[1, 1], label='Magnitude (ft)')

    # Add statistics
    stats_text = (
        f"Statistics:\n"
        f"X: {np.nanmean(disp_x):.2f} ± {np.nanstd(disp_x):.2f} ft\n"
        f"Y: {np.nanmean(disp_y):.2f} ± {np.nanstd(disp_y):.2f} ft\n"
        f"Z: {np.nanmean(disp_z):.2f} ± {np.nanstd(disp_z):.2f} ft\n"
        f"Mag: {np.nanmean(magnitude):.2f} ± {np.nanstd(magnitude):.2f} ft"
    )
    fig.text(0.5, 0.02, stats_text, ha='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.suptitle('Displacement Field Analysis (Geo Raster Convention)',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.05, 1, 0.97])

    # Save figure
    output_file = output_dir / "displacement_visualization.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Visualization saved to: {output_file}")

    # Show plot
    plt.show()

    print("\n" + "="*70)


def run_wrigley_test():
    """Run the Wrigley registration workflow."""
    print("="*70)
    print("Running Wrigley LiDAR vs Legacy Registration Test")
    print("="*70)
    print()

    from geoelastix.cli import ConfigParser, WorkflowOrchestrator
    from geoelastix.utils import setup_logging

    # Setup logging
    logger = setup_logging(log_level='INFO')

    # Load configuration
    config_path = Path("examples/wrigley/config_wrigley.yaml")
    logger.info(f"Loading configuration from: {config_path}")

    try:
        config = ConfigParser.load_and_validate(config_path)
        logger.info("✓ Configuration validated successfully")

        # Print configuration summary
        print("\nConfiguration Summary:")
        print(f"  Job ID: {config['job']['id']}")
        print(f"  Fixed Image: {config['input']['fixed_image']}")
        print(f"  Moving Image: {config['input']['moving_image']}")
        print(f"  Method: {config['registration']['method']}")
        print(f"  Output Dir: {config['job']['output_dir']}")
        print()

        # Ask user to confirm (skip if not interactive)
        try:
            response = input("Proceed with registration? This may take 2-5 minutes. (y/n): ")
            if response.lower() != 'y':
                print("Registration cancelled.")
                return False
        except EOFError:
            # Non-interactive mode, proceed automatically
            print("y (auto-confirmed in non-interactive mode)")
            pass

        # Run workflow
        print("\n" + "="*70)
        print("Starting Registration Workflow")
        print("="*70)
        print()

        orchestrator = WorkflowOrchestrator(config)
        results = orchestrator.run()

        print("\n" + "="*70)
        print("✓ Registration completed successfully!")
        print("="*70)
        print(f"\nOutput directory: {orchestrator.output_dir}")
        print("\nGenerated files:")
        print("  - Registered DEM")
        print("  - X, Y, Z displacement fields")
        print("  - Displacement magnitude")
        print("  - Quiver plots")
        print("  - Contour maps")
        print("  - Quality metrics report")
        print()

        # Visualize results with spacing information
        visualize_results(orchestrator.output_dir, spacing=30.0)

        return True

    except Exception as e:
        logger.error(f"\n✗ Registration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main test routine."""
    print("="*70)
    print("GeoElastix Quick Test Script")
    print("="*70)
    print()

    # Test 1: Check imports
    if not test_imports():
        print("\n✗ Import test failed. Please install dependencies:")
        print("  conda activate geoelastix")
        print("  conda install -c conda-forge gdal numpy scipy matplotlib itk itk-elastix")
        return 1

    # Test 2: Check GeoElastix modules
    if not test_geoelastix_modules():
        print("\n✗ GeoElastix module test failed. Please install the package:")
        print("  conda activate geoelastix")
        print("  pip install -e .")
        return 1

    # Test 3: Check data files
    if not check_data_files():
        print("\n✗ Data files not found. Please check the GIS/ directory.")
        return 1

    # Test 4: Run registration
    print("="*70)
    print("All preliminary checks passed!")
    print("="*70)
    print()

    response = input("Run full Wrigley registration test? (y/n): ")
    if response.lower() == 'y':
        if run_wrigley_test():
            return 0
        else:
            return 1
    else:
        print("\nSkipping registration test.")
        print("\nTo run registration manually:")
        print("  python -m geoelastix register --config examples/wrigley/config_wrigley.yaml")
        return 0

if __name__ == "__main__":
    sys.exit(main())