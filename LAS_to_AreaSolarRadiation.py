"""
Creates an Area Solar Radiation Raster based on LAS point cloud
"""
import os
import arcpy
from sys import argv
import time


def LAS_to_DSM(in_las_file, out_dsm, cell_size="1"):
    """
    Creates a DSM from an input LAS dataset. Default cell size is 1m
    """
    print("Converting LiDAR to DSM....")
    out_dsm_file_name = out_dsm
    # Specifies the output coordinate system to 3TM
    with arcpy.EnvManager(
        cellSize=cell_size,
        outputCoordinateSystem="PROJCS['NAD_1983_CSRS_3TM_114',GEOGCS['GCS_North_American_1983_CSRS',DATUM['D_North_American_1983_CSRS',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-114.0],PARAMETER['Scale_Factor',0.9999],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]",
    ):
        arcpy.conversion.LasDatasetToRaster(
            in_las_dataset=in_las_file,
            out_raster=out_dsm,
            value_field="ELEVATION",
            interpolation_type="BINNING AVERAGE LINEAR",
            data_type="FLOAT",
            sampling_type="CELLSIZE",
            sampling_value=cell_size,
            z_factor=1,
        )
        out_dsm = arcpy.Raster(out_dsm)
        out_dsm.save(out_dsm_file_name)
    return out_dsm_file_name


def Create_Area_Solar_Radiation_Raster(
    DSM, out_area_solar_radiation_raster, day_interval, hour_interval
):
    """
    Creates an area solar radiation raster based on the DSM
    """
    print("Beginning area solar radiation calculation....")
    ## There are optional files that the tool can also output. They might be useful as some point
    Output_direct_radiation_raster = None
    Output_diffuse_radiation_raster = None
    Output_direct_duration_raster = None

    out_raster_file_name = out_area_solar_radiation_raster
    out_area_solar_radiation_raster = arcpy.sa.AreaSolarRadiation(
        in_surface_raster=DSM,
        latitude=49,
        sky_size=200,
        time_configuration="MultiDays 2020 1 366",  # WholeYear 2020 | MultiDays 2020 1 366
        day_interval=day_interval,
        hour_interval=hour_interval,
        each_interval="NOINTERVAL",
        z_factor=1,
        slope_aspect_input_type="FROM_DEM",
        calculation_directions=32,
        zenith_divisions=8,
        azimuth_divisions=8,
        diffuse_model_type="UNIFORM_SKY",
        diffuse_proportion=0.3,
        transmittivity=0.5,
        out_direct_radiation_raster=Output_direct_radiation_raster,
        out_diffuse_radiation_raster=Output_diffuse_radiation_raster,
        out_direct_duration_raster=Output_direct_duration_raster,
    )
    out_area_solar_radiation_raster.save(out_raster_file_name)
    return out_raster_file_name


def Clip_Area_Solar_Radiation_to_Buildings(
    in_area_solar_radiation, out_raster, buildings
):
    print("Clipping area solar radiation to buildings....")
    out_raster_file_name = out_raster
    extent = arcpy.Raster(in_area_solar_radiation).extent
    rectangle = f"{extent.XMin} {extent.YMin} {extent.XMax} {extent.YMax}"
    print(f"Raster Extent: {rectangle}")
    with arcpy.EnvManager(extent=extent):
        arcpy.management.Clip(
            in_raster=in_area_solar_radiation,
            rectangle=rectangle,
            out_raster=out_raster,
            in_template_dataset=buildings,
            nodata_value="3.4e+38",
            clipping_geometry="ClippingGeometry",
            maintain_clipping_extent="NO_MAINTAIN_EXTENT",
        )
        out_raster = arcpy.Raster(out_raster)
        out_raster.save(out_raster_file_name)
    return out_raster_file_name


def Get_Raster_Extent(in_raster, output_extent, env):
    """
    Computes the extent of a raster
    """
    extent = output_extent
    with arcpy.EnvManager(
        scratchWorkspace=env,
        workspace=env,
    ):
        arcpy.ddd.RasterDomain(
            in_raster=in_raster,
            out_feature_class=output_extent,
            out_geometry_type="POLYGON",
        )
    return extent


def printseperator():
    """
    Displays a seperator on the screen to make output easier to read
    """
    print("".join(["-" for i in range(30)]))


