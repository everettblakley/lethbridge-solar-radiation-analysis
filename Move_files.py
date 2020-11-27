import os
import shutil

tileList = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\Lethbridge_ASR\NewLidarTiles.txt"
dsmDir = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\DSMs"
outDir = r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\NewDSMs"

with open(tileList, "r") as tiles:
    for tile in tiles:
        if tile[-1] == "\n":
            tile = tile[:-1]
        extensions = [".tif", ".tfw", ".tif.ovr", ".tif.aux.xml"]
        for ext in extensions:
            dsmName = f"{tile.split('.')[0]}{ext}"
            currentFile = os.path.join(dsmDir, dsmName)
            newFile = os.path.join(outDir, dsmName)
            if os.path.exists(currentFile):
                print(f"Moving {dsmName}")
                shutil.move(currentFile, newFile)
