"""
Convert LAS datasets to a Digital Surface Model (DSM) using arcpy
"""

import arcpy
import os

outDir = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\DSMs"
inDir = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\las_tiles"

# Get the list of LAS tiles to process
tiles = [f for f in os.listdir(inDir) if os.path.isfile(os.path.join(inDir, f))]

arcpy.env.overwriteOutput = True

# # Specifies the output coordinate system to 3TM
with arcpy.EnvManager(
    cellSize="1",
    outputCoordinateSystem="PROJCS['NAD_1983_CSRS_3TM_114',GEOGCS['GCS_North_American_1983_CSRS',DATUM['D_North_American_1983_CSRS',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-114.0],PARAMETER['Scale_Factor',0.9999],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]",
    workspace="memory",
):
    # For each tile in the list
    for tile in tiles:
        outName = f"{tile.split('.')[0]}.tif"
        outFile = os.path.join(outDir, outName)
        # If it's been processed, skip it
        if arcpy.Exists(outFile):
            print(f"{outName} already exists, skipping")
        else:
            # Else, convert the LiDAR Data to a DSM with a 1m cell size
            print(f"Converting {outName}")
            try:
                raster = "raster"
                output = "output"
                arcpy.conversion.LasDatasetToRaster(
                    in_las_dataset=os.path.join(inDir, tile),
                    out_raster=output,
                    value_field="ELEVATION",
                    interpolation_type="BINNING AVERAGE LINEAR",
                    data_type="FLOAT",
                    sampling_type="CELLSIZE",
                    sampling_value="1",
                    z_factor=1,
                )
                raster = arcpy.Raster(output)
                raster.save(outFile)
                print(f"\tDone {outName}")
            except arcpy.ExecuteError:
                print(f"\tSomething went wrong with {tile}")
                print(arcpy.GetMessages())
                break
            except Exception as err:
                print(f"\tSomething went wrong with {tile}")
                print(err.args[0])
                break
