"""Coordinate Reference System (CRS) detection and management."""

import logging
from osgeo import gdal, osr
import pyproj

logger = logging.getLogger("geoelastix.io")


class CRSManager:
    """
    Manage Coordinate Reference Systems for geospatial data.

    Provides CRS detection, validation, and comparison functionality.
    """

    @staticmethod
    def get_crs_from_dataset(dataset):
        """
        Extract CRS from GDAL dataset.

        Parameters
        ----------
        dataset : gdal.Dataset
            GDAL dataset

        Returns
        -------
        str or None
            WKT (Well-Known Text) representation of CRS, or None if not defined
        """
        projection = dataset.GetProjection()

        if projection:
            return projection
        else:
            logger.warning("No CRS information found in dataset")
            return None

    @staticmethod
    def get_crs_info(wkt):
        """
        Get human-readable CRS information from WKT.

        Parameters
        ----------
        wkt : str
            WKT representation of CRS

        Returns
        -------
        dict
            Dictionary with CRS information (name, authority, code, units)
        """
        if wkt is None or wkt == "":
            return {
                "name": "Unknown",
                "authority": None,
                "code": None,
                "units": "unknown"
            }

        srs = osr.SpatialReference()
        srs.ImportFromWkt(wkt)

        info = {
            "name": srs.GetName() if srs.GetName() else "Unknown",
            "authority": srs.GetAuthorityName(None),
            "code": srs.GetAuthorityCode(None),
            "units": srs.GetLinearUnitsName() if srs.IsProjected() else "degrees"
        }

        return info

    @staticmethod
    def get_epsg_code(wkt):
        """
        Extract EPSG code from WKT.

        Parameters
        ----------
        wkt : str
            WKT representation of CRS

        Returns
        -------
        int or None
            EPSG code, or None if not available
        """
        if wkt is None or wkt == "":
            return None

        srs = osr.SpatialReference()
        srs.ImportFromWkt(wkt)

        authority_code = srs.GetAuthorityCode(None)
        if authority_code:
            try:
                return int(authority_code)
            except (ValueError, TypeError):
                return None

        return None

    @staticmethod
    def compare_crs(wkt1, wkt2):
        """
        Compare two CRS for compatibility.

        Parameters
        ----------
        wkt1 : str
            First CRS in WKT format
        wkt2 : str
            Second CRS in WKT format

        Returns
        -------
        bool
            True if CRS are compatible, False otherwise
        """
        # Handle None/empty cases
        if (wkt1 is None or wkt1 == "") and (wkt2 is None or wkt2 == ""):
            logger.warning("Both CRS are undefined - assuming compatible")
            return True

        if (wkt1 is None or wkt1 == "") or (wkt2 is None or wkt2 == ""):
            logger.warning("One CRS is undefined - assuming compatible but this may cause issues")
            return True

        # Create spatial reference objects
        srs1 = osr.SpatialReference()
        srs2 = osr.SpatialReference()

        try:
            srs1.ImportFromWkt(wkt1)
            srs2.ImportFromWkt(wkt2)
        except Exception as e:
            logger.error(f"Failed to parse CRS: {e}")
            return False

        # Compare using IsSame
        are_same = srs1.IsSame(srs2)

        if not are_same:
            # Get info for logging
            info1 = CRSManager.get_crs_info(wkt1)
            info2 = CRSManager.get_crs_info(wkt2)
            logger.warning(
                f"CRS mismatch detected:\n"
                f"  CRS 1: {info1['name']} (EPSG:{info1['code']})\n"
                f"  CRS 2: {info2['name']} (EPSG:{info2['code']})"
            )

        return are_same

    @staticmethod
    def validate_crs_pair(dataset1, dataset2, raise_on_mismatch=False):
        """
        Validate that two datasets have compatible CRS.

        Parameters
        ----------
        dataset1 : gdal.Dataset
            First dataset
        dataset2 : gdal.Dataset
            Second dataset
        raise_on_mismatch : bool, optional
            If True, raise ValueError on mismatch. Default: False

        Returns
        -------
        bool
            True if CRS are compatible

        Raises
        ------
        ValueError
            If CRS mismatch and raise_on_mismatch=True
        """
        wkt1 = CRSManager.get_crs_from_dataset(dataset1)
        wkt2 = CRSManager.get_crs_from_dataset(dataset2)

        are_compatible = CRSManager.compare_crs(wkt1, wkt2)

        if not are_compatible and raise_on_mismatch:
            info1 = CRSManager.get_crs_info(wkt1)
            info2 = CRSManager.get_crs_info(wkt2)
            raise ValueError(
                f"CRS mismatch:\n"
                f"  Dataset 1: {info1['name']} (EPSG:{info1['code']})\n"
                f"  Dataset 2: {info2['name']} (EPSG:{info2['code']})"
            )

        return are_compatible

    @staticmethod
    def get_geotransform(dataset):
        """
        Get geotransform from dataset.

        Parameters
        ----------
        dataset : gdal.Dataset
            GDAL dataset

        Returns
        -------
        tuple
            Geotransform tuple (origin_x, pixel_width, rotation_x,
                               origin_y, rotation_y, pixel_height)
        """
        return dataset.GetGeoTransform()

    @staticmethod
    def get_pixel_size(dataset):
        """
        Get pixel size from dataset.

        Parameters
        ----------
        dataset : gdal.Dataset
            GDAL dataset

        Returns
        -------
        tuple
            (pixel_width, pixel_height) in map units
        """
        gt = dataset.GetGeoTransform()
        pixel_width = abs(gt[1])
        pixel_height = abs(gt[5])
        return pixel_width, pixel_height

    @staticmethod
    def create_crs_from_epsg(epsg_code):
        """
        Create WKT CRS from EPSG code.

        Parameters
        ----------
        epsg_code : int
            EPSG code

        Returns
        -------
        str
            WKT representation of CRS
        """
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg_code)
        return srs.ExportToWkt()
