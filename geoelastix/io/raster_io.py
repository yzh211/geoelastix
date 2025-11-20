"""Raster I/O operations for GeoTIFF and ASC formats."""

import numpy as np
import logging
from pathlib import Path
from osgeo import gdal, osr
import itk

from .nodata_handler import NoDataHandler
from .crs_manager import CRSManager

logger = logging.getLogger("geoelastix.io")

# Enable GDAL exceptions
gdal.UseExceptions()


class RasterIO:
    """
    Read and write geospatial raster data in GeoTIFF and ASC formats.

    Handles GDAL-compliant no-data values and CRS information.
    """

    @staticmethod
    def read_raster(file_path, band=1):
        """
        Read raster file and return array with metadata.

        Parameters
        ----------
        file_path : str or Path
            Path to raster file (GeoTIFF or ASC)
        band : int, optional
            Band number to read (1-indexed). Default: 1

        Returns
        -------
        dict
            Dictionary containing:
            - 'array': numpy array of raster data
            - 'mask': binary mask (1=valid, 0=no-data)
            - 'nodata': no-data value
            - 'crs': CRS in WKT format
            - 'geotransform': GDAL geotransform tuple
            - 'shape': (height, width)
            - 'dtype': data type
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Raster file not found: {file_path}")

        logger.info(f"Reading raster: {file_path}")

        # Open dataset
        dataset = gdal.Open(str(file_path), gdal.GA_ReadOnly)
        if dataset is None:
            raise IOError(f"Failed to open raster file: {file_path}")

        # Get raster band
        raster_band = dataset.GetRasterBand(band)

        # Read array
        array = raster_band.ReadAsArray()

        if array is None:
            raise IOError(f"Failed to read data from: {file_path}")

        # Get no-data value
        nodata = NoDataHandler.get_nodata_value(dataset)

        if nodata is None:
            logger.warning(
                f"No-data value not defined in {file_path.name}. "
                "Attempting auto-detection."
            )
            nodata = NoDataHandler.auto_detect_nodata(array)

        # Create mask
        mask = NoDataHandler.create_mask(array, nodata)

        # Get CRS
        crs_wkt = CRSManager.get_crs_from_dataset(dataset)

        # Get geotransform
        geotransform = CRSManager.get_geotransform(dataset)

        # Get metadata
        width = dataset.RasterXSize
        height = dataset.RasterYSize

        # Log information
        valid_percent = NoDataHandler.get_valid_data_percentage(mask)
        logger.info(
            f"  Shape: {height} x {width}\n"
            f"  Data type: {array.dtype}\n"
            f"  No-data value: {nodata}\n"
            f"  Valid data: {valid_percent:.1f}%"
        )

        if crs_wkt:
            crs_info = CRSManager.get_crs_info(crs_wkt)
            logger.info(
                f"  CRS: {crs_info['name']} (EPSG:{crs_info['code']})"
            )

        # Close dataset
        dataset = None

        return {
            'array': array,
            'mask': mask,
            'nodata': nodata,
            'crs': crs_wkt,
            'geotransform': geotransform,
            'shape': (height, width),
            'dtype': array.dtype
        }

    @staticmethod
    def write_geotiff(file_path, array, geotransform, crs_wkt, nodata_value=-9999,
                      compression='LZW', dtype=None):
        """
        Write array to GeoTIFF file.

        Parameters
        ----------
        file_path : str or Path
            Output file path
        array : numpy.ndarray
            Data array to write
        geotransform : tuple
            GDAL geotransform tuple
        crs_wkt : str
            CRS in WKT format
        nodata_value : float, optional
            No-data value. Default: -9999
        compression : str, optional
            Compression method ('LZW', 'DEFLATE', 'NONE'). Default: 'LZW'
        dtype : gdal data type, optional
            Output data type. If None, infers from array dtype.
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Writing GeoTIFF: {file_path}")

        # Determine GDAL data type
        if dtype is None:
            dtype = RasterIO._numpy_to_gdal_dtype(array.dtype)

        # Get dimensions
        if array.ndim == 2:
            height, width = array.shape
            bands = 1
        elif array.ndim == 3:
            bands, height, width = array.shape
        else:
            raise ValueError(f"Unsupported array dimensions: {array.ndim}")

        # Create driver
        driver = gdal.GetDriverByName('GTiff')

        # Create dataset with compression
        creation_options = []
        if compression != 'NONE':
            creation_options.append(f'COMPRESS={compression}')

        dataset = driver.Create(
            str(file_path),
            width,
            height,
            bands,
            dtype,
            options=creation_options
        )

        if dataset is None:
            raise IOError(f"Failed to create GeoTIFF: {file_path}")

        # Write data
        if bands == 1:
            band = dataset.GetRasterBand(1)
            band.WriteArray(array)
            band.SetNoDataValue(nodata_value)
        else:
            for i in range(bands):
                band = dataset.GetRasterBand(i + 1)
                band.WriteArray(array[i])
                band.SetNoDataValue(nodata_value)

        # Set geotransform
        dataset.SetGeoTransform(geotransform)

        # Set projection
        if crs_wkt:
            dataset.SetProjection(crs_wkt)

        # Flush to disk
        dataset.FlushCache()
        dataset = None

        logger.info(f"  Successfully wrote {file_path.name}")

    @staticmethod
    def write_asc(file_path, array, geotransform, nodata_value=-9999):
        """
        Write array to ASCII Grid (ASC) file.

        Parameters
        ----------
        file_path : str or Path
            Output file path
        array : numpy.ndarray
            Data array to write
        geotransform : tuple
            GDAL geotransform tuple
        nodata_value : float, optional
            No-data value. Default: -9999
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Writing ASC file: {file_path}")

        height, width = array.shape
        xllcorner = geotransform[0]
        yllcorner = geotransform[3] + height * geotransform[5]
        cellsize = abs(geotransform[1])

        # Write header
        header = (
            f"ncols         {width}\n"
            f"nrows         {height}\n"
            f"xllcorner     {xllcorner:.6f}\n"
            f"yllcorner     {yllcorner:.6f}\n"
            f"cellsize      {cellsize:.6f}\n"
            f"NODATA_value  {nodata_value}\n"
        )

        # Write file
        with open(file_path, 'w') as f:
            f.write(header)
            np.savetxt(f, array, fmt='%.6f')

        logger.info(f"  Successfully wrote {file_path.name}")

    @staticmethod
    def array_to_itk_image(array, spacing=None, origin=None):
        """
        Convert numpy array to ITK image.

        Parameters
        ----------
        array : numpy.ndarray
            Input array
        spacing : tuple, optional
            Pixel spacing (pixel_width, pixel_height)
        origin : tuple, optional
            Image origin (x, y)

        Returns
        -------
        itk.Image
            ITK image
        """
        # Convert to float32 for ITK-Elastix
        array_float = array.astype(np.float32)

        # Create ITK image
        itk_image = itk.image_from_array(array_float)

        # Set spacing if provided
        if spacing is not None:
            itk_image.SetSpacing(spacing)

        # Set origin if provided
        if origin is not None:
            itk_image.SetOrigin(origin)

        return itk_image

    @staticmethod
    def itk_image_to_array(itk_image):
        """
        Convert ITK image to numpy array.

        Parameters
        ----------
        itk_image : itk.Image
            ITK image

        Returns
        -------
        numpy.ndarray
            Numpy array
        """
        return itk.array_from_image(itk_image)

    @staticmethod
    def get_raster_info(file_path):
        """
        Get raster metadata without reading the full array.

        Parameters
        ----------
        file_path : str or Path
            Path to raster file

        Returns
        -------
        dict
            Dictionary with metadata
        """
        dataset = gdal.Open(str(file_path), gdal.GA_ReadOnly)
        if dataset is None:
            raise IOError(f"Failed to open raster file: {file_path}")

        band = dataset.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        crs_wkt = CRSManager.get_crs_from_dataset(dataset)
        geotransform = dataset.GetGeoTransform()
        crs_info = CRSManager.get_crs_info(crs_wkt) if crs_wkt else {}

        info = {
            'width': dataset.RasterXSize,
            'height': dataset.RasterYSize,
            'bands': dataset.RasterCount,
            'dtype': gdal.GetDataTypeName(band.DataType),
            'nodata': nodata,
            'crs': crs_wkt,
            'crs_info': crs_info,
            'geotransform': geotransform,
            'pixel_size': CRSManager.get_pixel_size(dataset)
        }

        dataset = None
        return info

    @staticmethod
    def _numpy_to_gdal_dtype(numpy_dtype):
        """
        Convert numpy dtype to GDAL data type.

        Parameters
        ----------
        numpy_dtype : numpy.dtype
            Numpy data type

        Returns
        -------
        int
            GDAL data type constant
        """
        dtype_mapping = {
            np.uint8: gdal.GDT_Byte,
            np.int16: gdal.GDT_Int16,
            np.uint16: gdal.GDT_UInt16,
            np.int32: gdal.GDT_Int32,
            np.uint32: gdal.GDT_UInt32,
            np.float32: gdal.GDT_Float32,
            np.float64: gdal.GDT_Float64,
        }

        numpy_dtype = np.dtype(numpy_dtype)

        if numpy_dtype.type in dtype_mapping:
            return dtype_mapping[numpy_dtype.type]
        else:
            # Default to Float32
            logger.warning(
                f"Unsupported dtype {numpy_dtype}, defaulting to Float32"
            )
            return gdal.GDT_Float32
