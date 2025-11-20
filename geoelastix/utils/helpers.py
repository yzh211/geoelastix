"""Helper utility functions."""

import os
from pathlib import Path
from .timestamp import generate_timestamp


def ensure_dir(directory):
    """
    Ensure a directory exists, creating it if necessary.

    Parameters
    ----------
    directory : str or Path
        Directory path

    Returns
    -------
    Path
        Path object for the directory
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_output_directory(base_dir, job_id, description=None, timestamp=None):
    """
    Generate output directory path with descriptive naming convention.

    Format: {base_dir}/{job_id}_{description}_{timestamp}/

    Parameters
    ----------
    base_dir : str or Path
        Base output directory
    job_id : str
        Job identifier
    description : str, optional
        Optional description (e.g., "2021_vs_2022")
    timestamp : str, optional
        Timestamp string. If None, generates current timestamp.

    Returns
    -------
    Path
        Output directory path

    Examples
    --------
    >>> get_output_directory("./output", "wrigley_landslide", "2021_vs_2022")
    Path('output/wrigley_landslide_2021_vs_2022_20241120_143022')

    >>> get_output_directory("./output", "analysis")
    Path('output/analysis_20241120_143022')
    """
    if timestamp is None:
        timestamp = generate_timestamp()

    # Build directory name
    if description:
        dir_name = f"{job_id}_{description}_{timestamp}"
    else:
        dir_name = f"{job_id}_{timestamp}"

    output_path = Path(base_dir) / dir_name
    return output_path


def get_file_size_mb(file_path):
    """
    Get file size in megabytes.

    Parameters
    ----------
    file_path : str or Path
        Path to file

    Returns
    -------
    float
        File size in MB
    """
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.

    Parameters
    ----------
    size_bytes : int
        Size in bytes

    Returns
    -------
    str
        Formatted size string (e.g., "12.5 MB", "1.2 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
