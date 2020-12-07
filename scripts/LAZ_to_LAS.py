"""
Convert from LAZ files to LAS using LASTools
"""

import os
import subprocess
import time

tileList = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\Lethbridge_ASR\NewLidarTiles.txt"
command = r"C:\Program Files\LAStools\bin\las2las.exe"
inDir = r"E:\GIS Data\lidar\Lethbridge\2015\laz"
outDir = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\las_tiles"

count = 0
startTime = time.time()
# Read the list of lidar tiles from a text file
with open(tileList, "r") as tiles:
    for tile in tiles:
        if tile[-1] == "\n":
            tile = tile[:-1]
        lasTileName = f"{tile.split('.')[0]}.las"
        # If the .las version of the file exists, skip it
        if os.path.exists(os.path.join(outDir, lasTileName)):
            print(f"{tile} already converted, skipping")
        else:
            # Else, convert from LAZ to LAS using LASTools
            print(f"Converting Tile {tile} to LAS")
            print(f"\ttime so far: {time.time() - startTime:.2f} seconds")
            try:
                cmd = [
                    command,
                    "-i",
                    os.path.join(inDir, tile + ".laz"),
                    "-odir",
                    outDir,
                    "-olas",
                ]
                print(f"\tcommand used: {' '.join(cmd)}")
                subprocess.check_call(cmd)
                count += 1
                print(f"\tDone with {tile}")
            except:
                print(f"an error occurred with {tile}, moving on")
    print(f"Converted {count} tiles")

print(f"Total time: {time.time() - startTime:.2f} seconds")
