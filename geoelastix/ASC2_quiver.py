from ASC2_rectification import *
import matplotlib.pyplot as plt

def dem_reg(new_dem, old_dem, parameterFile):
    ImagetoData.write_image(new_dem, save_name='fixed')
    ImagetoData.write_image(old_dem, save_name='moving')
    fixed_data, fixed_mask = ImagetoData.read_img(file_name='fixed')
    moving_data, moving_mask = ImagetoData.read_img(file_name='moving')

    # parameter file
    parameter_object = itk.ParameterObject.New()
    parameter_object.AddParameterFile(parameterFile)

    registered, parameters = itk.elastix_registration_method(
        fixed_data, moving_data,
        parameter_object=parameter_object,
        fixed_mask=fixed_mask, moving_mask=moving_mask,
        log_to_console=True,
        output_directory="../parameters/"
    )

    return registered, parameters

def deform_field(new_dem, transformParameters):
    if isinstance(transformParameters, str):
        parameter_object = itk.ParameterObject.New()
        parameter_object.AddParameterFile(transformParameters)
    else:
        parameter_object = transformParameters

    ImagetoData.write_image(new_dem, save_name='fixed')
    fixed_data, fixed_mask = ImagetoData.read_img(file_name='fixed')
    deformation_field = itk.transformix_deformation_field(
        fixed_data, parameter_object)
    deformation_field = np.asarray(deformation_field).astype(itk.F)
    return deformation_field[:, :, 0], deformation_field[:, :, 1]

def plot_dfield(x, y, gq, save_name):
    s = (x*x + y*y)**0.5
    gq_lons, gq_lats = raster_coords(gq)
    msk = raster_mask(gq)
    s = np.ma.masked_array(s, mask=msk)
    x = np.ma.masked_array(x, mask=msk)
    y = np.ma.masked_array(y, mask=msk)
    # gq_lons = np.ma.masked_where(np.ma.getmask(m),gq_lons)
    # gq_lats = np.ma.masked_where(np.ma.getmask(m),gq_lats)
    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    cp = ax.contourf(
        gq_lons[::, ::],
        gq_lats[::, ::],
        s[::, ::],
        levels=np.arange(0,21,5),
        cmap="Blues",
        extend='max'
    )
    cb = plt.colorbar(cp)
    quiv = plt.quiver(
        gq_lons[::200, ::200],
        gq_lats[::200, ::200],
        -x[::200, ::200],
        y[::200, ::200],
        angles='xy',
        scale_units='xy',
        scale=0.01
    )
    ax.axis("off")
    ax.set_aspect('equal')
    plt.savefig("../pics/" + save_name, dpi=1000)


if __name__ == "__main__":
    data_path = "./geoelastix/GIS/Jason_ASCIIs/"
    transformParameter = "../parameters/TransformParameters.0.txt"
    parameter1 = "../parameters/parameters_isonville_NA_MI_GD.txt"
    parameter2 = "../parameters/parameters_isonville_NA_NCC_ASGD.txt"
    # lowercase_filenames(data_path)
    legacy_filenames, lidar_filenames = sort_files(data_path)    
    parameter_names = [
        # "TS_MI_ASGD",
        # "RG_MI_ASGD",
        # "AF_MI_ASGD"        
        "NA_MI_GD",
        "NA_NCC_ASGD",
        # "NA_MSD_ASGD",
        # "NA_MI_ASGD"
    ]

    for newDEM, legacyDEM in zip(lidar_filenames, legacy_filenames):
        registered, parameters = dem_reg(newDEM, legacyDEM, parameter1)
        registered, parameters = dem_reg(newDEM, legacyDEM, parameter2)

        # Calculate deformation field
        x_disp, y_disp = deform_field(newDEM, transformParameter)

        # Plot the deformation field
        plot_dfield(
            x_disp_array,
            y_disp_array,
            gq,
            save_name="sandy_deformation_field.jpg"
        )
        print("success")