"""Quality metrics for registration validation."""

import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger("geoelastix.validation")


class QualityMetrics:
    """
    Compute quality metrics for registration validation.

    Provides RMSE, Mutual Information, Dice coefficient, and coverage analysis.
    """

    @staticmethod
    def compute_rmse(fixed_array, registered_array, mask=None):
        """
        Compute Root Mean Square Error between images.

        RMSE = sqrt(mean((fixed - registered)²))

        Parameters
        ----------
        fixed_array : numpy.ndarray
            Fixed (reference) image
        registered_array : numpy.ndarray
            Registered image
        mask : numpy.ndarray, optional
            Binary mask (1=valid, 0=no-data)

        Returns
        -------
        dict
            Dictionary with RMSE value and additional statistics
        """
        logger.info("Computing RMSE...")

        # Check shapes
        if fixed_array.shape != registered_array.shape:
            raise ValueError(
                f"Shape mismatch: fixed {fixed_array.shape} vs "
                f"registered {registered_array.shape}"
            )

        # Apply mask if provided
        if mask is not None:
            valid_mask = mask > 0
            fixed = fixed_array[valid_mask]
            registered = registered_array[valid_mask]
        else:
            fixed = fixed_array.flatten()
            registered = registered_array.flatten()

        # Remove NaN values
        valid_idx = ~(np.isnan(fixed) | np.isnan(registered))
        fixed = fixed[valid_idx]
        registered = registered[valid_idx]

        if len(fixed) == 0:
            logger.warning("No valid data for RMSE calculation")
            return {
                'rmse': np.nan,
                'mae': np.nan,
                'n_samples': 0
            }

        # Compute differences
        differences = fixed - registered

        # RMSE
        rmse = float(np.sqrt(np.mean(differences**2)))

        # MAE (Mean Absolute Error)
        mae = float(np.mean(np.abs(differences)))

        # Additional statistics
        max_error = float(np.max(np.abs(differences)))
        std_error = float(np.std(differences))

        logger.info(f"  RMSE: {rmse:.6f}")
        logger.info(f"  MAE: {mae:.6f}")
        logger.info(f"  Max error: {max_error:.6f}")

        return {
            'rmse': rmse,
            'mae': mae,
            'max_error': max_error,
            'std_error': std_error,
            'n_samples': len(fixed)
        }

    @staticmethod
    def compute_mutual_information(fixed_array, registered_array, bins=128, mask=None):
        """
        Compute Mutual Information between images.

        MI measures the statistical dependence between two images.
        Higher MI indicates better alignment.

        Parameters
        ----------
        fixed_array : numpy.ndarray
            Fixed image
        registered_array : numpy.ndarray
            Registered image
        bins : int, optional
            Number of histogram bins. Default: 128
        mask : numpy.ndarray, optional
            Binary mask

        Returns
        -------
        dict
            Dictionary with MI value and related metrics
        """
        logger.info("Computing Mutual Information...")

        # Apply mask if provided
        if mask is not None:
            valid_mask = mask > 0
            fixed = fixed_array[valid_mask]
            registered = registered_array[valid_mask]
        else:
            fixed = fixed_array.flatten()
            registered = registered_array.flatten()

        # Remove NaN values
        valid_idx = ~(np.isnan(fixed) | np.isnan(registered))
        fixed = fixed[valid_idx]
        registered = registered[valid_idx]

        if len(fixed) == 0:
            logger.warning("No valid data for MI calculation")
            return {
                'mutual_information': np.nan,
                'normalized_mi': np.nan,
                'n_samples': 0
            }

        # Compute 2D histogram
        hist_2d, x_edges, y_edges = np.histogram2d(
            fixed, registered, bins=bins
        )

        # Normalize to get joint probability
        pxy = hist_2d / float(np.sum(hist_2d))
        pxy = pxy + np.finfo(float).eps  # Avoid log(0)

        # Marginal probabilities
        px = np.sum(pxy, axis=1)
        py = np.sum(pxy, axis=0)

        # Marginal entropies
        px_py = px[:, None] * py[None, :]
        px_py = px_py + np.finfo(float).eps

        # Mutual Information
        nzs = pxy > 0
        mi = float(np.sum(pxy[nzs] * np.log(pxy[nzs] / px_py[nzs])))

        # Normalized Mutual Information
        # NMI = MI / sqrt(H(X) * H(Y))
        hx = -np.sum(px * np.log(px + np.finfo(float).eps))
        hy = -np.sum(py * np.log(py + np.finfo(float).eps))
        nmi = mi / np.sqrt(hx * hy) if (hx > 0 and hy > 0) else 0.0

        logger.info(f"  MI: {mi:.6f}")
        logger.info(f"  Normalized MI: {nmi:.6f}")

        return {
            'mutual_information': float(mi),
            'normalized_mi': float(nmi),
            'entropy_fixed': float(hx),
            'entropy_registered': float(hy),
            'n_samples': len(fixed)
        }

    @staticmethod
    def compute_dice_coefficient(mask1, mask2):
        """
        Compute Dice coefficient between two binary masks.

        Dice = 2 * |A ∩ B| / (|A| + |B|)

        Measures overlap between valid regions.

        Parameters
        ----------
        mask1 : numpy.ndarray
            First binary mask
        mask2 : numpy.ndarray
            Second binary mask

        Returns
        -------
        dict
            Dictionary with Dice coefficient and overlap statistics
        """
        logger.info("Computing Dice coefficient...")

        if mask1.shape != mask2.shape:
            raise ValueError("Masks must have the same shape")

        # Convert to boolean
        m1 = mask1.astype(bool)
        m2 = mask2.astype(bool)

        # Compute intersection and union
        intersection = np.logical_and(m1, m2)
        sum_masks = m1.sum() + m2.sum()

        if sum_masks == 0:
            logger.warning("Both masks are empty")
            return {
                'dice': 1.0,  # Empty sets considered identical
                'intersection': 0,
                'union': 0,
                'iou': 1.0
            }

        # Dice coefficient
        dice = 2.0 * intersection.sum() / sum_masks

        # IoU (Intersection over Union / Jaccard index)
        union = np.logical_or(m1, m2)
        iou = intersection.sum() / union.sum() if union.sum() > 0 else 0.0

        logger.info(f"  Dice: {dice:.6f}")
        logger.info(f"  IoU: {iou:.6f}")

        return {
            'dice': float(dice),
            'intersection': int(intersection.sum()),
            'union': int(union.sum()),
            'iou': float(iou)
        }

    @staticmethod
    def compute_coverage(mask1, mask2, image_shape):
        """
        Compute coverage statistics for masks.

        Parameters
        ----------
        mask1 : numpy.ndarray
            First mask
        mask2 : numpy.ndarray
            Second mask
        image_shape : tuple
            Total image shape

        Returns
        -------
        dict
            Coverage statistics
        """
        logger.info("Computing coverage statistics...")

        total_pixels = np.prod(image_shape)

        # Individual mask coverage
        mask1_pixels = np.sum(mask1 > 0)
        mask2_pixels = np.sum(mask2 > 0)

        mask1_coverage = (mask1_pixels / total_pixels) * 100
        mask2_coverage = (mask2_pixels / total_pixels) * 100

        # Overlap
        overlap = np.logical_and(mask1 > 0, mask2 > 0)
        overlap_pixels = np.sum(overlap)
        overlap_coverage = (overlap_pixels / total_pixels) * 100

        # Overlap as percentage of each mask
        overlap_of_mask1 = (overlap_pixels / mask1_pixels * 100) if mask1_pixels > 0 else 0.0
        overlap_of_mask2 = (overlap_pixels / mask2_pixels * 100) if mask2_pixels > 0 else 0.0

        logger.info(f"  Mask 1 coverage: {mask1_coverage:.2f}%")
        logger.info(f"  Mask 2 coverage: {mask2_coverage:.2f}%")
        logger.info(f"  Overlap coverage: {overlap_coverage:.2f}%")

        return {
            'mask1_coverage_percent': float(mask1_coverage),
            'mask2_coverage_percent': float(mask2_coverage),
            'overlap_coverage_percent': float(overlap_coverage),
            'overlap_of_mask1_percent': float(overlap_of_mask1),
            'overlap_of_mask2_percent': float(overlap_of_mask2),
            'mask1_pixels': int(mask1_pixels),
            'mask2_pixels': int(mask2_pixels),
            'overlap_pixels': int(overlap_pixels),
            'total_pixels': int(total_pixels)
        }

    @staticmethod
    def compute_correlation(fixed_array, registered_array, mask=None):
        """
        Compute correlation coefficient between images.

        Parameters
        ----------
        fixed_array : numpy.ndarray
            Fixed image
        registered_array : numpy.ndarray
            Registered image
        mask : numpy.ndarray, optional
            Binary mask

        Returns
        -------
        dict
            Correlation statistics
        """
        logger.info("Computing correlation...")

        # Apply mask
        if mask is not None:
            valid_mask = mask > 0
            fixed = fixed_array[valid_mask]
            registered = registered_array[valid_mask]
        else:
            fixed = fixed_array.flatten()
            registered = registered_array.flatten()

        # Remove NaN
        valid_idx = ~(np.isnan(fixed) | np.isnan(registered))
        fixed = fixed[valid_idx]
        registered = registered[valid_idx]

        if len(fixed) < 2:
            return {
                'pearson_r': np.nan,
                'r_squared': np.nan,
                'n_samples': len(fixed)
            }

        # Pearson correlation
        correlation_matrix = np.corrcoef(fixed, registered)
        pearson_r = float(correlation_matrix[0, 1])
        r_squared = pearson_r ** 2

        logger.info(f"  Pearson r: {pearson_r:.6f}")
        logger.info(f"  R²: {r_squared:.6f}")

        return {
            'pearson_r': pearson_r,
            'r_squared': r_squared,
            'n_samples': len(fixed)
        }

    @staticmethod
    def compute_all_metrics(fixed_array, registered_array, fixed_mask=None,
                           registered_mask=None, image_shape=None):
        """
        Compute all quality metrics.

        Parameters
        ----------
        fixed_array : numpy.ndarray
            Fixed image
        registered_array : numpy.ndarray
            Registered image
        fixed_mask : numpy.ndarray, optional
            Fixed image mask
        registered_mask : numpy.ndarray, optional
            Registered image mask
        image_shape : tuple, optional
            Image shape for coverage calculation

        Returns
        -------
        dict
            Dictionary with all metrics
        """
        logger.info("="*60)
        logger.info("Computing all quality metrics")
        logger.info("="*60)

        # Determine overlap mask
        if fixed_mask is not None and registered_mask is not None:
            overlap_mask = np.logical_and(fixed_mask > 0, registered_mask > 0).astype(np.uint8)
        elif fixed_mask is not None:
            overlap_mask = fixed_mask
        elif registered_mask is not None:
            overlap_mask = registered_mask
        else:
            overlap_mask = None

        metrics = {}

        # RMSE
        try:
            rmse_metrics = QualityMetrics.compute_rmse(
                fixed_array, registered_array, mask=overlap_mask
            )
            metrics.update(rmse_metrics)
        except Exception as e:
            logger.error(f"RMSE computation failed: {e}")
            metrics.update({'rmse': np.nan, 'mae': np.nan})

        # Mutual Information
        try:
            mi_metrics = QualityMetrics.compute_mutual_information(
                fixed_array, registered_array, mask=overlap_mask
            )
            metrics.update(mi_metrics)
        except Exception as e:
            logger.error(f"MI computation failed: {e}")
            metrics.update({'mutual_information': np.nan, 'normalized_mi': np.nan})

        # Correlation
        try:
            corr_metrics = QualityMetrics.compute_correlation(
                fixed_array, registered_array, mask=overlap_mask
            )
            metrics.update(corr_metrics)
        except Exception as e:
            logger.error(f"Correlation computation failed: {e}")
            metrics.update({'pearson_r': np.nan, 'r_squared': np.nan})

        # Dice coefficient and coverage (if masks provided)
        if fixed_mask is not None and registered_mask is not None:
            try:
                dice_metrics = QualityMetrics.compute_dice_coefficient(
                    fixed_mask, registered_mask
                )
                metrics.update(dice_metrics)
            except Exception as e:
                logger.error(f"Dice computation failed: {e}")
                metrics.update({'dice': np.nan})

            if image_shape is not None:
                try:
                    coverage_metrics = QualityMetrics.compute_coverage(
                        fixed_mask, registered_mask, image_shape
                    )
                    metrics.update(coverage_metrics)
                except Exception as e:
                    logger.error(f"Coverage computation failed: {e}")

        logger.info("="*60)
        logger.info("Quality metrics computed successfully")
        logger.info("="*60)

        return metrics
