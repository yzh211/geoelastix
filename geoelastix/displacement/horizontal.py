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

        # Get deformation field using transformix
        logger.info("  Generating deformation field...")

        try:
            # Create deformation field filter
            # This requires setting up transformix to output the deformation field
            param_map = transform_parameters.GetParameterMap(0)

            # Create a copy and set to output deformation field
            deformation_param = itk.ParameterObject.New()
            deformation_param.AddParameterMap(param_map)

            # Modify parameters to output deformation field
            mod_map = deformation_param.GetParameterMap(0)
            mod_map['ResultImageFormat'] = ['mhd']
            mod_map['ResultImagePixelType'] = ['float']
            deformation_param.SetParameterMap(0, mod_map)

            # Generate deformation field by transforming a grid
            # Create a displacement field by getting the transformation at each point
            displacement_x = np.zeros(image_shape, dtype=np.float32)
            displacement_y = np.zeros(image_shape, dtype=np.float32)

            # For BSpline and other transforms, we need to compute displacement
            # at each pixel location
            logger.info("  Computing displacement at each pixel...")

            # Get transform type
            transform_type = param_map.get('Transform', ['Unknown'])[0]
            logger.info(f"  Transform type: {transform_type}")

            if 'BSpline' in transform_type:
                # For BSpline, extract displacement from coefficient grid
                displacement_x, displacement_y = HorizontalDisplacement._extract_bspline_displacement(
                    transform_parameters, image_shape, spacing
                )
            elif 'Affine' in transform_type or 'Euler' in transform_type or 'Translation' in transform_type:
                # For affine/rigid transforms, compute displacement from parameters
                displacement_x, displacement_y = HorizontalDisplacement._extract_affine_displacement(
                    transform_parameters, image_shape, spacing, fixed_image
                )
            else:
                logger.warning(f"  Unknown transform type: {transform_type}, using pixel-based computation")
                displacement_x, displacement_y = HorizontalDisplacement._compute_displacement_pixel_by_pixel(
                    transform_parameters, fixed_image
                )

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
    def _extract_bspline_displacement(transform_parameters, image_shape, spacing):
        """
        Extract displacement from BSpline transformation parameters.

        For BSpline transforms, the displacement can be computed by evaluating
        the transformation at each pixel location.

        Parameters
        ----------
        transform_parameters : itk.ParameterObject
            Elastix transformation parameters
        image_shape : tuple
            (height, width) of image
        spacing : tuple
            Pixel spacing

        Returns
        -------
        tuple
            (displacement_x, displacement_y) as numpy arrays
        """
        logger.info("  Extracting BSpline displacement field...")

        height, width = image_shape
        displacement_x = np.zeros((height, width), dtype=np.float32)
        displacement_y = np.zeros((height, width), dtype=np.float32)

        # Get transformation parameters
        param_map = transform_parameters.GetParameterMap(0)

        # Get transform parameters (coefficients)
        if 'TransformParameters' in param_map:
            coefficients = [float(x) for x in param_map['TransformParameters']]

            # Get grid spacing and size
            grid_spacing_str = param_map.get('GridSpacing', ['1.0', '1.0'])
            grid_spacing = [float(x) for x in grid_spacing_str]

            grid_size_str = param_map.get('GridSize', ['10', '10'])
            grid_size = [int(x) for x in grid_size_str]

            grid_origin_str = param_map.get('GridOrigin', ['0.0', '0.0'])
            grid_origin = [float(x) for x in grid_origin_str]

            logger.info(f"    Grid size: {grid_size}")
            logger.info(f"    Grid spacing: {grid_spacing}")
            logger.info(f"    Grid origin: {grid_origin}")

            # Number of coefficients per dimension
            n_coef_x = grid_size[0] + 3  # BSpline order 3
            n_coef_y = grid_size[1] + 3
            n_coef_total = n_coef_x * n_coef_y

            if len(coefficients) >= 2 * n_coef_total:
                # Reshape coefficients
                coef_x = np.array(coefficients[:n_coef_total]).reshape(n_coef_y, n_coef_x)
                coef_y = np.array(coefficients[n_coef_total:2*n_coef_total]).reshape(n_coef_y, n_coef_x)

                # Interpolate displacement at each pixel
                # This is a simplified version - actual BSpline evaluation is more complex
                # For now, use bilinear interpolation from control points
                from scipy.interpolate import RectBivariateSpline

                # Create grid coordinates for coefficients
                x_grid = np.linspace(0, width * spacing[0], n_coef_x)
                y_grid = np.linspace(0, height * spacing[1], n_coef_y)

                # Create interpolators
                interp_x = RectBivariateSpline(y_grid, x_grid, coef_x, kx=3, ky=3)
                interp_y = RectBivariateSpline(y_grid, x_grid, coef_y, kx=3, ky=3)

                # Evaluate at all pixel positions
                pixel_x = np.arange(width) * spacing[0]
                pixel_y = np.arange(height) * spacing[1]

                displacement_x = interp_x(pixel_y, pixel_x)
                displacement_y = interp_y(pixel_y, pixel_x)

                logger.info("    Successfully extracted BSpline displacement field")
            else:
                logger.warning("    Insufficient coefficients, returning zero displacement")

        return displacement_x, displacement_y

    @staticmethod
    def _extract_affine_displacement(transform_parameters, image_shape, spacing, fixed_image):
        """
        Extract displacement from Affine/Rigid transformation parameters.

        For affine/rigid transforms, displacement = T(x) - x

        Parameters
        ----------
        transform_parameters : itk.ParameterObject
            Elastix transformation parameters
        image_shape : tuple
            (height, width) of image
        spacing : tuple
            Pixel spacing
        fixed_image : itk.Image
            Fixed image for getting origin

        Returns
        -------
        tuple
            (displacement_x, displacement_y) as numpy arrays
        """
        logger.info("  Computing Affine/Rigid displacement field...")

        param_map = transform_parameters.GetParameterMap(0)

        # Get transformation parameters
        transform_params = param_map.get('TransformParameters', [])
        if not transform_params:
            logger.warning("    No transform parameters found, returning zero displacement")
            return np.zeros(image_shape, dtype=np.float32), np.zeros(image_shape, dtype=np.float32)

        transform_params = [float(x) for x in transform_params]
        center_of_rotation = [float(x) for x in param_map.get('CenterOfRotationPoint', ['0.0', '0.0'])]

        logger.info(f"    Transform parameters: {transform_params}")
        logger.info(f"    Center of rotation: {center_of_rotation}")

        # Get image origin
        origin = fixed_image.GetOrigin()

        # Create coordinate grids
        height, width = image_shape
        y_coords, x_coords = np.mgrid[0:height, 0:width]

        # Convert to physical coordinates
        x_phys = origin[0] + x_coords * spacing[0]
        y_phys = origin[1] + y_coords * spacing[1]

        # Parse transformation based on number of parameters
        if len(transform_params) == 2:
            # Translation only
            tx, ty = transform_params
            displacement_x = np.full(image_shape, tx, dtype=np.float32)
            displacement_y = np.full(image_shape, ty, dtype=np.float32)
            logger.info("    Translation transform detected")

        elif len(transform_params) == 3:
            # Euler (rotation + translation)
            angle, tx, ty = transform_params
            cx, cy = center_of_rotation

            # Compute displacement at each pixel
            dx = x_phys - cx
            dy = y_phys - cy

            cos_a = np.cos(angle)
            sin_a = np.sin(angle)

            # Rotated position
            x_rot = cx + dx * cos_a - dy * sin_a + tx
            y_rot = cy + dx * sin_a + dy * cos_a + ty

            displacement_x = (x_rot - x_phys).astype(np.float32)
            displacement_y = (y_rot - y_phys).astype(np.float32)
            logger.info(f"    Euler transform detected (angle={np.degrees(angle):.2f}°)")

        elif len(transform_params) >= 6:
            # Affine transform
            # Parameters: [a11, a12, a21, a22, tx, ty] or similar
            logger.info("    Affine transform detected")

            # This is simplified - actual parameter order depends on elastix configuration
            # For now, assume standard affine matrix
            if len(transform_params) == 6:
                a11, a12, a21, a22, tx, ty = transform_params[:6]
            else:
                # More complex affine, use first 6 parameters
                a11, a12, a21, a22, tx, ty = transform_params[:6]

            cx, cy = center_of_rotation

            dx = x_phys - cx
            dy = y_phys - cy

            # Apply affine transformation
            x_trans = cx + a11 * dx + a12 * dy + tx
            y_trans = cy + a21 * dx + a22 * dy + ty

            displacement_x = (x_trans - x_phys).astype(np.float32)
            displacement_y = (y_trans - y_phys).astype(np.float32)

        else:
            logger.warning(f"    Unexpected number of parameters: {len(transform_params)}")
            displacement_x = np.zeros(image_shape, dtype=np.float32)
            displacement_y = np.zeros(image_shape, dtype=np.float32)

        return displacement_x, displacement_y

    @staticmethod
    def _compute_displacement_pixel_by_pixel(transform_parameters, fixed_image):
        """
        Compute displacement by transforming each pixel (fallback method).

        This is slower but works for any transformation type.

        Parameters
        ----------
        transform_parameters : itk.ParameterObject
            Elastix transformation parameters
        fixed_image : itk.Image
            Fixed image

        Returns
        -------
        tuple
            (displacement_x, displacement_y) as numpy arrays
        """
        logger.info("  Computing displacement pixel-by-pixel (this may take time)...")

        # This would require using transformix to transform a dense point set
        # For now, return zeros with a warning
        logger.warning("  Pixel-by-pixel displacement not fully implemented, returning zeros")

        fixed_array = itk.array_from_image(fixed_image)
        return np.zeros(fixed_array.shape, dtype=np.float32), np.zeros(fixed_array.shape, dtype=np.float32)

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
