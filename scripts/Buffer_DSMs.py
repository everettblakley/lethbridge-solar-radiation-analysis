"""
Clips the city-wide DSM to individual DSMs
"""

import arcpy
from os.path import join

outGdb = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\Lethbridge_ASR\Buffered_DSMs.gdb"
mosaic = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\Lethbridge_ASR\Default.gdb\Lethbridge_DSM"
tiles = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\Lethbridge_ASR\Default.gdb\DSM_Tiles_Buffer100"

tiles_fl = arcpy.MakeFeatureLayer_management(tiles, "tiles")
arcpy.env.overwriteOutput = True

# Iterate through the tiles in the tiles polygon layer
with arcpy.da.SearchCursor(tiles_fl, ["Name", "SHAPE@"]) as cursor:
    for row in cursor:
        selection = arcpy.management.SelectLayerByAttribute(
            tiles_fl, "NEW_SELECTION", f"Name = '{row[0]}'"
        )
        outFileName = "Buffered_DSM_" + row[0]
        outFile = join(outGdb, outFileName)

        # If we've already processed the DSM, skip it
        if arcpy.Exists(outFile):
            print(f"skipping {outFile}")
        else:
            ## Else, clip the DSM to the tile
            print(f"Clipping to {row[0]}")
            try:
                arcpy.management.Clip(
                    mosaic,
                    str(row[1].extent),
                    outFile,
                    selection,
                    clipping_geometry=True,
                )
                print("\tdone")
            except arcpy.ExecuteError:
                print(arcpy.GetMessages())
            except:
                print(f"\tsomething went wrong")
