---
title: "Point Delineation GH Page"
author: "Kyle O'Neil"
date: "April 6, 2016"
output: 
  html_document
  keep_md: yes
---




## Point Delineation Documentaiton
This project serves as an example workflow to delineating point locations on a 
stream network using the 
[NHDHRDV2 hydrography layers](http://conte-ecology.github.io/shedsGisData/). 
Culvert and flow gage locations in the Deerfield watershed in MA & VT are 
delineated as part of the MassDOT Culvert Project (Figure 1). Additionally, 
watershed attributes are caluclated for each of the given locations. Any tools 
referenced are assumed for ArcMap 10.2. The documentaiton is broken into the 
following sections: <br>
**1. Source Layers** <br>
**2. Layer Pre-processing** <br>
**3. Location Editing** <br>
**4. Watershed Delineation** <br>
**5. Additional Analysis** <br>
**6. Catchment Attributes** <br>


![Figure 1](https://cloud.githubusercontent.com/assets/6216239/14360676/82a1be6e-fcc5-11e5-8a41-b16be0630d9b.png)

Figure 1: Deerfield watershed with culvert and gage locations
<br><br>

## Source Layers
The intermediate hydrography processing layers from the NHDHRDV2 dataset are 
required for the delineation process. Not all of these layers are made public, 
but are available upon request. In addition to the source layers listed in the 
table below, a spatial points layer representing the locations to be delineated 
is required. If the points are not already mapped to the stream grid, this is 
done in the **Location Editing** section. 


| Description                        | Filename              | Directory                                          |
|:-----------------------------------|:----------------------|:---------------------------------------------------|
| Catchment Layer                    | Catchment01           | HRD\V2\gisFiles\NHDH01\arcHydro\vectors.gdb\Layers |
| Flow direction grid                | Fdr01                 | HRD\V2\gisFiles\NHDH01\arcHydro\Layers             |
| Flow accumulation grid             | Fac01                 | HRD\V2\gisFiles\NHDH01\arcHydro\Layers             |
| Stream grid (final)                | strFinal01            | HRD\V2\gisFiles\NHDH01\arcHydro\Layers             |
| Drainage line (final)              | DrainageLineFinal01   | HRD\V2\gisFiles\NHDH01\arcHydro\vectors.gdb\Layers |
| High res flowlines                 | detailedFlowlines01   | HRD\V2\products\hydrography.gdb                    |
| Points layer                       | crossings_delineation | User-specified                                     |
| Digital Elevation Model (optional) | dem                   | HRD\V2\gisFiles\NHDH01\arcHydroInput.gdb           |
Table 1: Required source layers from NHDHRDV2 dataset

## Layer Pre-processing

**1. Define Processing Zone** <br>
The processing zone shapefile is created, encompasing the full extent of the 
potential contributing drainage area to the points being processed. This can be 
based on  a HUC boundary layer, selected catchments, or some other processing 
area designation layer. Whatever the method, it is important to maintain network 
connectivity within the desired watershed. Splitting a watershed by excluding 
contributing drainage area will result in incorrect delineation.

**2. Buffer Processing Zone** <br>
The processing zone shapefile is buffered (*Analysis Tools > Proximity > Buffer*)
to ensure all features in the necessary processing range are captured. 1 - 2 km 
is a reasonable buffer length. This step is not necessary if the original shapefile 
certain to contain all required catchments and flowlines.

**3. Generate Vector Layers** <br>
Features from each of the Drainage Line and Catchment layers that intersect 
the buffer layer are selected and exported as new layers.

**4. Generate Raster Layers** <br>
The stream grid, dem, flow direction grid and flow accumulation grid 
are clipped to the buffer layer using the Extract by Mask tool 
(*Spatial Analyst Tools > Extraction > Extract by Mask*).

**5. Create Snap Stream Grid** <br>
A stream grid used for snapping points (`strSnap50`) is created using the 
Reclassify tool (*Spatial Analyst Tools > Reclass > Reclassify*). In this 
case, cells in the flow accumulation layer with 50 or more contributing cells 
are reclassfied as a value of 1 to define the snapping grid. All other cells 
are reclassified as "NoData".


## Location Editing

The delineation process requires location points to be snapped to the 
`strSnap50` layer (Figure 2). Before this snapping is completed, the 
points must be  manually inspected to ensure that they will snap to sensible 
locations on the stream grid. For visual inspection, the stream grid 
(`strFinal`) is displayed over the `strSnap50` layer. The high resolution 
flowline vector layer (`strHR`) is also displayed for reference in the manual 
inspection process. 

![Figure 2](https://cloud.githubusercontent.com/assets/6216239/14295484/d84dbcf6-fb43-11e5-9909-d578fddea8db.png)

Figure 2: Example of snapping a point to the snap stream grid
<br><br>

As a general rule, relative positioning of the point on the `strHR` vector layer 
should be reflected in its position on the stream grid after snapping. Figure 3 
shows an example of a correction to ensure the point is located on the correct 
branch of the stream grid with respect to it's location on the vector layer. 

![Figure 3](https://cloud.githubusercontent.com/assets/6216239/14295485/d850c892-fb43-11e5-942f-757504d4fe0b.png)

Figure 3: Adjustment of a point to the correct position on the stream grid
<br><br>


Differences between the stream and snap grids also require adjustment of points 
to ensure they fall on the correct channel. Figure 4 shows how a point may fall 
onto a seemingly accurate position on the snap stream grid (`strSnap50`), but 
actually needs to be corrected to fall into the main channel of the stream 
represented by `strFinal`. 

![Figure 4](https://cloud.githubusercontent.com/assets/6216239/14295486/d852824a-fb43-11e5-8c52-5ea70749c804.png)

Figure 4: Location adjustment to ensure point falls on the main stream channel
<br><br>

In some cases locations are on such small, undocumented streams that snapping 
should be turned off for that particular point (Figure 5). These points are 
noted and will be identified in the "SnapOn" column of the **Batch Point Setup** 
step of the next section.

![Figure 5](https://cloud.githubusercontent.com/assets/6216239/14295483/d84c727e-fb43-11e5-9d05-b4aedbf056b1.png)

Figure 5: Example of a point, located on an undocumented stream, that does not  
get snapped to the stream grid
<br><br>


## Watershed Delineation
The watershed delineation process takes advantage of the ArcHydro tools. Layers 
are conformed to the specifications of these tools. It is necessary to follow 
the steps in order to generate the watersheds polygon layer.

**1. Adjoint Catchment Processing**

***Input*** <br>
Drainage Line: DrainageLineFinal <br> 
Catchment: Catchment <br>

***Output*** <br>
Adjoint Catchment: AdjointCatchment <br>
<br><br>

**2. Batch Point Setup**

Five columns are added to the point location layer using the "Add Field" tool 
(*Data Management Tools > Fields > Add Field*). These columns are necessary 
for batch delineation and are described in the table below.


| Name      | Type          | Value     | Description                                                                                                                    |
|:----------|:--------------|:----------|:-------------------------------------------------------------------------------------------------------------------------------|
| SnapOn    | Short integer | 1         | Identifies whether or not the site gets snapped to the steram grid. 0 = don't snap, 1 = snap                                   |
| BatchDone | Short integer | 0         | Identified whether or not the point has been processed by the Batch Waterhsed Delineation tool. 0 = unprocessed, 1 = processed |
| SrcType   | Short integer | 0         | Defines the point type. 0 = outlet, 1 = inlet                                                                                  |
| Name      | String        | XYCroCode | The unique ID assigned to the watershed                                                                                        |
| Descript  | String        | StrmName  | The description of the site                                                                                                    |
Table 2: Fields added to the point location layer to establish the "Batch Point" 
layer for delineation
<br><br>

**3. Batch Watershed Delineation**

***Input*** <br>
Batch Point: crossings_delineation <br>
Flow Direction Grid: fdr <br>
Stream Grid: strFinal <br>
Snap Stream Grid: strSnap50 <br>
Catchment: Catchment <br>
Adjoint Catchment: AdjointCatchment

***Output*** <br>
Watershed: Watershed <br>
Watershed Point: WatershedPoint
<br><br>

## Additional Analysis
This section describes the additional steps required to caluclate attributes 
specific to the MassDOT Culvert Project. These steps are not neccessary for 
creating watershed polygons.

**1. Longest Flow Path**

***Input*** <br>
Drainage Area: Watersheds <br>
Flow Direction Grid: fdr

***Output*** <br>
Longest Flow Path: LongestFlowPath
<br><br>

**2. Flow Path Parameters from 2D Line**

***Input*** <br>
Longest Flow Path: LongestFlowPath <br>
Raw DEM: dem <br>

***Output*** <br>
Slope 1085 Point: Slp1085Point
<br><br>


## Catchment Attributes
The steps in this section calculate the attributes for the watershed polygons. 
A small set of value rasters is used but can be added to if new attributes are 
desired.

**1. Spatial Layer Processing**

Once the spatial layers have been generated a post-processing script is run to 
add unique ID fields, calculate area/length, and export tables for use in later 
steps. The inputs are defined in the `spatialPostProcessing.py` script and it 
is executed in Arc Python.


| Variable            | Description                                                                                                                    | Example                       |
|:--------------------|:-------------------------------------------------------------------------------------------------------------------------------|:------------------------------|
| arcHydroGeodatabase | The path to the ArcHydro output geodatabase containing the hydrography layers (Watershed, WatershedPoint, and LongestFlowPath) | "C:/culverts/NHDHRDV2.gdb"    |
| uniqueID            | The name of the unique ID field used to populate the "Name" column in the Batch Point Setup step                               | "XYCroCode"                   |
| zonalStatsDirectory | The path to the parent directory where the attributes tables will be written                                                   | "C:/culverts/zonalStatistics" |
Table 3: User-inputs to the spatialPostProcessing.py script
<br><br>

**2. Calculate Zonal Statistics**
After the spatial layers are updated, the inputs to the 
`zonalStatisticsProcessing.py` script are defined and the script is executed in 
Arc Python.


| Variable            | Description                                                                                                                                                        | Example                                                               |
|:--------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------|
| zonalStatsDirectory | The  path to the parent directory where the attributes tables will be written                                                                                      | "C:/culverts/zonalStatistics"                                         |
| catchmentsFilePath  | The name of the unique ID field used to populate the "Name" column in the Batch Point Setup step                                                                   | "C:/culverts/NHDHRDV2.gdb/Watershed"                                  |
| zoneField           | The field identifying the watershed polygons over which stats are calculated, typically the same as the uniqueID variable in the "spatialPostProcessing.py" script | "XYCroCode"                                                           |
| rasterDirectory     | The directory path to where the value rasters are located                                                                                                          | "C:/culverts/spatial/rasters"                                         |
| rasterList          | The list of rasters to process                                                                                                                                     | ["slope_pcnt", "ann_prcp_mm", "surfcoarse", "elevation", "lccti.tif"] |
| statList            | The list of stats to process for each raster, positions must match the "rasterList"                                                                                | ["STD", "MEAN", "MEAN", "MEAN", "MIN_MAX_MEAN"]                       |
Table 4: User-inputs to the zonalStatisticsProcessing.py script
<br><br>

**3. Finalize Attributes**
The R script, `finalizeZonalStatistics.R`, edits the raw output from the "Zonal 
Statistics" tool for final output. The inputs are defined and the script is 
executed in R.

| Variable            | Description                                                                                                         | Example                                                                                                      |
|:--------------------|:--------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------|
| zonalStatsDirectory | The path to the parent directory where the attributes tables will be written                                        | "C:/culverts/zonalStatistics"                                                                                |
| outputName          | The name used to identify the output .RData file                                                                    | "deerfield"                                                                                                  |
| zoneField           | The field identifying the watershed polygons over which stats are calculated                                        | "XYCroCode"                                                                                                  |
| rasterList          | The list of rasters to process                                                                                      | c("slope_pcnt", "ann_prcp_mm", "surfcoarse", "elevation", "lccti.tif")                                       |
| statList            | The list of stat names used for proecssing raster. Names are used for column indexing and should match ArcGIS names | c("STD", "MEAN", "MEAN", "MEAN", "MIN_MAX_MEAN")                                                             |
| conversionFactor    | The conversion factors from the raw rater value to the final output value                                           | c(1, 0.0393701, 100, 3.28084, 1, 1, 1)                                                                       |
| newName             | The ouput name for the variables from the raw rasters                                                               | c("slope_pcnt_std", "ann_prcp_in", "surfcoarse", "elevation_ft", "lccti_mean",  "lccti_min", "channelSlope") |
Table 5: User-inputs to the finalizeZonalStatistics.R script
