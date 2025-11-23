"""PDF report generation for registration results."""

import logging
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger("geoelastix.visualization")


class ReportGenerator:
    """
    Generate comprehensive PDF reports with metrics and visualizations.

    Creates reports summarizing registration quality, displacement statistics,
    and includes visualization plots.
    """

    def __init__(self, output_dir):
        """
        Initialize report generator.

        Parameters
        ----------
        output_dir : str or Path
            Output directory for report
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized ReportGenerator: {self.output_dir}")

    def generate_text_report(self, job_info, metrics, displacement_stats=None,
                            quality_checks=None, output_filename="report.txt"):
        """
        Generate text-based report.

        Parameters
        ----------
        job_info : dict
            Job information (id, timestamp, input files, parameters)
        metrics : dict
            Quality metrics
        displacement_stats : dict, optional
            Displacement statistics
        quality_checks : dict, optional
            Quality check results
        output_filename : str, optional
            Output filename. Default: "report.txt"

        Returns
        -------
        Path
            Path to generated report
        """
        logger.info("Generating text report...")

        output_path = self.output_dir / output_filename

        lines = []

        # Header
        lines.append("="*80)
        lines.append("GEOELASTIX REGISTRATION REPORT")
        lines.append("="*80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Job Information
        lines.append("JOB INFORMATION")
        lines.append("-"*80)
        if 'id' in job_info:
            lines.append(f"  Job ID: {job_info['id']}")
        if 'description' in job_info:
            lines.append(f"  Description: {job_info['description']}")
        if 'timestamp' in job_info:
            lines.append(f"  Timestamp: {job_info['timestamp']}")
        if 'fixed_image' in job_info:
            lines.append(f"  Fixed image: {job_info['fixed_image']}")
        if 'moving_image' in job_info:
            lines.append(f"  Moving image: {job_info['moving_image']}")
        if 'method' in job_info:
            lines.append(f"  Registration method: {job_info['method']}")
        if 'metric' in job_info:
            lines.append(f"  Similarity metric: {job_info['metric']}")
        lines.append("")

        # Registration Quality Metrics
        lines.append("REGISTRATION QUALITY METRICS")
        lines.append("-"*80)

        # RMSE and MAE removed - not meaningful for DEM registration
        # if 'rmse' in metrics:
        #     lines.append(f"  Root Mean Square Error (RMSE):     {metrics['rmse']:.6f}")
        # if 'mae' in metrics:
        #     lines.append(f"  Mean Absolute Error (MAE):         {metrics['mae']:.6f}")

        if 'mutual_information' in metrics:
            lines.append(f"  Mutual Information (MI):           {metrics['mutual_information']:.6f}")
        if 'normalized_mi' in metrics:
            lines.append(f"  Normalized MI:                     {metrics['normalized_mi']:.6f}")

        # Correlation removed - not meaningful for DEM registration
        # if 'pearson_r' in metrics:
        #     lines.append(f"  Correlation (Pearson r):           {metrics['pearson_r']:.6f}")
        # if 'r_squared' in metrics:
        #     lines.append(f"  R² (coefficient of determination): {metrics['r_squared']:.6f}")

        lines.append("")

        # Coverage Statistics
        if 'overlap_coverage_percent' in metrics:
            lines.append("COVERAGE STATISTICS")
            lines.append("-"*80)
            lines.append(f"  Valid data overlap:                {metrics['overlap_coverage_percent']:.2f}%")
            if 'dice' in metrics:
                lines.append(f"  Dice coefficient:                  {metrics['dice']:.6f}")
            if 'iou' in metrics:
                lines.append(f"  Intersection over Union (IoU):     {metrics['iou']:.6f}")
            if 'overlap_pixels' in metrics:
                lines.append(f"  Overlap pixels:                    {metrics['overlap_pixels']:,}")
            lines.append("")

        # Displacement Statistics
        if displacement_stats:
            lines.append("DISPLACEMENT STATISTICS")
            lines.append("-"*80)

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
                lines.append(f"    RMSE: {displacement_stats.get('z_rmse', 0):.6f}")
                if 'uplift_area_percent' in displacement_stats:
                    lines.append(f"    Uplift area: {displacement_stats['uplift_area_percent']:.2f}%")
                if 'subsidence_area_percent' in displacement_stats:
                    lines.append(f"    Subsidence area: {displacement_stats['subsidence_area_percent']:.2f}%")

            if 'magnitude_mean' in displacement_stats:
                lines.append(f"  Horizontal magnitude:")
                lines.append(f"    Mean: {displacement_stats['magnitude_mean']:.6f} ± {displacement_stats['magnitude_std']:.6f}")
                lines.append(f"    Range: [{displacement_stats['magnitude_min']:.6f}, {displacement_stats['magnitude_max']:.6f}]")
                lines.append(f"    Median: {displacement_stats.get('magnitude_median', 0):.6f}")
                lines.append(f"    95th percentile: {displacement_stats.get('magnitude_percentile_95', 0):.6f}")

            if 'n_valid_pixels' in displacement_stats:
                lines.append(f"  Valid pixels: {displacement_stats['n_valid_pixels']:,}")

            lines.append("")

        # Quality Checks
        if quality_checks:
            lines.append("QUALITY ASSESSMENT")
            lines.append("-"*80)

            if quality_checks.get('errors'):
                lines.append("ERRORS:")
                for msg in quality_checks['errors']:
                    lines.append(f"  ✗ {msg}")
                lines.append("")

            if quality_checks.get('warnings'):
                lines.append("WARNINGS:")
                for msg in quality_checks['warnings']:
                    lines.append(f"  ⚠ {msg}")
                lines.append("")

            if not quality_checks.get('errors') and not quality_checks.get('warnings'):
                lines.append("  ✓ All quality checks passed")
                lines.append("")

            # Individual check results
            if quality_checks.get('checks'):
                lines.append("DETAILED CHECKS:")
                for check_name, result in quality_checks['checks'].items():
                    status_icon = {'PASS': '✓', 'WARNING': '⚠', 'ERROR': '✗', 'UNKNOWN': '?'}.get(result, '?')
                    lines.append(f"  {status_icon} {check_name}: {result}")
                lines.append("")

        # Output Files
        if 'output_files' in job_info:
            lines.append("OUTPUT FILES")
            lines.append("-"*80)
            for category, files in job_info['output_files'].items():
                lines.append(f"  {category}:")
                for file in files:
                    lines.append(f"    - {file}")
            lines.append("")

        # Footer
        lines.append("="*80)
        lines.append("End of Report")
        lines.append("="*80)
        lines.append("")
        lines.append("Generated by GeoElastix")
        lines.append("https://github.com/yzh211/geoelastix")
        lines.append("")

        # Write to file (use UTF-8 encoding for Unicode characters)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        logger.info(f"Text report saved to: {output_path}")

        return output_path

    def save_metrics_json(self, metrics, displacement_stats=None,
                         quality_checks=None, output_filename="metrics.json"):
        """
        Save metrics to JSON file for machine-readable format.

        Parameters
        ----------
        metrics : dict
            Quality metrics
        displacement_stats : dict, optional
            Displacement statistics
        quality_checks : dict, optional
            Quality check results
        output_filename : str, optional
            Output filename

        Returns
        -------
        Path
            Path to JSON file
        """
        logger.info("Saving metrics to JSON...")

        output_path = self.output_dir / output_filename

        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }

        if displacement_stats:
            data['displacement_statistics'] = displacement_stats

        if quality_checks:
            data['quality_checks'] = quality_checks

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Metrics JSON saved to: {output_path}")

        return output_path

    def create_summary_figure(self, plots_dict, output_filename="summary.png",
                             dpi=150, figsize=(16, 12)):
        """
        Create a summary figure with multiple plots.

        Parameters
        ----------
        plots_dict : dict
            Dictionary of {title: figure} or {title: image_array}
        output_filename : str, optional
            Output filename
        dpi : int, optional
            Figure DPI
        figsize : tuple, optional
            Figure size

        Returns
        -------
        Path
            Path to summary figure
        """
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg

        logger.info("Creating summary figure...")

        output_path = self.output_dir / output_filename

        n_plots = len(plots_dict)
        if n_plots == 0:
            logger.warning("No plots provided for summary figure")
            return None

        # Determine grid layout
        if n_plots == 1:
            nrows, ncols = 1, 1
        elif n_plots == 2:
            nrows, ncols = 1, 2
        elif n_plots <= 4:
            nrows, ncols = 2, 2
        elif n_plots <= 6:
            nrows, ncols = 2, 3
        else:
            nrows = (n_plots + 2) // 3
            ncols = 3

        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, dpi=dpi)
        if n_plots == 1:
            axes = [axes]
        else:
            axes = axes.flatten()

        # Plot each image
        for idx, (title, plot_data) in enumerate(plots_dict.items()):
            if idx >= len(axes):
                break

            ax = axes[idx]

            # Load image if it's a file path
            if isinstance(plot_data, (str, Path)):
                img = mpimg.imread(str(plot_data))
                ax.imshow(img)
            else:
                # Assume it's a numpy array
                ax.imshow(plot_data)

            ax.set_title(title, fontsize=10, fontweight='bold')
            ax.axis('off')

        # Hide unused subplots
        for idx in range(n_plots, len(axes)):
            axes[idx].axis('off')

        plt.tight_layout()
        fig.savefig(output_path, bbox_inches='tight', dpi=dpi)
        plt.close(fig)

        logger.info(f"Summary figure saved to: {output_path}")

        return output_path

    @staticmethod
    def format_number(value, precision=3):
        """Format number for display."""
        if isinstance(value, (int, np.integer)):
            return f"{value:,}"
        elif isinstance(value, (float, np.floating)):
            if abs(value) < 0.001 or abs(value) > 10000:
                return f"{value:.{precision}e}"
            else:
                return f"{value:.{precision}f}"
        else:
            return str(value)


# Import numpy for type checking
import numpy as np
