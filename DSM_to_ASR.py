"""
Calculate the Area Solar Radiation for each DSM
"""

import arcpy
from os.path import join
import sys

# Variables
inGDB = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\Lethbridge_ASR\Buffered_DSMs.gdb"
outGDB = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\Lethbridge_ASR\ASR_Rasters.gdb"
tile_index = "https://services1.arcgis.com/JIxJEU91T3GTguUM/arcgis/rest/services/Lidar_Tile_Index_2015/FeatureServer/0"

# Get the ASR rasters that already exist
arcpy.env.workspace = outGDB
existingRasters = arcpy.ListRasters("ASR_*")

# Determine tiles to process
arcpy.env.workspace = inGDB
baseName = "Buffered_DSM_"
bufferedRasters = arcpy.ListRasters(f"{baseName}*")
tiles = [
    t for t in bufferedRasters if f"ASR_{t.split('_', 2)[-1]}" not in existingRasters
]
total = len(tiles)

# Spatial reference object for NAD83 CSRS
gcs = arcpy.SpatialReference(8232)

count = 0
skipped = 0


def DSM_to_ASR(tile_name):
    """
    Converts a DSM raster to an Area Solar Radiation raster.
    """
    if arcpy.Exists(tile_name):
        print(f"starting {tile_name}")
        label = "_".join(tile_name.split("_")[-2:])
        outASR = f"ASR_{label}"
        outFile = join(outGDB, outASR)
        if arcpy.Exists(outFile):
            print(f"\tASR raster exists for {label}. skipping")
            global skipped
            skipped += 1
        else:
            try:
                # Get the raster
                raster = arcpy.Raster(tile_name)

                # Calculate the center latitude for the raster
                extent = raster.extent
                center_in_meters = arcpy.Point(
                    extent.XMin + ((extent.XMax - extent.XMin) / 2),
                    extent.YMin + ((extent.YMax - extent.YMin) / 2),
                )
                point = arcpy.PointGeometry(center_in_meters, raster.spatialReference)
                center_in_latlon = point.projectAs(gcs)
                latitude = center_in_latlon.centroid.Y

                # Convert to Area Solar Radiation raster, for the whole year,
                # using a daily time step, with half hour time intervals
                output = arcpy.sa.AreaSolarRadiation(
                    raster,
                    latitude,
                    200,
                    "MultiDays 2020 1 366",
                    1,
                    0.5,
                    "NOINTERVAL",
                    1,
                    "FROM_DEM",
                    32,
                    8,
                    8,
                    "UNIFORM_SKY",
                    0.3,
                    0.5,
                    None,
                    None,
                    None,
                )
                output.save(outFile)
                global count
                count += 1
                print(
                    f"\tdone. Saved to {outFile}\n\tCompleted at {datetime.today().strftime('%c')}"
                )
            except arcpy.ExecuteError:
                print(arcpy.GetMessages())
            except Exception as error:
                print(f"\tsomething went wrong with {label}:", error)
    else:
        print(f"can't find {tile_name}")


# Process the tiles in order of building count
with arcpy.da.SearchCursor(
    tile_index,
    ["Building_GEQ10M_Count", "Label"],
    "Building_GEQ10M_Count >= 5",
    sql_clause=(None, "ORDER BY Building_GEQ10M_Count DESC"),
) as cursor:
    for row in cursor:
        building_count, label = row
        try:
            tile = f"{baseName}{label}"
            if tile in tiles:
                tiles.remove(tile)
                DSM_to_ASR(tile)
        except ValueError:
            print(f"Could not find {label}")

# Process the remaining tiles, if any
for tile in tiles:
    tiles.remove(tile)
    DSM_to_ASR(tile)
