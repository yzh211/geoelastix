"""Vertical displacement calculation from elevation difference."""

import numpy as np
import logging
import itk

logger = logging.getLogger("geoelastix.displacement")


class VerticalDisplacement:
    """
    Calculate vertical displacement (Z) from elevation difference.

    Computes Z displacement by directly comparing elevation values
    between fixed and registered moving images.
    """

    @staticmethod
    def compute_from_images(fixed_image, registered_moving_image, nodata_value=None):
        """
        Compute vertical displacement from image elevation difference.

        Z_displacement = Fixed_elevation - Registered_moving_elevation

        Positive values indicate uplift, negative values indicate subsidence.

        Parameters
        ----------
        fixed_image : itk.Image or numpy.ndarray
            Fixed (reference) image
        registered_moving_image : itk.Image or numpy.ndarray
            Registered moving image
        nodata_value : float, optional
            No-data value to set for invalid regions

        Returns
        -------
        dict
            Dictionary containing:
            - 'displacement_z': numpy array of vertical displacement
            - 'residual': numpy array (same as displacement_z)
            - 'statistics': displacement statistics
        """
        logger.info("Computing vertical displacement from elevation difference...")

        # Convert to numpy arrays if needed
        if hasattr(fixed_image, 'GetLargestPossibleRegion'):
            # It's an ITK image
            fixed_array = itk.array_from_image(fixed_image)
        else:
            fixed_array = np.array(fixed_image)

        if hasattr(registered_moving_image, 'GetLargestPossibleRegion'):
            registered_array = itk.array_from_image(registered_moving_image)
        else:
            registered_array = np.array(registered_moving_image)

        # Check shapes match
        if fixed_array.shape != registered_array.shape:
            raise ValueError(
                f"Image shape mismatch: fixed {fixed_array.shape} vs "
                f"registered {registered_array.shape}"
            )

        logger.info(f"  Image shape: {fixed_array.shape}")

        # Compute vertical displacement
        # Z_displacement = Fixed - Registered_moving
        # Positive = uplift, Negative = subsidence
        displacement_z = (fixed_array - registered_array).astype(np.float32)

        # Handle no-data regions
        if nodata_value is not None:
            # Identify no-data in either image
            invalid_fixed = np.isnan(fixed_array) if np.issubdtype(fixed_array.dtype, np.floating) else (fixed_array == nodata_value)
            invalid_registered = np.isnan(registered_array) if np.issubdtype(registered_array.dtype, np.floating) else (registered_array == nodata_value)

            invalid_mask = invalid_fixed | invalid_registered
            displacement_z[invalid_mask] = np.nan

        # Compute statistics
        stats = VerticalDisplacement.get_statistics(displacement_z)

        logger.info(f"  Vertical displacement range: [{stats['z_min']:.3f}, {stats['z_max']:.3f}]")
        logger.info(f"  Mean vertical displacement: {stats['z_mean']:.3f} ± {stats['z_std']:.3f}")

        return {
            'displacement_z': displacement_z,
            'residual': displacement_z,  # Same as displacement
            'statistics': stats
        }

    @staticmethod
    def compute_from_arrays(fixed_array, registered_array, mask=None):
        """
        Compute vertical displacement from numpy arrays.

        Parameters
        ----------
        fixed_array : numpy.ndarray
            Fixed (reference) elevation array
        registered_array : numpy.ndarray
            Registered moving elevation array
        mask : numpy.ndarray, optional
            Binary mask (1=valid, 0=no-data)

        Returns
        -------
        dict
            Dictionary with displacement_z and statistics
        """
        logger.info("Computing vertical displacement from arrays...")

        # Compute displacement
        displacement_z = (fixed_array - registered_array).astype(np.float32)

        # Apply mask if provided
        if mask is not None:
            displacement_z[mask == 0] = np.nan

        # Compute statistics
        stats = VerticalDisplacement.get_statistics(displacement_z)

        logger.info(f"  Vertical displacement computed")
        logger.info(f"  Range: [{stats['z_min']:.3f}, {stats['z_max']:.3f}]")

        return {
            'displacement_z': displacement_z,
            'statistics': stats
        }

    @staticmethod
    def apply_mask(displacement_z, mask):
        """
        Apply mask to vertical displacement field.

        Parameters
        ----------
        displacement_z : numpy.ndarray
            Z displacement field
        mask : numpy.ndarray
            Binary mask (1=valid, 0=no-data)

        Returns
        -------
        numpy.ndarray
            Masked displacement field
        """
        masked_z = displacement_z.copy()
        masked_z[mask == 0] = np.nan
        return masked_z

    @staticmethod
    def get_statistics(displacement_z, mask=None):
        """
        Compute statistics for vertical displacement field.

        Parameters
        ----------
        displacement_z : numpy.ndarray
            Vertical displacement field
        mask : numpy.ndarray, optional
            Binary mask for valid regions

        Returns
        -------
        dict
            Statistics dictionary
        """
        if mask is not None:
            valid_mask = mask > 0
            dz = displacement_z[valid_mask]
        else:
            dz = displacement_z.flatten()

        # Remove NaN values
        dz = dz[~np.isnan(dz)]

        if len(dz) == 0:
            logger.warning("No valid data for statistics calculation")
            return {
                'z_mean': 0.0,
                'z_std': 0.0,
                'z_min': 0.0,
                'z_max': 0.0,
                'z_median': 0.0,
                'z_rmse': 0.0,
                'n_valid_pixels': 0,
                'uplift_area_percent': 0.0,
                'subsidence_area_percent': 0.0
            }

        # Basic statistics
        z_mean = float(np.mean(dz))
        z_std = float(np.std(dz))
        z_min = float(np.min(dz))
        z_max = float(np.max(dz))
        z_median = float(np.median(dz))

        # RMSE (relative to zero)
        z_rmse = float(np.sqrt(np.mean(dz**2)))

        # Count uplift and subsidence
        n_total = len(dz)
        n_uplift = np.sum(dz > 0)
        n_subsidence = np.sum(dz < 0)

        uplift_percent = (n_uplift / n_total) * 100 if n_total > 0 else 0.0
        subsidence_percent = (n_subsidence / n_total) * 100 if n_total > 0 else 0.0

        stats = {
            'z_mean': z_mean,
            'z_std': z_std,
            'z_min': z_min,
            'z_max': z_max,
            'z_median': z_median,
            'z_rmse': z_rmse,
            'n_valid_pixels': int(n_total),
            'uplift_area_percent': float(uplift_percent),
            'subsidence_area_percent': float(subsidence_percent)
        }

        return stats

    @staticmethod
    def classify_displacement(displacement_z, thresholds=None):
        """
        Classify vertical displacement into categories.

        Parameters
        ----------
        displacement_z : numpy.ndarray
            Vertical displacement field
        thresholds : dict, optional
            Threshold values for classification:
            - 'significant_uplift': threshold for significant uplift (default: 1.0)
            - 'significant_subsidence': threshold for significant subsidence (default: -1.0)

        Returns
        -------
        numpy.ndarray
            Classification array:
            - 3: Significant uplift
            - 2: Minor uplift
            - 1: Stable
            - 0: Minor subsidence
            - -1: Significant subsidence
            - nan: No data
        """
        if thresholds is None:
            thresholds = {
                'significant_uplift': 1.0,
                'significant_subsidence': -1.0
            }

        classification = np.full(displacement_z.shape, 1, dtype=np.int8)  # Default: stable

        # Significant uplift
        classification[displacement_z > thresholds['significant_uplift']] = 3

        # Minor uplift
        classification[(displacement_z > 0) & (displacement_z <= thresholds['significant_uplift'])] = 2

        # Minor subsidence
        classification[(displacement_z < 0) & (displacement_z >= thresholds['significant_subsidence'])] = 0

        # Significant subsidence
        classification[displacement_z < thresholds['significant_subsidence']] = -1

        # No data
        classification[np.isnan(displacement_z)] = -128  # Special value for no-data

        return classification

    @staticmethod
    def compute_gradient(displacement_z, spacing=1.0):
        """
        Compute gradient of vertical displacement field.

        This can help identify areas of rapid elevation change.

        Parameters
        ----------
        displacement_z : numpy.ndarray
            Vertical displacement field
        spacing : float or tuple, optional
            Pixel spacing in map units. Default: 1.0

        Returns
        -------
        dict
            Dictionary with gradient_y, gradient_x, gradient_magnitude
        """
        logger.info("Computing vertical displacement gradient...")

        # Compute gradients
        if isinstance(spacing, (tuple, list)):
            dy_spacing = spacing[1]
            dx_spacing = spacing[0]
        else:
            dy_spacing = dx_spacing = spacing

        # Use numpy gradient
        grad_y, grad_x = np.gradient(displacement_z, dy_spacing, dx_spacing)

        # Compute magnitude
        grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)

        logger.info(f"  Gradient magnitude range: [{np.nanmin(grad_magnitude):.3f}, {np.nanmax(grad_magnitude):.3f}]")

        return {
            'gradient_y': grad_y.astype(np.float32),
            'gradient_x': grad_x.astype(np.float32),
            'gradient_magnitude': grad_magnitude.astype(np.float32)
        }
