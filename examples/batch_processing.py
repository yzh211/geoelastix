"""Example: Batch processing multiple DEM pairs."""

from pathlib import Path
from geoelastix.cli import ConfigParser, WorkflowOrchestrator

def batch_process_time_series():
    """Process multiple DEM pairs in sequence."""

    # Define analyses
    analyses = [
        {
            'fixed': 'GIS/wrigley_30ft_lidar.tif',
            'moving': 'GIS/wrigley_30ft_legacy.tif',
            'job_id': 'analysis_legacy_vs_lidar',
            'description': 'Wrigley Legacy vs LiDAR'
        },
    ]

    # Process each pair
    results_summary = []

    for analysis in analyses:
        print(f"\n{'='*70}")
        print(f"Processing: {analysis['description']}")
        print(f"Job ID: {analysis['job_id']}")
        print(f"{'='*70}\n")

        # Build configuration
        config = ConfigParser.merge_with_defaults({
            'job': {
                'id': analysis['job_id'],
                'description': analysis['description'],
                'output_dir': './output'
            },
            'input': {
                'fixed_image': analysis['fixed'],
                'moving_image': analysis['moving']
            },
            'registration': {
                'method': 'NA',  # Use Non-Affine for landslide monitoring
                'metric': 'NCC'
            },
            'visualization': {
                'generate_plots': True,
                'plot_types': ['quiver', 'contour_magnitude']
            },
            'logging': {
                'level': 'INFO',
                'save_to_file': True
            }
        })

        # Validate configuration
        try:
            ConfigParser.validate_config(config)
        except ValueError as e:
            print(f"✗ Configuration validation failed for {analysis['job_id']}: {e}")
            continue

        # Run workflow
        try:
            orchestrator = WorkflowOrchestrator(config)
            results = orchestrator.run()

            # Store summary
            results_summary.append({
                'job_id': analysis['job_id'],
                'description': analysis['description'],
                'status': 'success',
                'output_dir': orchestrator.output_dir
            })

            print(f"\n✓ {analysis['job_id']} completed successfully")

        except Exception as e:
            print(f"\n✗ {analysis['job_id']} failed: {e}")
            results_summary.append({
                'job_id': analysis['job_id'],
                'description': analysis['description'],
                'status': 'failed',
                'error': str(e)
            })

    # Print summary
    print(f"\n\n{'='*70}")
    print("BATCH PROCESSING SUMMARY")
    print(f"{'='*70}\n")

    for result in results_summary:
        status_icon = '✓' if result['status'] == 'success' else '✗'
        print(f"{status_icon} {result['job_id']}: {result['status'].upper()}")
        if result['status'] == 'success':
            print(f"   Output: {result['output_dir']}")
        else:
            print(f"   Error: {result['error']}")
        print()

    success_count = sum(1 for r in results_summary if r['status'] == 'success')
    print(f"Completed: {success_count}/{len(results_summary)} analyses")

    return results_summary


if __name__ == '__main__':
    results = batch_process_time_series()