def Calculate_Statistics(
    raster_file,
    day_interval,
    hour_interval,
    cell_size,
):

    std_dev = arcpy.GetRasterProperties_management(raster_file, "STD")
    mean = arcpy.GetRasterProperties_management(raster_file, "MEAN")
    min_val = arcpy.GetRasterProperties_management(raster_file, "MINIMUM")
    max_val = arcpy.GetRasterProperties_management(raster_file, "MAXIMUM")

    print(
        f"Statistics for the whole year, every {day_interval} days at {hour_interval} hour intervals:"
    )
    print(f"Cell Size: {cell_size}m")
    print(f"Average: {mean}")
    print(f"Minimum: {min_val}")
    print(f"Maximum: {max_val}")
    print(f"Standard Deviation: {std_dev}")


def LAS_to_ASR(in_las_file, day_interval=14, hour_interval=0.5, cell_size="1"):
    """
    Creates a Area Solar Radiation raster from the input las file
    """

    printseperator()

    start_time = time.time()

    arcpy.env.overwriteOutput = False

    # Check out any necessary licenses.
    arcpy.CheckOutExtension("spatial")

    out_gdb_location = os.getcwd()

    in_name = os.path.splitext(os.path.basename(in_las_file))[0]
    out_name = in_name
    gdb_name = out_name
    suffix = 1
    while os.path.exists(os.path.join(out_gdb_location, gdb_name + ".gdb")):
        gdb_name = out_name + "_" + str(suffix)
        suffix += 1

    print("Start...")

    print(f'Creating file GDB "{gdb_name}"')
    out_gdb_name = arcpy.management.CreateFileGDB(
        out_folder_path=out_gdb_location, out_name=gdb_name, out_version="CURRENT"
    )[0]

    print(f'Created output File Geodatabase "{out_gdb_name}"')
    print(f'All output files will be in here, with a base name of "{out_name}"')

    # Building shapefile
    in_buildings = os.path.join(os.getcwd(), "Building_Footprints.shp")
    if not arcpy.Exists(in_buildings):
        raise RuntimeError("Could not find Building_Footprints shapefile")

    # Process: LAS Dataset To Raster (LAS Dataset To Raster) (conversion)
    out_dsm_file = f"{out_name}_DSM"
    out_dsm = os.path.join(out_gdb_name, out_dsm_file)
    out_dsm = LAS_to_DSM(in_las_file, out_dsm, cell_size)
    print(f'Created DSM "{out_dsm_file}", with a cell size of {cell_size}m')

    # Process: Area Solar Radiation (Area Solar Radiation) (sa)
    out_area_solar_radiation_raster_file = f"{out_name}_area_solar_radiation_raster"
    out_area_solar_radiation_raster = os.path.join(
        out_gdb_name, out_area_solar_radiation_raster_file
    )
    out_area_solar_radiation_raster = Create_Area_Solar_Radiation_Raster(
        out_dsm, out_area_solar_radiation_raster, day_interval, hour_interval
    )
    print(f'Created solar radiation raster "{out_area_solar_radiation_raster_file}"')

    # Process: Raster Domain (Raster Domain) (3d)
    dsm_extent = f"{out_dsm}_extent"
    dsm_extent = Get_Raster_Extent(out_dsm, dsm_extent, out_gdb_name)

    # Process: Clip (Clip) (analysis)
    out_clipped_buildings_file = f"{out_name}_buildings"
    out_clipped_buildings = os.path.join(out_gdb_name, out_clipped_buildings_file)
    arcpy.analysis.Clip(
        in_features=in_buildings,
        clip_features=dsm_extent,
        out_feature_class=out_clipped_buildings,
        cluster_tolerance="",
    )
    print(f'Clipped buildings to DSM extent, "{out_clipped_buildings_file}"')

    # Process: Clip Raster (Clip Raster) (management)
    out_clipped_area_solar_radiation_file = f"{out_name}_area_solar_radiation_clipped"
    out_clipped_area_solar_radiation = os.path.join(
        out_gdb_name, out_clipped_area_solar_radiation_file
    )
    Clip_Area_Solar_Radiation_to_Buildings(
        out_area_solar_radiation_raster,
        out_clipped_area_solar_radiation,
        out_clipped_buildings,
    )
    print(
        f'Clipped area solar radiation to building footprints, "{out_clipped_area_solar_radiation_file}"'
    )

    # print(f"Calculating statistics for {out_clipped_area_solar_radiation}")
    # Calculate_Statistics(
    #     out_clipped_area_solar_radiation, day_interval, hour_interval, cell_size
    # )

    end_time = time.time()

    print(f"Done! Process took {end_time - start_time} seconds")
    printseperator()


if __name__ == "__main__":
    # Global Environment settings
    with arcpy.EnvManager(
        scratchWorkspace="in_memory",
        workspace="in_memory",
    ):
        LAS_to_ASR(*argv[1:])
