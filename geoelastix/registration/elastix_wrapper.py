"""ITK-Elastix registration wrapper."""

import logging
import itk
import numpy as np
from pathlib import Path

logger = logging.getLogger("geoelastix.registration")


class ElastixWrapper:
    """
    Wrapper for ITK-Elastix registration functionality.

    Provides a simplified interface to ITK-Elastix registration with
    proper logging and error handling.
    """

    def __init__(self, parameter_object):
        """
        Initialize elastix wrapper.

        Parameters
        ----------
        parameter_object : itk.ParameterObject
            ITK-Elastix parameter object
        """
        self.parameter_object = parameter_object
        logger.info("Initialized ElastixWrapper")

    def register(self, fixed_image, moving_image, fixed_mask=None,
                 moving_mask=None, log_to_console=False,
                 use_transformix_workaround=False):
        """
        Perform image registration using elastix.

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
        use_transformix_workaround : bool, optional
            Apply transformix_filter after registration as workaround for
            potential pixel buffer issues. This doubles registration time
            but may be needed for some datasets. Default: False

        Returns
        -------
        tuple
            (registered_image, transform_parameters)
            - registered_image: itk.Image, registered moving image
            - transform_parameters: itk.ParameterObject, transformation parameters
        """
        logger.info("Starting elastix registration...")

        # Validate inputs
        if moving_image is None:
            raise ValueError("moving_image is None - cannot perform registration")
        if fixed_image is None:
            raise ValueError("fixed_image is None - cannot perform registration")

        # Log image information (get size from ITK image, no conversion needed)
        fixed_size = fixed_image.GetLargestPossibleRegion().GetSize()
        moving_size = moving_image.GetLargestPossibleRegion().GetSize()

        logger.info(f"  Fixed image shape: ({fixed_size[1]}, {fixed_size[0]})")
        logger.info(f"  Moving image shape: ({moving_size[1]}, {moving_size[0]})")

        if fixed_mask is not None:
            logger.info(f"  Fixed mask: provided")

        if moving_mask is not None:
            logger.info(f"  Moving mask: provided")

        try:
            # Perform registration
            if fixed_mask is not None and moving_mask is not None:
                result_image, transform_parameters = itk.elastix_registration_method(
                    fixed_image,
                    moving_image,
                    parameter_object=self.parameter_object,
                    fixed_mask=fixed_mask,
                    moving_mask=moving_mask,
                    log_to_console=log_to_console
                )
            elif fixed_mask is not None:
                result_image, transform_parameters = itk.elastix_registration_method(
                    fixed_image,
                    moving_image,
                    parameter_object=self.parameter_object,
                    fixed_mask=fixed_mask,
                    log_to_console=log_to_console
                )
            else:
                result_image, transform_parameters = itk.elastix_registration_method(
                    fixed_image,
                    moving_image,
                    parameter_object=self.parameter_object,
                    log_to_console=log_to_console
                )

            logger.info("Registration completed successfully")

            # Check if result_image has valid pixel data
            # When WriteResultImage="false", elastix returns an image object but
            # with no pixel buffer, so we must use transformix to generate it
            result_has_data = False
            if result_image is not None:
                try:
                    test_array = itk.array_from_image(result_image)
                    result_has_data = (test_array is not None)
                except:
                    result_has_data = False

            if not result_has_data or use_transformix_workaround:
                if not result_has_data:
                    logger.info("Result image has no pixel data, applying transform with transformix...")
                else:
                    logger.info("Applying transformix workaround for pixel buffer...")

                registered_image = itk.transformix_filter(
                    moving_image,
                    transform_parameters,
                    log_to_console=log_to_console
                )
                if registered_image is None:
                    raise ValueError("transformix returned None for registered image")

                # Verify the transformix result has data
                test_array = itk.array_from_image(registered_image)
                if test_array is None:
                    raise ValueError("transformix result has no pixel data")

                logger.info("✓ Registered image generated with transformix")
            else:
                registered_image = result_image
                logger.info("✓ Using registered image from elastix")

            return registered_image, transform_parameters

        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            raise

    def apply_transform(self, moving_image, transform_parameters, log_to_console=False):
        """
        Apply existing transformation to an image using transformix.

        Parameters
        ----------
        moving_image : itk.Image
            Image to transform
        transform_parameters : itk.ParameterObject
            Transformation parameters from registration
        log_to_console : bool, optional
            Enable transformix console logging. Default: False

        Returns
        -------
        itk.Image
            Transformed image
        """
        logger.info("Applying transformation with transformix...")

        try:
            transformed_image = itk.transformix_filter(
                moving_image,
                transform_parameters,
                log_to_console=log_to_console
            )

            logger.info("Transformation applied successfully")
            return transformed_image

        except Exception as e:
            logger.error(f"Transform application failed: {str(e)}")
            raise

    def get_transform_parameters(self):
        """
        Get current parameter object.

        Returns
        -------
        itk.ParameterObject
            Parameter object
        """
        return self.parameter_object

    def save_transform_parameters(self, transform_parameters, output_path):
        """
        Save transformation parameters to file.

        Parameters
        ----------
        transform_parameters : itk.ParameterObject
            Transformation parameters
        output_path : str or Path
            Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        transform_parameters.WriteParameterFile(
            transform_parameters.GetParameterMap(0),
            str(output_path)
        )

        logger.info(f"Saved transform parameters: {output_path}")

    @staticmethod
    def read_transform_parameters(file_path):
        """
        Read transformation parameters from file.

        Parameters
        ----------
        file_path : str or Path
            Path to parameter file

        Returns
        -------
        itk.ParameterObject
            Loaded transformation parameters
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Parameter file not found: {file_path}")

        parameter_object = itk.ParameterObject.New()
        parameter_object.AddParameterFile(str(file_path))

        logger.info(f"Loaded transform parameters: {file_path}")
        return parameter_object

    @staticmethod
    def extract_metric_value(transform_parameters, index=0):
        """
        Extract final metric value from transform parameters.

        Parameters
        ----------
        transform_parameters : itk.ParameterObject
            Transformation parameters
        index : int, optional
            Parameter map index. Default: 0

        Returns
        -------
        float or None
            Final metric value, or None if not available
        """
        try:
            param_map = transform_parameters.GetParameterMap(index)

            # Try to get final metric value
            # This is stored differently depending on the metric
            if 'FinalMetricValue' in param_map:
                value_str = param_map['FinalMetricValue'][0]
                return float(value_str)

            return None

        except Exception as e:
            logger.warning(f"Could not extract metric value: {e}")
            return None

    @staticmethod
    def get_transform_type(transform_parameters, index=0):
        """
        Get transformation type from parameters.

        Parameters
        ----------
        transform_parameters : itk.ParameterObject
            Transformation parameters
        index : int, optional
            Parameter map index. Default: 0

        Returns
        -------
        str
            Transform type name
        """
        param_map = transform_parameters.GetParameterMap(index)
        transform_type = param_map.get('Transform', ['Unknown'])[0]
        return transform_type
