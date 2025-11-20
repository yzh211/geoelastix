"""Timestamp generation utilities."""

from datetime import datetime


def generate_timestamp(format_string="%Y%m%d_%H%M%S"):
    """
    Generate a timestamp string.

    Parameters
    ----------
    format_string : str, optional
        Format string for datetime.strftime(). Default: "%Y%m%d_%H%M%S"

    Returns
    -------
    str
        Formatted timestamp string

    Examples
    --------
    >>> timestamp = generate_timestamp()
    >>> print(timestamp)
    '20241120_143022'

    >>> timestamp = generate_timestamp("%Y-%m-%d")
    >>> print(timestamp)
    '2024-11-20'
    """
    return datetime.now().strftime(format_string)
