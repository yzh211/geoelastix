"""Test raster I/O functionality with Wrigley dataset."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from geoelastix.io import RasterIO, NoDataHandler, CRSManager
from geoelastix.utils import setup_logging

def test_read_wrigley_data():
    """Test reading Wrigley dataset."""

    # Setup logging
    logger = setup_logging(log_level="INFO")

    # Define file paths
    base_dir = Path(__file__).parent.parent.parent
    fixed_file = base_dir / "examples/wrigley/data/wrigley_30ft_lidar.tif"
    moving_file = base_dir / "examples/wrigley/data/wrigley_30ft_legacy.tif"

    logger.info("="*60)
    logger.info("Testing GeoElastix I/O Module with Wrigley Dataset")
    logger.info("="*60)

    # Test reading fixed image
    logger.info("\n1. Reading fixed image (newer LiDAR):")
    logger.info("-"*60)

    try:
        fixed_data = RasterIO.read_raster(fixed_file)
        logger.info(f"✓ Successfully read fixed image")
        logger.info(f"  Array shape: {fixed_data['array'].shape}")
        logger.info(f"  Data type: {fixed_data['dtype']}")
        logger.info(f"  No-data value: {fixed_data['nodata']}")

        if fixed_data['crs']:
            crs_info = CRSManager.get_crs_info(fixed_data['crs'])
            logger.info(f"  CRS: {crs_info['name']} (EPSG:{crs_info['code']})")

        valid_pct = NoDataHandler.get_valid_data_percentage(fixed_data['mask'])
        logger.info(f"  Valid data: {valid_pct:.2f}%")

    except Exception as e:
        logger.error(f"✗ Failed to read fixed image: {e}")
        return False

    # Test reading moving image
    logger.info("\n2. Reading moving image (legacy DEM):")
    logger.info("-"*60)

    try:
        moving_data = RasterIO.read_raster(moving_file)
        logger.info(f"✓ Successfully read moving image")
        logger.info(f"  Array shape: {moving_data['array'].shape}")
        logger.info(f"  Data type: {moving_data['dtype']}")
        logger.info(f"  No-data value: {moving_data['nodata']}")

        if moving_data['crs']:
            crs_info = CRSManager.get_crs_info(moving_data['crs'])
            logger.info(f"  CRS: {crs_info['name']} (EPSG:{crs_info['code']})")

        valid_pct = NoDataHandler.get_valid_data_percentage(moving_data['mask'])
        logger.info(f"  Valid data: {valid_pct:.2f}%")

    except Exception as e:
        logger.error(f"✗ Failed to read moving image: {e}")
        return False

    # Test CRS comparison
    logger.info("\n3. Comparing CRS:")
    logger.info("-"*60)

    try:
        are_compatible = CRSManager.compare_crs(
            fixed_data['crs'],
            moving_data['crs']
        )

        if are_compatible:
            logger.info("✓ CRS are compatible")
        else:
            logger.warning("⚠ CRS mismatch detected")

    except Exception as e:
        logger.error(f"✗ CRS comparison failed: {e}")

    # Test shape compatibility
    logger.info("\n4. Checking image dimensions:")
    logger.info("-"*60)

    if fixed_data['shape'] == moving_data['shape']:
        logger.info(f"✓ Images have matching dimensions: {fixed_data['shape']}")
    else:
        logger.warning(
            f"⚠ Dimension mismatch:\n"
            f"  Fixed: {fixed_data['shape']}\n"
            f"  Moving: {moving_data['shape']}"
        )

    # Test pixel size
    logger.info("\n5. Checking pixel resolution:")
    logger.info("-"*60)

    from osgeo import gdal
    fixed_ds = gdal.Open(str(fixed_file))
    moving_ds = gdal.Open(str(moving_file))

    fixed_pixel = CRSManager.get_pixel_size(fixed_ds)
    moving_pixel = CRSManager.get_pixel_size(moving_ds)

    logger.info(f"  Fixed pixel size: {fixed_pixel[0]:.6f} x {fixed_pixel[1]:.6f}")
    logger.info(f"  Moving pixel size: {moving_pixel[0]:.6f} x {moving_pixel[1]:.6f}")

    fixed_ds = None
    moving_ds = None

    # Test ITK conversion
    logger.info("\n6. Testing ITK image conversion:")
    logger.info("-"*60)

    try:
        fixed_itk = RasterIO.array_to_itk_image(
            fixed_data['array'],
            spacing=fixed_pixel
        )
        logger.info(f"✓ Successfully converted to ITK image")
        logger.info(f"  ITK image size: {fixed_itk.GetLargestPossibleRegion().GetSize()}")

        # Convert back
        array_back = RasterIO.itk_image_to_array(fixed_itk)
        logger.info(f"✓ Successfully converted back to numpy array")
        logger.info(f"  Array shape: {array_back.shape}")

    except Exception as e:
        logger.error(f"✗ ITK conversion failed: {e}")
        return False

    logger.info("\n" + "="*60)
    logger.info("All I/O tests completed successfully!")
    logger.info("="*60)

    return True


if __name__ == "__main__":
    success = test_read_wrigley_data()
    sys.exit(0 if success else 1)
