"""Displacement magnitude calculation."""

import numpy as np
import logging

logger = logging.getLogger("geoelastix.displacement")


class DisplacementMagnitude:
    """
    Calculate displacement magnitude from X, Y, Z components.

    Provides methods to compute total displacement magnitude in 2D and 3D.
    """

    @staticmethod
    def compute_horizontal_magnitude(displacement_x, displacement_y):
        """
        Compute horizontal displacement magnitude.

        magnitude = sqrt(x² + y²)

        Parameters
        ----------
        displacement_x : numpy.ndarray
            X displacement (East-West)
        displacement_y : numpy.ndarray
            Y displacement (North-South)

        Returns
        -------
        dict
            Dictionary containing:
            - 'magnitude': numpy array of horizontal displacement magnitude
            - 'direction': numpy array of displacement direction (radians)
            - 'statistics': magnitude statistics
        """
        logger.info("Computing horizontal displacement magnitude...")

        # Check shapes match
        if displacement_x.shape != displacement_y.shape:
            raise ValueError(
                f"Shape mismatch: X {displacement_x.shape} vs Y {displacement_y.shape}"
            )

        # Compute magnitude
        magnitude = np.sqrt(displacement_x**2 + displacement_y**2).astype(np.float32)

        # Compute direction (angle from East, counterclockwise)
        # atan2(y, x) gives angle in radians
        direction = np.arctan2(displacement_y, displacement_x).astype(np.float32)

        # Compute statistics
        stats = DisplacementMagnitude.get_statistics(magnitude)

        logger.info(f"  Magnitude range: [{stats['min']:.3f}, {stats['max']:.3f}]")
        logger.info(f"  Mean magnitude: {stats['mean']:.3f} ± {stats['std']:.3f}")

        return {
            'magnitude': magnitude,
            'direction': direction,
            'statistics': stats
        }

    @staticmethod
    def compute_3d_magnitude(displacement_x, displacement_y, displacement_z):
        """
        Compute 3D displacement magnitude.

        magnitude = sqrt(x² + y² + z²)

        Parameters
        ----------
        displacement_x : numpy.ndarray
            X displacement
        displacement_y : numpy.ndarray
            Y displacement
        displacement_z : numpy.ndarray
            Z displacement

        Returns
        -------
        dict
            Dictionary with magnitude and statistics
        """
        logger.info("Computing 3D displacement magnitude...")

        # Check shapes match
        if not (displacement_x.shape == displacement_y.shape == displacement_z.shape):
            raise ValueError("Displacement arrays must have the same shape")

        # Compute 3D magnitude
        magnitude_3d = np.sqrt(
            displacement_x**2 + displacement_y**2 + displacement_z**2
        ).astype(np.float32)

        # Compute statistics
        stats = DisplacementMagnitude.get_statistics(magnitude_3d)

        logger.info(f"  3D magnitude range: [{stats['min']:.3f}, {stats['max']:.3f}]")

        return {
            'magnitude_3d': magnitude_3d,
            'statistics': stats
        }

    @staticmethod
    def get_displacement_direction_name(direction_radians):
        """
        Convert direction in radians to compass direction name.

        Parameters
        ----------
        direction_radians : float or numpy.ndarray
            Direction in radians (0 = East, π/2 = North)

        Returns
        -------
        str or numpy.ndarray
            Direction name(s): N, NE, E, SE, S, SW, W, NW
        """
        # Convert radians to degrees (0-360)
        degrees = np.degrees(direction_radians) % 360

        # Define direction bins
        directions = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE']
        bin_size = 360 / 8  # 45 degrees per bin
        offset = bin_size / 2  # Start bins at -22.5 degrees

        if isinstance(degrees, np.ndarray):
            # Vectorized version for arrays
            indices = ((degrees + offset) / bin_size).astype(int) % 8
            return np.array([directions[i] for i in indices.flatten()]).reshape(degrees.shape)
        else:
            # Single value
            index = int((degrees + offset) / bin_size) % 8
            return directions[index]

    @staticmethod
    def apply_mask(magnitude, mask):
        """
        Apply mask to magnitude field.

        Parameters
        ----------
        magnitude : numpy.ndarray
            Magnitude field
        mask : numpy.ndarray
            Binary mask (1=valid, 0=no-data)

        Returns
        -------
        numpy.ndarray
            Masked magnitude field
        """
        masked_magnitude = magnitude.copy()
        masked_magnitude[mask == 0] = np.nan
        return masked_magnitude

    @staticmethod
    def get_statistics(magnitude, mask=None):
        """
        Compute statistics for magnitude field.

        Parameters
        ----------
        magnitude : numpy.ndarray
            Magnitude field
        mask : numpy.ndarray, optional
            Binary mask for valid regions

        Returns
        -------
        dict
            Statistics dictionary
        """
        if mask is not None:
            valid_mask = mask > 0
            mag = magnitude[valid_mask]
        else:
            mag = magnitude.flatten()

        # Remove NaN values
        mag = mag[~np.isnan(mag)]

        if len(mag) == 0:
            logger.warning("No valid data for magnitude statistics")
            return {
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0,
                'median': 0.0,
                'percentile_95': 0.0,
                'percentile_99': 0.0,
                'n_valid_pixels': 0
            }

        stats = {
            'mean': float(np.mean(mag)),
            'std': float(np.std(mag)),
            'min': float(np.min(mag)),
            'max': float(np.max(mag)),
            'median': float(np.median(mag)),
            'percentile_95': float(np.percentile(mag, 95)),
            'percentile_99': float(np.percentile(mag, 99)),
            'n_valid_pixels': int(len(mag))
        }

        return stats

    @staticmethod
    def classify_magnitude(magnitude, thresholds=None):
        """
        Classify displacement magnitude into categories.

        Parameters
        ----------
        magnitude : numpy.ndarray
            Displacement magnitude field
        thresholds : list, optional
            Threshold values for classification. Default: [0.5, 1.0, 2.0, 5.0]
            Creates categories: [0-0.5), [0.5-1.0), [1.0-2.0), [2.0-5.0), [5.0+)

        Returns
        -------
        numpy.ndarray
            Classification array (0 to N categories)
        """
        if thresholds is None:
            thresholds = [0.5, 1.0, 2.0, 5.0]

        classification = np.zeros(magnitude.shape, dtype=np.int8)

        for i, threshold in enumerate(thresholds):
            classification[magnitude >= threshold] = i + 1

        # Mark no-data
        classification[np.isnan(magnitude)] = -1

        return classification

    @staticmethod
    def compute_displacement_vector_field(displacement_x, displacement_y,
                                         subsample=1):
        """
        Prepare vector field data for quiver plots.

        Parameters
        ----------
        displacement_x : numpy.ndarray
            X displacement
        displacement_y : numpy.ndarray
            Y displacement
        subsample : int, optional
            Subsampling factor (e.g., 10 means every 10th point). Default: 1

        Returns
        -------
        dict
            Dictionary with subsampled coordinates and displacement vectors
        """
        height, width = displacement_x.shape

        # Create coordinate grids
        y_coords, x_coords = np.mgrid[0:height:subsample, 0:width:subsample]

        # Subsample displacement fields
        u = displacement_x[::subsample, ::subsample]
        v = displacement_y[::subsample, ::subsample]

        # Compute magnitude for subsampled field
        magnitude = np.sqrt(u**2 + v**2)

        return {
            'x': x_coords,
            'y': y_coords,
            'u': u,
            'v': v,
            'magnitude': magnitude,
            'n_vectors': x_coords.size
        }

    @staticmethod
    def compute_strain_rate(displacement_x, displacement_y, spacing=1.0):
        """
        Compute strain rate from displacement field.

        This is useful for understanding deformation patterns.

        Parameters
        ----------
        displacement_x : numpy.ndarray
            X displacement
        displacement_y : numpy.ndarray
            Y displacement
        spacing : float or tuple, optional
            Pixel spacing. Default: 1.0

        Returns
        -------
        dict
            Dictionary with strain components and principal strains
        """
        logger.info("Computing strain rate from displacement field...")

        if isinstance(spacing, (tuple, list)):
            dy_spacing = spacing[1]
            dx_spacing = spacing[0]
        else:
            dy_spacing = dx_spacing = spacing

        # Compute gradients
        du_dy, du_dx = np.gradient(displacement_x, dy_spacing, dx_spacing)
        dv_dy, dv_dx = np.gradient(displacement_y, dy_spacing, dx_spacing)

        # Strain components
        exx = du_dx  # Normal strain in x
        eyy = dv_dy  # Normal strain in y
        exy = 0.5 * (du_dy + dv_dx)  # Shear strain

        # Principal strains
        # e1, e2 = eigenvalues of strain tensor
        trace = exx + eyy
        det = exx * eyy - exy**2

        discriminant = trace**2 - 4*det
        discriminant[discriminant < 0] = 0  # Handle numerical errors

        e1 = (trace + np.sqrt(discriminant)) / 2  # Maximum principal strain
        e2 = (trace - np.sqrt(discriminant)) / 2  # Minimum principal strain

        # Maximum shear strain
        max_shear = (e1 - e2) / 2

        logger.info("  Strain rate computed")

        return {
            'exx': exx.astype(np.float32),
            'eyy': eyy.astype(np.float32),
            'exy': exy.astype(np.float32),
            'e1': e1.astype(np.float32),  # Max principal strain
            'e2': e2.astype(np.float32),  # Min principal strain
            'max_shear': max_shear.astype(np.float32)
        }
