"""Example: Using GeoElastix Python API for custom workflows."""

from pathlib import Path
import numpy as np
import itk
from osgeo import gdal

from geoelastix.io import RasterIO, CRSManager
from geoelastix.registration import TwoPassRegistration, ParameterManager
from geoelastix.displacement import (
    HorizontalDisplacement,
    VerticalDisplacement,
    DisplacementMagnitude
)
from geoelastix.validation import QualityMetrics, QualityChecker
from geoelastix.visualization import QuiverPlot, ContourPlot
from geoelastix.utils import setup_logging, ensure_dir


def main():
    """Complete registration and displacement analysis workflow using API."""

    # Setup logging
    logger = setup_logging(log_level='INFO')

    logger.info("="*70)
    logger.info("GeoElastix Python API Example")
    logger.info("="*70)

    # =========================================================================
    # STEP 1: Load Input Data
    # =========================================================================
    logger.info("\nStep 1: Loading input data...")

    fixed_path = "GIS/wrigley_30ft_lidar.tif"
    moving_path = "GIS/wrigley_30ft_legacy.tif"

    # Read rasters
    fixed_data = RasterIO.read_raster(fixed_path)
    moving_data = RasterIO.read_raster(moving_path)

    logger.info(f"  Fixed image: {fixed_data['shape']}")
    logger.info(f"  Moving image: {moving_data['shape']}")
    logger.info(f"  CRS: {fixed_data['crs']}")

    # Get pixel spacing
    ds = gdal.Open(str(fixed_path))
    pixel_spacing = CRSManager.get_pixel_size(ds)
    logger.info(f"  Pixel spacing: {pixel_spacing}")

    # =========================================================================
    # STEP 2: Convert to ITK Images
    # =========================================================================
    logger.info("\nStep 2: Converting to ITK format...")

    fixed_itk = RasterIO.array_to_itk_image(
        fixed_data['array'],
        spacing=pixel_spacing
    )
    moving_itk = RasterIO.array_to_itk_image(
        moving_data['array'],
        spacing=pixel_spacing
    )

    # Create masks
    fixed_mask = itk.image_from_array(fixed_data['mask'].astype(np.uint8))
    moving_mask = itk.image_from_array(moving_data['mask'].astype(np.uint8))

    # =========================================================================
    # STEP 3: Perform Registration
    # =========================================================================
    logger.info("\nStep 3: Performing registration...")

    # Create parameter object (Non-Affine method)
    param_obj = ParameterManager.create_parameter_object(method='NA')

    # Initialize two-pass registration
    two_pass = TwoPassRegistration(param_obj)

    # Register
    reg_result = two_pass.register(
        fixed_itk,
        moving_itk,
        fixed_mask=fixed_mask,
        moving_mask=moving_mask,
        log_to_console=False
    )

    logger.info("  Registration complete")

    # Convert registered image back to array
    registered_array = RasterIO.itk_image_to_array(reg_result['registered_image'])

    # =========================================================================
    # STEP 4: Calculate Displacement
    # =========================================================================
    logger.info("\nStep 4: Calculating displacement...")

    # Horizontal displacement (X, Y)
    horiz_result = HorizontalDisplacement.compute_from_transform(
        reg_result['registered_image'],
        reg_result['transform_parameters'],
        spacing=pixel_spacing
    )

    displacement_x = horiz_result['displacement_x']
    displacement_y = horiz_result['displacement_y']

    # Get horizontal statistics
    horiz_stats = HorizontalDisplacement.get_statistics(
        displacement_x,
        displacement_y,
        mask=fixed_data['mask']
    )

    logger.info(f"  X displacement: mean={horiz_stats['x_mean']:.2f} m, "
                f"max={horiz_stats['x_max']:.2f} m")
    logger.info(f"  Y displacement: mean={horiz_stats['y_mean']:.2f} m, "
                f"max={horiz_stats['y_max']:.2f} m")

    # Vertical displacement (Z)
    vert_result = VerticalDisplacement.compute_from_arrays(
        fixed_data['array'],
        registered_array,
        mask=fixed_data['mask']
    )

    displacement_z = vert_result['displacement_z']
    vert_stats = vert_result['statistics']

    logger.info(f"  Z displacement: mean={vert_stats['mean']:.2f} m, "
                f"max={vert_stats['max']:.2f} m")

    # Displacement magnitude
    mag_result = DisplacementMagnitude.compute_horizontal_magnitude(
        displacement_x,
        displacement_y
    )

    displacement_magnitude = mag_result['magnitude']
    displacement_direction = mag_result['direction']
    mag_stats = mag_result['statistics']

    logger.info(f"  Horizontal magnitude: mean={mag_stats['mean']:.2f} m, "
                f"max={mag_stats['max']:.2f} m")

    # =========================================================================
    # STEP 5: Compute Quality Metrics
    # =========================================================================
    logger.info("\nStep 5: Computing quality metrics...")

    metrics = QualityMetrics.compute_all_metrics(
        fixed_data['array'],
        registered_array,
        fixed_mask=fixed_data['mask'],
        registered_mask=moving_data['mask'],
        image_shape=fixed_data['shape']
    )

    logger.info(f"  RMSE: {metrics['rmse']:.2f}")
    logger.info(f"  Correlation: {metrics['correlation']:.3f}")
    logger.info(f"  Dice coefficient: {metrics['dice_coefficient']:.3f}")
    logger.info(f"  Normalized MI: {metrics['normalized_mi']:.3f}")

    # Quality checks
    checker = QualityChecker()
    quality_checks = checker.check_metrics(metrics)

    # =========================================================================
    # STEP 6: Save Outputs
    # =========================================================================
    logger.info("\nStep 6: Saving outputs...")

    output_dir = Path("./api_example_output")
    ensure_dir(output_dir)
    ensure_dir(output_dir / "displacement")
    ensure_dir(output_dir / "registered")
    ensure_dir(output_dir / "visualization")

    # Save registered image
    RasterIO.write_geotiff(
        output_dir / "registered" / "registered_moving.tif",
        registered_array,
        fixed_data['geotransform'],
        fixed_data['crs'],
        nodata_value=fixed_data['nodata'],
        compression='LZW'
    )

    # Save displacement fields
    for name, data in [
        ('displacement_x', displacement_x),
        ('displacement_y', displacement_y),
        ('displacement_z', displacement_z),
        ('displacement_magnitude', displacement_magnitude)
    ]:
        # GeoTIFF
        RasterIO.write_geotiff(
            output_dir / "displacement" / f"{name}.tif",
            data,
            fixed_data['geotransform'],
            fixed_data['crs'],
            nodata_value=-9999,
            compression='LZW'
        )

        # ASC
        RasterIO.write_asc(
            output_dir / "displacement" / f"{name}.asc",
            data,
            fixed_data['geotransform'],
            nodata_value=-9999
        )

    logger.info(f"  Outputs saved to: {output_dir}")

    # =========================================================================
    # STEP 7: Create Visualizations
    # =========================================================================
    logger.info("\nStep 7: Creating visualizations...")

    # Quiver plot
    fig_quiver = QuiverPlot.create_quiver_plot(
        displacement_x,
        displacement_y,
        subsample=50,
        dpi=300,
        colormap='viridis',
        mask=fixed_data['mask']
    )
    QuiverPlot.save_plot(
        fig_quiver,
        output_dir / "visualization" / "horizontal_quiver.png"
    )

    # Contour plots
    for component, data, title, cmap in [
        ('x', displacement_x, 'X Displacement (East-West)', 'RdBu_r'),
        ('y', displacement_y, 'Y Displacement (North-South)', 'RdBu_r'),
        ('z', displacement_z, 'Z Displacement (Vertical)', 'RdBu_r'),
        ('magnitude', displacement_magnitude, 'Horizontal Magnitude', 'viridis')
    ]:
        fig_contour = ContourPlot.create_contour_plot(
            data,
            title=title,
            dpi=300,
            colormap=cmap,
            mask=fixed_data['mask'],
            center_zero=(component != 'magnitude')
        )
        ContourPlot.save_plot(
            fig_contour,
            output_dir / "visualization" / f"displacement_{component}_contour.png"
        )

    logger.info(f"  Visualizations saved")

    # =========================================================================
    # STEP 8: Generate Report
    # =========================================================================
    logger.info("\nStep 8: Generating report...")

    report_path = output_dir / "report.txt"

    with open(report_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write("GEOELASTIX REGISTRATION AND DISPLACEMENT ANALYSIS\n")
        f.write("="*70 + "\n\n")

        f.write("INPUT FILES\n")
        f.write("-"*70 + "\n")
        f.write(f"Fixed image:  {fixed_path}\n")
        f.write(f"Moving image: {moving_path}\n")
        f.write(f"Image shape:  {fixed_data['shape']}\n")
        f.write(f"CRS:          {fixed_data['crs']}\n")
        f.write(f"Pixel size:   {pixel_spacing[0]:.6f} x {pixel_spacing[1]:.6f}\n\n")

        f.write("QUALITY METRICS\n")
        f.write("-"*70 + "\n")
        f.write(f"RMSE:                 {metrics['rmse']:.2f} m\n")
        f.write(f"Correlation:          {metrics['correlation']:.3f}\n")
        f.write(f"Dice coefficient:     {metrics['dice_coefficient']:.3f}\n")
        f.write(f"Mutual Information:   {metrics['mutual_information']:.3f}\n")
        f.write(f"Normalized MI:        {metrics['normalized_mi']:.3f}\n\n")

        f.write("DISPLACEMENT STATISTICS\n")
        f.write("-"*70 + "\n")
        f.write(f"X Displacement (East-West):\n")
        f.write(f"  Mean:   {horiz_stats['x_mean']:.2f} m\n")
        f.write(f"  Std:    {horiz_stats['x_std']:.2f} m\n")
        f.write(f"  Min:    {horiz_stats['x_min']:.2f} m\n")
        f.write(f"  Max:    {horiz_stats['x_max']:.2f} m\n\n")

        f.write(f"Y Displacement (North-South):\n")
        f.write(f"  Mean:   {horiz_stats['y_mean']:.2f} m\n")
        f.write(f"  Std:    {horiz_stats['y_std']:.2f} m\n")
        f.write(f"  Min:    {horiz_stats['y_min']:.2f} m\n")
        f.write(f"  Max:    {horiz_stats['y_max']:.2f} m\n\n")

        f.write(f"Z Displacement (Vertical):\n")
        f.write(f"  Mean:   {vert_stats['mean']:.2f} m\n")
        f.write(f"  Std:    {vert_stats['std']:.2f} m\n")
        f.write(f"  Min:    {vert_stats['min']:.2f} m\n")
        f.write(f"  Max:    {vert_stats['max']:.2f} m\n\n")

        f.write(f"Horizontal Magnitude:\n")
        f.write(f"  Mean:   {mag_stats['mean']:.2f} m\n")
        f.write(f"  Std:    {mag_stats['std']:.2f} m\n")
        f.write(f"  Max:    {mag_stats['max']:.2f} m\n\n")

        f.write("="*70 + "\n")
        f.write("Analysis complete\n")

    logger.info(f"  Report saved to: {report_path}")

    # =========================================================================
    # Done
    # =========================================================================
    logger.info("\n" + "="*70)
    logger.info("✓ Analysis complete!")
    logger.info(f"  Output directory: {output_dir}")
    logger.info("="*70)


if __name__ == '__main__':
    main()
