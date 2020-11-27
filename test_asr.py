import arcpy

outGDB = (
    r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\Lethbridge_ASR\Default.gdb"
)

out_global_radiation_raster = arcpy.sa.AreaSolarRadiation(
    r"C:\Users\evere\Courses\Fall_2020\GEOG4740\GroupProject\DSMs\845_5511.tif",
    49.6754711163158,
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

import os

outFile = os.path.join(outGDB, "asr_845_5511")

out_global_radiation_raster.save(outFile)
