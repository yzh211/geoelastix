"""Test displacement calculation modules."""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from geoelastix.displacement import HorizontalDisplacement, VerticalDisplacement, DisplacementMagnitude
from geoelastix.utils import setup_logging

def test_vertical_displacement():
    """Test vertical displacement calculation."""

    logger = setup_logging(log_level="INFO")

    logger.info("="*60)
    logger.info("Testing Vertical Displacement Module")
    logger.info("="*60)

    # Create synthetic elevation data
    height, width = 100, 100

    # Fixed image: flat surface at 1000m elevation
    fixed_array = np.full((height, width), 1000.0, dtype=np.float32)

    # Moving image: surface with subsidence in center
    moving_array = np.full((height, width), 1000.0, dtype=np.float32)

    # Add circular subsidence in center
    y_center, x_center = height // 2, width // 2
    radius = 30

    for i in range(height):
        for j in range(width):
            dist = np.sqrt((i - y_center)**2 + (j - x_center)**2)
            if dist < radius:
                # Subsidence decreases with distance from center
                subsidence = 5.0 * (1 - dist / radius)
                moving_array[i, j] -= subsidence

    logger.info("\n1. Computing vertical displacement from synthetic data:")
    logger.info("-"*60)

    result = VerticalDisplacement.compute_from_arrays(fixed_array, moving_array)

    displacement_z = result['displacement_z']
    stats = result['statistics']

    logger.info(f"✓ Vertical displacement computed")
    logger.info(f"  Shape: {displacement_z.shape}")
    logger.info(f"  Range: [{stats['z_min']:.3f}, {stats['z_max']:.3f}]")
    logger.info(f"  Mean: {stats['z_mean']:.3f} ± {stats['z_std']:.3f}")
    logger.info(f"  Median: {stats['z_median']:.3f}")
    logger.info(f"  Uplift area: {stats['uplift_area_percent']:.1f}%")
    logger.info(f"  Subsidence area: {stats['subsidence_area_percent']:.1f}%")

    # Verify expected results
    assert displacement_z.shape == (height, width), "Shape mismatch"
    assert stats['z_max'] > 0, "Expected positive displacement (uplift)"
    assert stats['z_min'] < 0.1, "Expected near-zero minimum"

    logger.info("\n2. Testing displacement classification:")
    logger.info("-"*60)

    classification = VerticalDisplacement.classify_displacement(displacement_z)
    logger.info(f"✓ Classification computed")
    logger.info(f"  Classification range: [{np.min(classification)}, {np.max(classification)}]")

    # Test gradient computation
    logger.info("\n3. Computing displacement gradient:")
    logger.info("-"*60)

    gradient = VerticalDisplacement.compute_gradient(displacement_z, spacing=30.0)
    logger.info(f"✓ Gradient computed")
    logger.info(f"  Gradient magnitude range: [{np.nanmin(gradient['gradient_magnitude']):.6f}, "
               f"{np.nanmax(gradient['gradient_magnitude']):.6f}]")

    logger.info("\n" + "="*60)
    logger.info("Vertical Displacement Tests PASSED")
    logger.info("="*60)

    return True


