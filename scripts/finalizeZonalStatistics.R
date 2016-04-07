rm(list=ls())

# ==============
# Load libraries
# ==============
library(dplyr)
library(foreign)


# ==============
# Specify Inputs
# ==============
# Path to the zonal statistics directory
zonalStatsDirectory <- 'C:/KPONEIL/massDOTCulvertProject/zonalStatistics'

# Name for output file
outputName <- "deerfield"

# Unique ID
zoneField <- "XYCroCode"

# List of raster names, statistics list, conversion factors, and output names
rasterList       <- c(    "slope_pcnt", "ann_prcp_mm", "surfcoarse",    "elevation",      "lccti",      "lccti", "longestFlowPath")
statList         <- c(           "STD",        "MEAN",       "MEAN",         "MEAN",       "MEAN",        "MIN",       "Slp1085FM")
conversionFactor <- c(               1,     0.0393701,          100,        3.28084,            1,            1,                 1)
newName          <- c("slope_pcnt_std", "ann_prcp_in", "surfcoarse", "elevation_ft", "lccti_mean",  "lccti_min",    "channelSlope")

# ==========
# Load files
# ==========

# Shapefile
# -----------
shapeAreas <- read.dbf(paste0(zonalStatsDirectory, "/gisTables/watershed.dbf"))[,c(zoneField, "AreaSqKM")]
shapeAreas$AreaSqMI <- shapeAreas$AreaSqKM*0.386102
shapeAreas$XYCroCode <- as.character(shapeAreas$XYCroCode)

# Rasters
# -------
attributes <- shapeAreas[,c(zoneField, "AreaSqMI")]

# Loop through layers, reading files.
for (j in seq_along(rasterList)){
  
  # File path to table
  tableFilePath <- file.path(paste0(baseDirectory, "/gisTables"), paste0(rasterList[j], ".dbf"))
  
  # Open table
  dbfTable <-read.dbf(tableFilePath)[,c(zoneField, statList[j])]
  names(dbfTable)[2] <- newName[j]
  dbfTable[2] <- dbfTable[2]*conversionFactor[j]
  dbfTable$XYCroCode <- as.character(dbfTable$XYCroCode)
  
  attributes <- left_join(attributes, dbfTable, by = zoneField)
}


# ===========
# Save output
# ===========
save(attributes, file = paste0(baseDirectory, "/attributes_", outputName, ".RData"))
