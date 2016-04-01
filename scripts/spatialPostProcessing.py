# ==============
# Specify inputs
# ==============

# Geodatabase used in the ArcHydro process
arcHydroGeodatabase = "C:/KPONEIL/massDOTCulvertProject/spatial/NHDHRDV2/NHDHRDV2.gdb"

# Field name defining the zones
uniqueID = "XYCroCode"

# Path to the zonal statistics directory
zonalStatsDirectory = "C:/KPONEIL/massDOTCulvertProject/zonalStatistics"


# ================
# Define Functions
# ================
# Function to check for the existence of the field
def fieldExists(inFeatureClass, inFieldName):
   fieldList = arcpy.ListFields(inFeatureClass)
   for iField in fieldList:
      if iField.name.lower() == inFieldName.lower():
         return True
   return False


# ===========
# Folder prep
# ===========
# Check if folder exists and create it if not
# Output tables
gisTablesDirectory = zonalStatsDirectory + "/gisTables"
if not arcpy.Exists(gisTablesDirectory): arcpy.CreateFolder_management(zonalStatsDirectory, "gisTables")


# =============
# Layer editing
# =============

# Watershed
# ---------
watershed = arcHydroGeodatabase + "/Layers/Watershed"


# Add common unique ID field
if fieldExists(watershed, uniqueID) == False:
  arcpy.AddField_management(watershed, uniqueID, "Text")
  arcpy.CalculateField_management(watershed, uniqueID, "!Name!", "PYTHON_9.3")	

# Add area field
if fieldExists(watershed, "AreaSqKM") == False:  
  arcpy.AddField_management(watershed, "AreaSqKM", "DOUBLE")
  arcpy.CalculateField_management(watershed, "AreaSqKM", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON")
  
# Save as dbf (for external accessibility)
if arcpy.Exists(gisTablesDirectory + "/watershed.dbf") == False: 
  arcpy.TableToTable_conversion(watershed, gisTablesDirectory, "watershed.dbf")


# Watershed Point
# ---------------
watershedPoint = arcHydroGeodatabase + "/Layers/WatershedPoint"

# Add common unique ID field
if fieldExists(watershedPoint, uniqueID) == False:
  arcpy.AddField_management(watershedPoint, uniqueID, "Text")
  arcpy.CalculateField_management(watershedPoint, uniqueID, "!Name!", "PYTHON_9.3")	


# Longest Flowpath
# ----------------
longestFlowPath = arcHydroGeodatabase + "/Layers/LongestFlowPath"

# Add zoneField
if fieldExists(longestFlowPath, uniqueID) == False:

  # Add common unique ID field
  arcpy.AddField_management(longestFlowPath, uniqueID, "Text")
  
  # Join watershed for grabbing unique ID
  arcpy.MakeFeatureLayer_management(longestFlowPath, "longestFlowPathLyr")
  arcpy.AddJoin_management("longestFlowPathLyr", "DrainID", "C:/KPONEIL/workspace/watershed.dbf", "HydroID")
  
  # Calculate unique ID field
  arcpy.CalculateField_management("longestFlowPathLyr", uniqueID, "!watershed.Name!", "PYTHON_9.3") 

  # Drop the join
  arcpy.RemoveJoin_management("longestFlowPathLyr")

  # Save as dbf (for external accessibility)
  if arcpy.Exists(gisTablesDirectory + "/longestFlowPath.dbf") == False: 
    arcpy.TableToTable_conversion(longestFlowPath, gisTablesDirectory, "longestFlowPath.dbf") 

  # Delete the temporary layer
  arcpy.Delete_management("longestFlowPathLyr")