def test_displacement_magnitude():
    """Test displacement magnitude calculation."""

    logger = setup_logging(log_level="INFO")

    logger.info("\n" + "="*60)
    logger.info("Testing Displacement Magnitude Module")
    logger.info("="*60)

    # Create synthetic displacement fields
    height, width = 100, 100

    # Create X displacement (eastward movement in right half)
    displacement_x = np.zeros((height, width), dtype=np.float32)
    displacement_x[:, width//2:] = 2.0  # 2 meters east

    # Create Y displacement (northward movement in top half)
    displacement_y = np.zeros((height, width), dtype=np.float32)
    displacement_y[:height//2, :] = 1.5  # 1.5 meters north

    logger.info("\n1. Computing horizontal magnitude:")
    logger.info("-"*60)

    result = DisplacementMagnitude.compute_horizontal_magnitude(displacement_x, displacement_y)

    magnitude = result['magnitude']
    direction = result['direction']
    stats = result['statistics']

    logger.info(f"✓ Horizontal magnitude computed")
    logger.info(f"  Shape: {magnitude.shape}")
    logger.info(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}]")
    logger.info(f"  Mean: {stats['mean']:.3f} ± {stats['std']:.3f}")
    logger.info(f"  Median: {stats['median']:.3f}")
    logger.info(f"  95th percentile: {stats['percentile_95']:.3f}")

    # Verify expected results
    assert magnitude.shape == (height, width), "Shape mismatch"
    assert np.max(magnitude) > 0, "Expected non-zero magnitude"

    logger.info("\n2. Testing direction calculation:")
    logger.info("-"*60)

    # Test direction name conversion
    test_angles = [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi]
    test_names = ['E', 'NE', 'N', 'NW', 'W']

    logger.info("  Direction conversions:")
    for angle, expected_name in zip(test_angles, test_names):
        name = DisplacementMagnitude.get_displacement_direction_name(angle)
        logger.info(f"    {np.degrees(angle):6.1f}° → {name} (expected: {expected_name})")
        assert name == expected_name, f"Direction mismatch for {angle}"

    logger.info("✓ Direction calculation correct")

    # Test 3D magnitude
    logger.info("\n3. Computing 3D magnitude:")
    logger.info("-"*60)

    displacement_z = np.ones((height, width), dtype=np.float32) * 0.5  # 0.5m vertical

    result_3d = DisplacementMagnitude.compute_3d_magnitude(
        displacement_x, displacement_y, displacement_z
    )

    magnitude_3d = result_3d['magnitude_3d']
    stats_3d = result_3d['statistics']

    logger.info(f"✓ 3D magnitude computed")
    logger.info(f"  Range: [{stats_3d['min']:.3f}, {stats_3d['max']:.3f}]")
    logger.info(f"  Mean: {stats_3d['mean']:.3f}")

    # Verify 3D magnitude is larger than 2D
    assert np.all(magnitude_3d >= magnitude - 0.001), "3D magnitude should be >= 2D magnitude"

    # Test vector field preparation
    logger.info("\n4. Preparing vector field for visualization:")
    logger.info("-"*60)

    vector_field = DisplacementMagnitude.compute_displacement_vector_field(
        displacement_x, displacement_y, subsample=10
    )

    logger.info(f"✓ Vector field prepared")
    logger.info(f"  Original points: {height * width}")
    logger.info(f"  Subsampled points: {vector_field['n_vectors']}")
    logger.info(f"  Subsample factor: 10")

    # Test strain rate computation
    logger.info("\n5. Computing strain rate:")
    logger.info("-"*60)

    strain = DisplacementMagnitude.compute_strain_rate(
        displacement_x, displacement_y, spacing=30.0
    )

    logger.info(f"✓ Strain rate computed")
    logger.info(f"  Strain components: exx, eyy, exy")
    logger.info(f"  Principal strains: e1 (max), e2 (min)")
    logger.info(f"  Max shear strain range: [{np.nanmin(strain['max_shear']):.6f}, "
               f"{np.nanmax(strain['max_shear']):.6f}]")

    logger.info("\n" + "="*60)
    logger.info("Displacement Magnitude Tests PASSED")
    logger.info("="*60)

    return True


def test_tiling():
    """Test tiling functionality."""

    from geoelastix.tiling import TileManager, EdgeHandler

    logger = setup_logging(log_level="INFO")

    logger.info("\n" + "="*60)
    logger.info("Testing Tiling Module")
    logger.info("="*60)

    # Test with an image that needs tiling
    large_shape = (6000, 7000)

    logger.info("\n1. Creating tile layout:")
    logger.info("-"*60)

    tile_manager = TileManager(
        image_shape=large_shape,
        tile_size=5000,
        overlap=100
    )

    assert tile_manager.needs_tiling == True, "Should need tiling"
    logger.info(f"✓ Tile manager created")
    logger.info(f"  Number of tiles: {len(tile_manager.tiles)}")

    # Test edge handler
    logger.info("\n2. Testing edge blending:")
    logger.info("-"*60)

    edge_handler = EdgeHandler(overlap=100)

    # Create feather mask
    mask = edge_handler.create_feather_mask(1000, 1000)
    logger.info(f"✓ Feather mask created")
    logger.info(f"  Shape: {mask.shape}")
    logger.info(f"  Range: [{np.min(mask):.3f}, {np.max(mask):.3f}]")

    assert mask.shape == (1000, 1000), "Mask shape mismatch"
    assert np.min(mask) >= 0 and np.max(mask) <= 1, "Mask values should be in [0, 1]"

    # Test small image (no tiling needed)
    logger.info("\n3. Testing small image (no tiling):")
    logger.info("-"*60)

    small_shape = (1000, 1000)
    small_tile_manager = TileManager(small_shape, tile_size=5000)

    assert small_tile_manager.needs_tiling == False, "Should not need tiling"
    logger.info(f"✓ Small image correctly identified as not needing tiling")

    logger.info("\n" + "="*60)
    logger.info("Tiling Tests PASSED")
    logger.info("="*60)

    return True


if __name__ == "__main__":
    try:
        # Run tests
        success = True

        success &= test_vertical_displacement()
        success &= test_displacement_magnitude()
        success &= test_tiling()

        if success:
            print("\n" + "="*60)
            print("ALL DISPLACEMENT TESTS PASSED")
            print("="*60)
            sys.exit(0)
        else:
            print("\nSome tests failed")
            sys.exit(1)

    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
