"""Two-pass registration for improved accuracy."""

import logging
from .elastix_wrapper import ElastixWrapper

logger = logging.getLogger("geoelastix.registration")


class TwoPassRegistration:
    """
    Implement two-pass registration strategy for improved accuracy.

    Performs registration twice using the same parameters, with the second
    pass using the results of the first pass as initialization. This approach
    has been shown to improve registration accuracy for landslide monitoring.
    """

    def __init__(self, parameter_object):
        """
        Initialize two-pass registration.

        Parameters
        ----------
        parameter_object : itk.ParameterObject
            ITK-Elastix parameter object for registration
        """
        self.parameter_object = parameter_object
        logger.info("Initialized TwoPassRegistration")

    def register(self, fixed_image, moving_image, fixed_mask=None,
                 moving_mask=None, log_to_console=False):
        """
        Perform two-pass registration.

        Parameters
        ----------
        fixed_image : itk.Image
            Fixed (reference) image
        moving_image : itk.Image
            Moving image to be registered
        fixed_mask : itk.Image, optional
            Binary mask for fixed image (uint8)
        moving_mask : itk.Image, optional
            Binary mask for moving image (uint8)
        log_to_console : bool, optional
            Enable elastix console logging. Default: False

        Returns
        -------
        dict
            Dictionary containing:
            - 'registered_image': final registered image
            - 'transform_parameters': final transformation parameters
            - 'pass1_image': result from first pass
            - 'pass1_parameters': parameters from first pass
            - 'pass2_image': result from second pass
            - 'pass2_parameters': parameters from second pass
        """
        logger.info("="*60)
        logger.info("Starting two-pass registration")
        logger.info("="*60)

        # First pass
        logger.info("")
        logger.info("PASS 1: Initial registration")
        logger.info("-"*60)

        wrapper1 = ElastixWrapper(self.parameter_object)
        pass1_image, pass1_params = wrapper1.register(
            fixed_image,
            moving_image,
            fixed_mask=fixed_mask,
            moving_mask=moving_mask,
            log_to_console=log_to_console
        )

        logger.info("Pass 1 completed")

        # Second pass - use first pass result as moving image
        logger.info("")
        logger.info("PASS 2: Refinement registration")
        logger.info("-"*60)

        wrapper2 = ElastixWrapper(self.parameter_object)
        pass2_image, pass2_params = wrapper2.register(
            fixed_image,
            pass1_image,  # Use result from first pass
            fixed_mask=fixed_mask,
            moving_mask=moving_mask,
            log_to_console=log_to_console
        )

        logger.info("Pass 2 completed")

        logger.info("")
        logger.info("="*60)
        logger.info("Two-pass registration completed successfully")
        logger.info("="*60)

        return {
            'registered_image': pass2_image,
            'transform_parameters': pass2_params,
            'pass1_image': pass1_image,
            'pass1_parameters': pass1_params,
            'pass2_image': pass2_image,
            'pass2_parameters': pass2_params,
        }

    def register_with_initial_transform(self, fixed_image, moving_image,
                                       initial_transform, fixed_mask=None,
                                       moving_mask=None, log_to_console=False):
        """
        Perform registration with an initial transformation.

        This can be used to further refine an existing registration.

        Parameters
        ----------
        fixed_image : itk.Image
            Fixed (reference) image
        moving_image : itk.Image
            Moving image to be registered
        initial_transform : itk.ParameterObject
            Initial transformation parameters
        fixed_mask : itk.Image, optional
            Binary mask for fixed image
        moving_mask : itk.Image, optional
            Binary mask for moving image
        log_to_console : bool, optional
            Enable console logging. Default: False

        Returns
        -------
        dict
            Registration results dictionary
        """
        logger.info("Registration with initial transform")

        # First apply initial transform
        wrapper = ElastixWrapper(self.parameter_object)
        transformed_image = wrapper.apply_transform(
            moving_image,
            initial_transform,
            log_to_console=log_to_console
        )

        # Then perform two-pass registration
        return self.register(
            fixed_image,
            transformed_image,
            fixed_mask=fixed_mask,
            moving_mask=moving_mask,
            log_to_console=log_to_console
        )

    @staticmethod
    def save_results(results, output_dir):
        """
        Save all registration results to directory.

        Parameters
        ----------
        results : dict
            Results dictionary from register()
        output_dir : Path
            Output directory
        """
        from pathlib import Path
        import itk

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save images
        itk.imwrite(
            results['registered_image'],
            str(output_dir / 'registered_final.mhd')
        )
        itk.imwrite(
            results['pass1_image'],
            str(output_dir / 'registered_pass1.mhd')
        )

        # Save parameters
        wrapper = ElastixWrapper(None)
        wrapper.save_transform_parameters(
            results['pass1_parameters'],
            output_dir / 'TransformParameters_pass1.txt'
        )
        wrapper.save_transform_parameters(
            results['pass2_parameters'],
            output_dir / 'TransformParameters_pass2.txt'
        )

        logger.info(f"Saved registration results to: {output_dir}")
