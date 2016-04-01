#Import System Modules:
import arcpy
from arcpy import env
from arcpy.sa import *


# ==============
# Specify inputs
# ==============
# Path to the zonal statistics directory
baseDirectory = "C:/KPONEIL/massDOTCulvertProject/zonalStatistics"

# Catchments file path
catchmentsFilePath =  "C:/KPONEIL/massDOTCulvertProject/spatial/NHDHRDV2/NHDHRDV2.gdb/Layers/Watershed"

# Field name defining the zones
zoneField = "XYCroCode"

# Raster directory path
rasterDirectory = "C:/KPONEIL/massDOTCulvertProject/spatial/rasters"

# Raster names and associated stat to calculate
rasterList = ["slope_pcnt", "ann_prcp_mm", "surfcoarse", "elevation",    "lccti.tif"]
statList   = [       "STD",        "MEAN",       "MEAN",      "MEAN", "MIN_MAX_MEAN"]


# =============
# Install Tools
# =============
# Import the supplemental tools (downloaded from here: http://blogs.esri.com/esri/arcgis/2013/11/26/new-spatial-analyst-supplemental-tools-v1-3/#comment-7007)
arcpy.ImportToolbox("C:/KPONEIL/tools/ArcGIS/SpatialAnalystSupplementalTools/Spatial Analyst Supplemental Tools.pyt")


# ================
# Define Functions
# ================
# Check if an index exists in a table
def indexExists(tablename,indexname):
 if not arcpy.Exists(tablename):
  return False
 tabledescription = arcpy.Describe(tablename)
 for iIndex in tabledescription.indexes:
  if (iIndex.Name == indexname):
   return True
 return False
 

# ===========
# Folder prep
# ===========
# Check if folder exists and create it if not

# Output tables
gisTables_directory = baseDirectory + "/gisTables"
if not arcpy.Exists(gisTables_directory): arcpy.CreateFolder_management(baseDirectory, "gisTables")


# ==========
# Add layers
# ==========
# Define map
mxd = arcpy.mapping.MapDocument("CURRENT")
# Define dataframe
df = arcpy.mapping.ListDataFrames(mxd)[0]

# Add the catchments layer to the map
addLayer = arcpy.mapping.Layer(catchmentsFilePath)
arcpy.mapping.AddLayer(df, addLayer, "AUTO_ARRANGE")


# ====================
# Run Zonal Statistics
# ====================

zoneObject = catchmentsFilePath

# Add attribute index to increase performance
if indexExists(zoneObject,zoneField + "_ind") is False:
  arcpy.AddIndex_management(zoneObject, zoneField, zoneField + "_ind", "UNIQUE", "NON_ASCENDING")


for i in range(len(rasterList)):
		
	raster = rasterList[i]
	statType = statList[i]

	rasterName = rasterList[i].split('.')[0]
		
	# Name of output table
	outTable = gisTables_directory + "/" + rasterName + ".dbf"
		
	arcpy.ZonalStatisticsAsTable02_sas(zoneObject,
										zoneField,
										rasterDirectory + "/" + raster,
										outTable,
										statType,
										"DATA")	
											
	# Check for missing catchments. If some catchments are missing from the output table, then run the script to fill these in.
	cat = arcpy.GetCount_management(zoneObject) 
	catRows = int(cat.getOutput(0))
	tab = arcpy.GetCount_management(outTable)
	tabRows = int(tab.getOutput(0))

	# Might want to write this as a function
	if tabRows < catRows:

		arcpy.MakeFeatureLayer_management(zoneObject, "zoneObject_Lyr")
	
		# Calculate catchments with missing data
		# --------------------------------------
		# Join the output file to the catchments file
		attributeJoin = arcpy.AddJoin_management ("zoneObject_Lyr", 
													zoneField, 
													outTable, 
													zoneField)
		
		# Define the query
		qry = rasterName + "."  + zoneField + ' IS NULL'
		
		# Export the missing features as a new table
		missingVals = arcpy.TableToTable_conversion("zoneObject_Lyr",
													gisTables_directory,
													rasterName + "_" + "MissingValues.dbf",
													qry)
		
		# Delete the temporary feature layer
		arcpy.Delete_management("zoneObject_Lyr")		
		
		# Add a new field for the table to match the zonal statistics output table
		arcpy.AddField_management(missingVals, "AREA", "DOUBLE")
		arcpy.AddField_management(missingVals, statType, "DOUBLE")

		arcpy.CalculateField_management (missingVals, "AREA", 0, "PYTHON_9.3")
		arcpy.CalculateField_management (missingVals, statType, -9999, "PYTHON_9.3")							

		# Append the missing values to the existing table
		arcpy.Append_management(missingVals,
									outTable,
									"NO_TEST")