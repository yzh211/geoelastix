"""Edge handling for seamless tile blending."""

import numpy as np
import logging

logger = logging.getLogger("geoelastix.tiling")


class EdgeHandler:
    """
    Handle edge blending for tiled processing.

    Provides methods for creating feather masks and blending
    overlapping tile regions seamlessly.
    """

    def __init__(self, overlap=100):
        """
        Initialize edge handler.

        Parameters
        ----------
        overlap : int, optional
            Overlap width in pixels. Default: 100
        """
        self.overlap = overlap
        logger.debug(f"Initialized EdgeHandler with overlap={overlap}")

    def create_feather_mask(self, height, width, overlap=None):
        """
        Create feathering weight mask for a tile.

        The mask has values from 0 to 1, with smooth transitions
        in the overlap regions to enable seamless blending.

        Parameters
        ----------
        height : int
            Tile height
        width : int
            Tile width
        overlap : int, optional
            Overlap width. If None, uses self.overlap

        Returns
        -------
        numpy.ndarray
            Feather mask (0-1 values) with shape (height, width)
        """
        if overlap is None:
            overlap = self.overlap

        # Initialize mask with ones
        mask = np.ones((height, width), dtype=np.float32)

        if overlap <= 0:
            return mask

        # Create 1D feather profiles
        # Linear ramp from 0 to 1 over overlap distance
        ramp = np.linspace(0, 1, overlap)

        # Apply feathering to edges
        # Top edge
        if height > overlap:
            mask[:overlap, :] *= ramp[:, np.newaxis]

        # Bottom edge
        if height > overlap:
            mask[-overlap:, :] *= ramp[::-1, np.newaxis]

        # Left edge
        if width > overlap:
            mask[:, :overlap] *= ramp[np.newaxis, :]

        # Right edge
        if width > overlap:
            mask[:, -overlap:] *= ramp[::-1][np.newaxis, :]

        return mask

    def create_distance_weight_mask(self, height, width):
        """
        Create distance-based weight mask.

        Weight is based on distance from tile edges, giving higher
        weight to central pixels.

        Parameters
        ----------
        height : int
            Tile height
        width : int
            Tile width

        Returns
        -------
        numpy.ndarray
            Weight mask with shape (height, width)
        """
        # Create distance from edges
        y_coords = np.arange(height)
        x_coords = np.arange(width)

        # Distance from top/bottom edges
        y_dist = np.minimum(y_coords, height - 1 - y_coords)

        # Distance from left/right edges
        x_dist = np.minimum(x_coords, width - 1 - x_coords)

        # Create 2D distance field
        y_field = y_dist[:, np.newaxis]
        x_field = x_dist[np.newaxis, :]

        # Minimum distance to any edge
        dist_field = np.minimum(y_field, x_field)

        # Normalize to 0-1
        max_dist = np.max(dist_field)
        if max_dist > 0:
            weight_mask = dist_field / max_dist
        else:
            weight_mask = np.ones((height, width), dtype=np.float32)

        return weight_mask.astype(np.float32)

    def blend_tiles(self, tile1, tile2, overlap_direction='horizontal'):
        """
        Blend two overlapping tiles.

        Parameters
        ----------
        tile1 : numpy.ndarray
            First tile array
        tile2 : numpy.ndarray
            Second tile array
        overlap_direction : str, optional
            Direction of overlap: 'horizontal' or 'vertical'. Default: 'horizontal'

        Returns
        -------
        numpy.ndarray
            Blended result
        """
        if tile1.shape != tile2.shape:
            raise ValueError("Tiles must have the same shape for blending")

        height, width = tile1.shape

        if overlap_direction == 'horizontal':
            # Blend horizontally (left-right overlap)
            # Create weight ramp: 1 on left, 0 on right
            weights = np.linspace(1, 0, width)[np.newaxis, :]
            blended = tile1 * weights + tile2 * (1 - weights)

        elif overlap_direction == 'vertical':
            # Blend vertically (top-bottom overlap)
            # Create weight ramp: 1 on top, 0 on bottom
            weights = np.linspace(1, 0, height)[:, np.newaxis]
            blended = tile1 * weights + tile2 * (1 - weights)

        else:
            raise ValueError(f"Unknown overlap direction: {overlap_direction}")

        return blended.astype(tile1.dtype)

    def extract_core_region(self, tile_array, overlap=None):
        """
        Extract core region of tile (excluding overlap edges).

        Parameters
        ----------
        tile_array : numpy.ndarray
            Tile array
        overlap : int, optional
            Overlap width. If None, uses self.overlap

        Returns
        -------
        numpy.ndarray
            Core region array
        """
        if overlap is None:
            overlap = self.overlap

        if overlap <= 0:
            return tile_array

        height, width = tile_array.shape

        # Calculate core boundaries
        row_start = overlap // 2
        row_end = height - (overlap - overlap // 2)
        col_start = overlap // 2
        col_end = width - (overlap - overlap // 2)

        # Ensure valid slice
        row_start = max(0, row_start)
        col_start = max(0, col_start)
        row_end = min(height, row_end)
        col_end = min(width, col_end)

        return tile_array[row_start:row_end, col_start:col_end]

    def create_gaussian_feather_mask(self, height, width, sigma=None):
        """
        Create Gaussian-based feather mask for smoother blending.

        Parameters
        ----------
        height : int
            Tile height
        width : int
            Tile width
        sigma : float, optional
            Gaussian sigma. If None, uses overlap/3

        Returns
        -------
        numpy.ndarray
            Gaussian feather mask
        """
        from scipy.ndimage import gaussian_filter

        if sigma is None:
            sigma = self.overlap / 3.0

        # Start with distance-based mask
        mask = self.create_distance_weight_mask(height, width)

        # Apply Gaussian smoothing for smoother transitions
        mask = gaussian_filter(mask, sigma=sigma)

        # Renormalize to 0-1
        mask_min = np.min(mask)
        mask_max = np.max(mask)
        if mask_max > mask_min:
            mask = (mask - mask_min) / (mask_max - mask_min)

        return mask.astype(np.float32)

    def detect_edge_artifacts(self, array, edge_width=None, threshold=2.0):
        """
        Detect potential edge artifacts in processed tile.

        Parameters
        ----------
        array : numpy.ndarray
            Processed tile array
        edge_width : int, optional
            Width of edge region to check. If None, uses overlap
        threshold : float, optional
            Threshold for artifact detection (in standard deviations). Default: 2.0

        Returns
        -------
        dict
            Artifact detection results with boolean flags and statistics
        """
        if edge_width is None:
            edge_width = self.overlap

        height, width = array.shape

        # Extract edge regions
        top_edge = array[:edge_width, :]
        bottom_edge = array[-edge_width:, :]
        left_edge = array[:, :edge_width]
        right_edge = array[:, -edge_width:]

        # Compute statistics for each edge
        edges = {
            'top': top_edge,
            'bottom': bottom_edge,
            'left': left_edge,
            'right': right_edge
        }

        # Overall array statistics
        array_mean = np.nanmean(array)
        array_std = np.nanstd(array)

        results = {
            'has_artifacts': False,
            'edges': {}
        }

        for edge_name, edge_data in edges.items():
            edge_mean = np.nanmean(edge_data)
            edge_std = np.nanstd(edge_data)

            # Check if edge statistics deviate significantly from overall
            mean_diff = abs(edge_mean - array_mean)
            is_anomalous = mean_diff > threshold * array_std

            results['edges'][edge_name] = {
                'mean': float(edge_mean),
                'std': float(edge_std),
                'mean_diff': float(mean_diff),
                'is_anomalous': bool(is_anomalous)
            }

            if is_anomalous:
                results['has_artifacts'] = True

        return results

    @staticmethod
    def apply_edge_mask(array, mask_width, value=np.nan):
        """
        Mask edge pixels to a specified value.

        Parameters
        ----------
        array : numpy.ndarray
            Input array
        mask_width : int
            Width of edge mask in pixels
        value : float, optional
            Value to set edge pixels to. Default: np.nan

        Returns
        -------
        numpy.ndarray
            Array with masked edges
        """
        result = array.copy()

        if mask_width <= 0:
            return result

        height, width = array.shape

        # Mask edges
        result[:mask_width, :] = value  # Top
        result[-mask_width:, :] = value  # Bottom
        result[:, :mask_width] = value  # Left
        result[:, -mask_width:] = value  # Right

        return result
