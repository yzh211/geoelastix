"""Quality checks and warnings for registration results."""

import logging
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger("geoelastix.validation")


class QualityChecker:
    """
    Perform quality checks on registration results and issue warnings.

    Evaluates metrics against thresholds and provides actionable feedback.
    """

    # Default thresholds
    DEFAULT_THRESHOLDS = {
        'rmse_warning': 10.0,           # Warning if RMSE > 10 map units
        'rmse_error': 50.0,             # Error if RMSE > 50 map units
        'min_overlap_percent': 70.0,    # Warning if overlap < 70%
        'max_nodata_percent': 30.0,     # Warning if no-data > 30%
        'min_dice': 0.7,                # Warning if Dice < 0.7
        'min_correlation': 0.5,         # Warning if correlation < 0.5
        'min_mi': 0.1,                  # Warning if MI < 0.1
    }

    def __init__(self, thresholds=None):
        """
        Initialize quality checker.

        Parameters
        ----------
        thresholds : dict, optional
            Custom threshold values. If None, uses defaults.
        """
        self.thresholds = self.DEFAULT_THRESHOLDS.copy()
        if thresholds is not None:
            self.thresholds.update(thresholds)

        logger.info("Initialized QualityChecker with thresholds:")
        for key, value in self.thresholds.items():
            logger.info(f"  {key}: {value}")

    def check_metrics(self, metrics: Dict) -> Dict:
        """
        Check all metrics and generate warnings/errors.

        Parameters
        ----------
        metrics : dict
            Dictionary of computed metrics

        Returns
        -------
        dict
            Dictionary with check results:
            - 'passed': bool, overall pass/fail
            - 'warnings': list of warning messages
            - 'errors': list of error messages
            - 'info': list of informational messages
            - 'checks': dict of individual check results
        """
        logger.info("="*60)
        logger.info("Performing quality checks")
        logger.info("="*60)

        warnings = []
        errors = []
        info = []
        checks = {}

        # Check RMSE
        if 'rmse' in metrics and not np.isnan(metrics['rmse']):
            rmse = metrics['rmse']
            if rmse > self.thresholds['rmse_error']:
                errors.append(
                    f"RMSE ({rmse:.2f}) exceeds error threshold "
                    f"({self.thresholds['rmse_error']:.2f}). "
                    "Registration quality is very poor."
                )
                checks['rmse'] = 'ERROR'
            elif rmse > self.thresholds['rmse_warning']:
                warnings.append(
                    f"RMSE ({rmse:.2f}) exceeds warning threshold "
                    f"({self.thresholds['rmse_warning']:.2f}). "
                    "Registration quality may be suboptimal."
                )
                checks['rmse'] = 'WARNING'
            else:
                info.append(f"RMSE ({rmse:.2f}) is within acceptable range.")
                checks['rmse'] = 'PASS'
        else:
            warnings.append("RMSE could not be computed.")
            checks['rmse'] = 'UNKNOWN'

        # Check overlap/coverage
        if 'overlap_coverage_percent' in metrics:
            overlap = metrics['overlap_coverage_percent']
            if overlap < self.thresholds['min_overlap_percent']:
                warnings.append(
                    f"Valid data overlap ({overlap:.1f}%) is below threshold "
                    f"({self.thresholds['min_overlap_percent']:.1f}%). "
                    "Limited overlapping area may affect results."
                )
                checks['overlap'] = 'WARNING'
            else:
                info.append(f"Valid data overlap ({overlap:.1f}%) is sufficient.")
                checks['overlap'] = 'PASS'
        else:
            checks['overlap'] = 'UNKNOWN'

        # Check no-data percentage
        if 'overlap_coverage_percent' in metrics:
            nodata_percent = 100.0 - metrics['overlap_coverage_percent']
            if nodata_percent > self.thresholds['max_nodata_percent']:
                warnings.append(
                    f"No-data percentage ({nodata_percent:.1f}%) exceeds threshold "
                    f"({self.thresholds['max_nodata_percent']:.1f}%). "
                    "Large no-data regions may affect displacement calculations."
                )
                checks['nodata'] = 'WARNING'
            else:
                info.append(f"No-data percentage ({nodata_percent:.1f}%) is acceptable.")
                checks['nodata'] = 'PASS'
        else:
            checks['nodata'] = 'UNKNOWN'

        # Check Dice coefficient
        if 'dice' in metrics and not np.isnan(metrics['dice']):
            dice = metrics['dice']
            if dice < self.thresholds['min_dice']:
                warnings.append(
                    f"Dice coefficient ({dice:.3f}) is below threshold "
                    f"({self.thresholds['min_dice']:.3f}). "
                    "Poor overlap between valid regions."
                )
                checks['dice'] = 'WARNING'
            else:
                info.append(f"Dice coefficient ({dice:.3f}) indicates good overlap.")
                checks['dice'] = 'PASS'
        else:
            checks['dice'] = 'UNKNOWN'

        # Check correlation
        if 'pearson_r' in metrics and not np.isnan(metrics['pearson_r']):
            corr = metrics['pearson_r']
            if abs(corr) < self.thresholds['min_correlation']:
                warnings.append(
                    f"Correlation coefficient ({corr:.3f}) is below threshold "
                    f"({self.thresholds['min_correlation']:.3f}). "
                    "Images may not be well aligned."
                )
                checks['correlation'] = 'WARNING'
            else:
                info.append(f"Correlation coefficient ({corr:.3f}) indicates good alignment.")
                checks['correlation'] = 'PASS'
        else:
            checks['correlation'] = 'UNKNOWN'

        # Check Mutual Information
        if 'normalized_mi' in metrics and not np.isnan(metrics['normalized_mi']):
            nmi = metrics['normalized_mi']
            if nmi < self.thresholds['min_mi']:
                warnings.append(
                    f"Normalized MI ({nmi:.3f}) is below threshold "
                    f"({self.thresholds['min_mi']:.3f}). "
                    "Low mutual information may indicate poor registration."
                )
                checks['mutual_information'] = 'WARNING'
            else:
                info.append(f"Normalized MI ({nmi:.3f}) is acceptable.")
                checks['mutual_information'] = 'PASS'
        else:
            checks['mutual_information'] = 'UNKNOWN'

        # Determine overall result
        passed = len(errors) == 0

        # Log results
        logger.info("\nQuality Check Results:")
        logger.info("-"*60)

        if errors:
            logger.error("ERRORS:")
            for msg in errors:
                logger.error(f"  ✗ {msg}")

        if warnings:
            logger.warning("WARNINGS:")
            for msg in warnings:
                logger.warning(f"  ⚠ {msg}")

        if info and not warnings and not errors:
            logger.info("INFO:")
            for msg in info:
                logger.info(f"  ✓ {msg}")

        if passed:
            logger.info("\n✓ All quality checks PASSED")
        else:
            logger.error("\n✗ Quality checks FAILED")

        logger.info("="*60)

        return {
            'passed': passed,
            'warnings': warnings,
            'errors': errors,
            'info': info,
            'checks': checks
        }

    def check_displacement(self, displacement_stats: Dict) -> Dict:
        """
        Check displacement statistics for anomalies.

        Parameters
        ----------
        displacement_stats : dict
            Displacement statistics

        Returns
        -------
        dict
            Check results
        """
        logger.info("Checking displacement statistics...")

        warnings = []
        info = []

        # Note: For landslide monitoring, large displacements are EXPECTED
        # So we don't warn about excessive displacement or unrealistic gradients

        # Check for data availability
        if 'n_valid_pixels' in displacement_stats:
            n_valid = displacement_stats['n_valid_pixels']
            if n_valid == 0:
                warnings.append("No valid displacement data available.")
            else:
                info.append(f"Displacement computed for {n_valid:,} valid pixels.")

        # Check for extreme outliers (may indicate errors)
        if 'magnitude_max' in displacement_stats:
            max_mag = displacement_stats['magnitude_max']
            mean_mag = displacement_stats.get('magnitude_mean', 0)

            # Flag if max is more than 10x the mean (potential outlier)
            if mean_mag > 0 and max_mag > 10 * mean_mag:
                info.append(
                    f"Maximum displacement ({max_mag:.2f}) is much larger than mean ({mean_mag:.2f}). "
                    "This is acceptable for landslide monitoring but verify extreme values."
                )

        # Summary
        logger.info("Displacement checks:")
        for msg in warnings + info:
            logger.info(f"  {msg}")

        return {
            'passed': len(warnings) == 0,
            'warnings': warnings,
            'info': info
        }

    def generate_quality_report(self, metrics: Dict, displacement_stats: Dict = None) -> str:
        """
        Generate a text quality report.

        Parameters
        ----------
        metrics : dict
            Quality metrics
        displacement_stats : dict, optional
            Displacement statistics

        Returns
        -------
        str
            Formatted quality report
        """
        lines = []
        lines.append("="*70)
        lines.append("GEOELASTIX QUALITY REPORT")
        lines.append("="*70)
        lines.append("")

        # Registration Quality Metrics
        lines.append("REGISTRATION QUALITY METRICS")
        lines.append("-"*70)

        if 'rmse' in metrics:
            lines.append(f"  Root Mean Square Error (RMSE):     {metrics['rmse']:.6f}")
        if 'mae' in metrics:
            lines.append(f"  Mean Absolute Error (MAE):         {metrics['mae']:.6f}")
        if 'mutual_information' in metrics:
            lines.append(f"  Mutual Information (MI):           {metrics['mutual_information']:.6f}")
        if 'normalized_mi' in metrics:
            lines.append(f"  Normalized MI:                     {metrics['normalized_mi']:.6f}")
        if 'pearson_r' in metrics:
            lines.append(f"  Correlation (Pearson r):           {metrics['pearson_r']:.6f}")
        if 'r_squared' in metrics:
            lines.append(f"  R² (coefficient of determination): {metrics['r_squared']:.6f}")

        lines.append("")

        # Coverage Statistics
        if 'overlap_coverage_percent' in metrics:
            lines.append("COVERAGE STATISTICS")
            lines.append("-"*70)
            lines.append(f"  Valid data overlap:                {metrics['overlap_coverage_percent']:.2f}%")
            if 'dice' in metrics:
                lines.append(f"  Dice coefficient:                  {metrics['dice']:.6f}")
            if 'iou' in metrics:
                lines.append(f"  Intersection over Union (IoU):     {metrics['iou']:.6f}")
            lines.append("")

        # Displacement Statistics
        if displacement_stats:
            lines.append("DISPLACEMENT STATISTICS")
            lines.append("-"*70)

            if 'x_mean' in displacement_stats:
                lines.append(f"  X displacement (East-West):")
                lines.append(f"    Mean: {displacement_stats['x_mean']:.6f} ± {displacement_stats['x_std']:.6f}")
                lines.append(f"    Range: [{displacement_stats['x_min']:.6f}, {displacement_stats['x_max']:.6f}]")

            if 'y_mean' in displacement_stats:
                lines.append(f"  Y displacement (North-South):")
                lines.append(f"    Mean: {displacement_stats['y_mean']:.6f} ± {displacement_stats['y_std']:.6f}")
                lines.append(f"    Range: [{displacement_stats['y_min']:.6f}, {displacement_stats['y_max']:.6f}]")

            if 'z_mean' in displacement_stats:
                lines.append(f"  Z displacement (Vertical):")
                lines.append(f"    Mean: {displacement_stats['z_mean']:.6f} ± {displacement_stats['z_std']:.6f}")
                lines.append(f"    Range: [{displacement_stats['z_min']:.6f}, {displacement_stats['z_max']:.6f}]")
                if 'uplift_area_percent' in displacement_stats:
                    lines.append(f"    Uplift area: {displacement_stats['uplift_area_percent']:.2f}%")
                if 'subsidence_area_percent' in displacement_stats:
                    lines.append(f"    Subsidence area: {displacement_stats['subsidence_area_percent']:.2f}%")

            if 'magnitude_mean' in displacement_stats:
                lines.append(f"  Horizontal magnitude:")
                lines.append(f"    Mean: {displacement_stats['magnitude_mean']:.6f} ± {displacement_stats['magnitude_std']:.6f}")
                lines.append(f"    Range: [{displacement_stats['magnitude_min']:.6f}, {displacement_stats['magnitude_max']:.6f}]")

            lines.append("")

        # Quality Checks
        check_results = self.check_metrics(metrics)

        lines.append("QUALITY ASSESSMENT")
        lines.append("-"*70)

        if check_results['errors']:
            lines.append("ERRORS:")
            for msg in check_results['errors']:
                lines.append(f"  ✗ {msg}")
            lines.append("")

        if check_results['warnings']:
            lines.append("WARNINGS:")
            for msg in check_results['warnings']:
                lines.append(f"  ⚠ {msg}")
            lines.append("")

        if not check_results['errors'] and not check_results['warnings']:
            lines.append("  ✓ All quality checks passed")
            lines.append("")

        lines.append("="*70)

        return "\n".join(lines)

    def save_report(self, report_text: str, output_path):
        """
        Save quality report to file.

        Parameters
        ----------
        report_text : str
            Report text
        output_path : str or Path
            Output file path
        """
        from pathlib import Path

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(report_text)

        logger.info(f"Quality report saved to: {output_path}")
