"""Horizontal displacement calculation from deformation field."""

import numpy as np
import logging
import itk
from pathlib import Path

logger = logging.getLogger("geoelastix.displacement")


class HorizontalDisplacement:
    """
    Calculate horizontal displacement (X, Y) from elastix deformation field.

    Extracts the deformation field from elastix transformation parameters
    and computes displacement in X (East-West) and Y (North-South) directions.
    """

    @staticmethod
    def compute_from_transform(fixed_image, transform_parameters, spacing=None):
        """
        Compute horizontal displacement from transformation parameters.

        Parameters
        ----------
        fixed_image : itk.Image
            Fixed (reference) image used as template for output
        transform_parameters : itk.ParameterObject
            Elastix transformation parameters
        spacing : tuple, optional
            Pixel spacing (pixel_width, pixel_height) in map units.
            If None, uses spacing from fixed_image.

        Returns
        -------
        dict
            Dictionary containing:
            - 'displacement_x': numpy array of X displacement (East-West)
            - 'displacement_y': numpy array of Y displacement (North-South)
            - 'spacing': pixel spacing used
        """
        logger.info("Computing horizontal displacement from deformation field...")

        # Get image dimensions and spacing
        fixed_array = itk.array_from_image(fixed_image)
        image_shape = fixed_array.shape

        if spacing is None:
            spacing = fixed_image.GetSpacing()
            logger.info(f"  Using image spacing: {spacing}")
        else:
            logger.info(f"  Using provided spacing: {spacing}")

        # Use ITK's transformix_deformation_field (matches reference code)
        logger.info("  Generating deformation field using transformix...")

        try:
            # Generate deformation field using ITK's built-in function
            # This is the correct approach matching the reference ASC2_rectification.py
            deformation_field = itk.transformix_deformation_field(
                fixed_image,
                transform_parameters
            )

            # Convert to numpy array
            deformation_array = itk.array_from_image(deformation_field)

            # Extract X and Y components
            # ITK convention: deformation_field[:, :, 0] is X, [:, :, 1] is Y
            displacement_x = deformation_array[:, :, 0].astype(np.float32)
            displacement_y = deformation_array[:, :, 1].astype(np.float32)

            logger.info(f"  Displacement X range: [{np.min(displacement_x):.3f}, {np.max(displacement_x):.3f}]")
            logger.info(f"  Displacement Y range: [{np.min(displacement_y):.3f}, {np.max(displacement_y):.3f}]")

            return {
                'displacement_x': displacement_x,
                'displacement_y': displacement_y,
                'spacing': spacing
            }

        except Exception as e:
            logger.error(f"Failed to compute displacement: {e}")
            raise

    @staticmethod
    def apply_mask(displacement_x, displacement_y, mask):
        """
        Apply mask to displacement fields.

        Parameters
        ----------
        displacement_x : numpy.ndarray
            X displacement field
        displacement_y : numpy.ndarray
            Y displacement field
        mask : numpy.ndarray
            Binary mask (1=valid, 0=no-data)

        Returns
        -------
        tuple
            (masked_disp_x, masked_disp_y)
        """
        masked_x = displacement_x.copy()
        masked_y = displacement_y.copy()

        masked_x[mask == 0] = np.nan
        masked_y[mask == 0] = np.nan

        return masked_x, masked_y

    @staticmethod
    def get_statistics(displacement_x, displacement_y, mask=None):
        """
        Compute statistics for displacement fields.

        Parameters
        ----------
        displacement_x : numpy.ndarray
            X displacement field
        displacement_y : numpy.ndarray
            Y displacement field
        mask : numpy.ndarray, optional
            Binary mask for valid regions

        Returns
        -------
        dict
            Statistics dictionary
        """
        if mask is not None:
            valid_mask = mask > 0
            dx = displacement_x[valid_mask]
            dy = displacement_y[valid_mask]
        else:
            dx = displacement_x.flatten()
            dy = displacement_y.flatten()

        # Remove NaN values
        dx = dx[~np.isnan(dx)]
        dy = dy[~np.isnan(dy)]

        magnitude = np.sqrt(dx**2 + dy**2)

        stats = {
            'x_mean': float(np.mean(dx)),
            'x_std': float(np.std(dx)),
            'x_min': float(np.min(dx)),
            'x_max': float(np.max(dx)),
            'y_mean': float(np.mean(dy)),
            'y_std': float(np.std(dy)),
            'y_min': float(np.min(dy)),
            'y_max': float(np.max(dy)),
            'magnitude_mean': float(np.mean(magnitude)),
            'magnitude_std': float(np.std(magnitude)),
            'magnitude_min': float(np.min(magnitude)),
            'magnitude_max': float(np.max(magnitude)),
            'n_valid_pixels': len(dx)
        }

        return stats
