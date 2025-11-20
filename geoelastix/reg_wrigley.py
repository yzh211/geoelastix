import itk
# import cv2
from itkwidgets.widget_checkerboard import checkerboard
import numpy as np
# from matplotlib import image
import matplotlib.pyplot as plt
from osgeo import gdal
import os, sys

class ImagetoData():
    @staticmethod
    def read_raster(file_path):
        'Read raster datasets as array'
        dat = gdal.Open(file_path)
        array = dat.GetRasterBand(1).ReadAsArray()

        # create mask
        loc_noData = np.min(array)
        # loc_noData = np.where(np.isnan(array))
        array[array==loc_noData] = 0.
        mask = np.ones_like(array)
        mask[mask==loc_noData] = 0
        return array, mask

    @classmethod
    def write_image(cls, file_path, save_name):
        array, mask = cls.read_raster(file_path=file_path)
        array_image = itk.image_from_array(array.astype(itk.F))
        mask_image = itk.image_from_array(mask.astype(itk.UC))
        itk.imwrite(array_image, '../pics/' + save_name + '_data.mhd')
        itk.imwrite(mask_image, '../pics/' + save_name + '_mask.mhd')

    @staticmethod
    def read_img(file_name):
        # file_image = itk.imread('../pics/' + file_name+'_data.png', itk.F)
        # file_mask = itk.imread('../pics/' + file_name+'_mask.png', itk.UC)
        file_image = itk.imread('../pics/' + file_name+'_data.mhd', itk.F)
        file_mask = itk.imread('../pics/' + file_name+'_mask.mhd', itk.UC)
        return file_image, file_mask

class Reg_eval():
    'Evaluating registration'
    # TODO: mask nan data
    def __init__(self, fixed=None, moving=None):
        self.fixed = np.asarray(fixed).astype(float)
        self.moving = np.asarray(moving).astype(float)

    @property
    def abs_error(self):
        diff = self.fixed - self.moving
        return np.sum(np.abs(diff))

    @property
    def dice(self, empty_score=1.0):
        im1 = self.fixed.astype(np.bool)
        im2 = self.moving.astype(np.bool)

        if im1.shape != im2.shape:
            raise ValueError("shape mismatch: im1 and im2 must have the same shape.")

        im_sum = im1.sum() + im2.sum()
        if im_sum == 0:
            return empty_score
        
        # Compute Dice coefficient
        intersection = np.logical_and(im1, im2)

        return 2. * intersection.sum() / im_sum

    @classmethod
    def plt_dem(cls, dem, file_out='test.jpg'):
        if isinstance(dem, np.ndarray):
            array = dem
        else:
            array = np.asarray(dem).astype(float)
            
        fig, ax = plt.subplots(1,1, figsize=(3.0,3.0))
        ax.imshow(
            array,
            cmap='gray',
            vmin=600.0,
            vmax=1300.0
            )
        ax.patch.set_facecolor('none')
        
        ax.axis('off')

        # plt.subplots_adjust(
        #     left=0.01,
        #     right=0.99,
        #     top=0.99,
        #     bottom=0.01,
        #     hspace=0.001
        #     )
        plt.tight_layout()
        # cv2.imwrite('../pics/' + file_out, array)
        fig.savefig('../pics/' + file_out, facecolor=fig.get_facecolor(),
        dpi=1000)

if __name__ == "__main__":
    file = sys.path[0]
    sys.path.append(os.path.join(file, '../'))
    os.chdir(file)

    new_dem = "../GIS/wrigley_30ft_lidar_sm2.tif"
    old_dem = "../GIS/wrigley_30ft_legacy.tif"
    parameter = "../parameters/parameters_isonville_NA_NCC_ASGD.txt"

    ImagetoData.write_image(new_dem, save_name='fixed')
    ImagetoData.write_image(old_dem, save_name='moving')
    fixed_data, fixed_mask = ImagetoData.read_img(file_name='fixed')
    moving_data, moving_mask = ImagetoData.read_img(file_name='moving')

    # parameter file
    parameter_object = itk.ParameterObject.New()
    parameter_object.AddParameterFile(parameter)
    print(parameter_object)

    registered, parameters = itk.elastix_registration_method(
        fixed_data, moving_data,
        parameter_object=parameter_object,
        fixed_mask=fixed_mask, moving_mask=moving_mask,
        log_to_console=True
        )

    registered, parameters = itk.elastix_registration_method(
        fixed_data, moving_data,
        parameter_object=parameter_object,
        fixed_mask=fixed_mask, moving_mask=moving_mask,
        log_to_console=True
        )

    # save image
    itk.imwrite(registered, '../pics/' + 'reg_wrigley.mhd')
    itk.imwrite(fixed_data, '../pics/' + 'fixed_wrigley.mhd')
    itk.imwrite(moving_data, '../pics/' + 'moving_wrigley.mhd')

    # # Plot dem and checkerboard
    # Reg_eval.plt_dem(dem=registered, file_out='ison_reg_dem.jpg')
    # output = itk.checker_board_image_filter(fixed_data, registered)
    # Reg_eval.plt_dem(dem=output, file_out='ison_checker.jpg')
    # # itk.imwrite(output, '../pics/' + 'combine_image.mhd')