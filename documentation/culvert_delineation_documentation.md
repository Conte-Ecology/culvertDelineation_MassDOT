---
title: "SHEDS Data GH Page"
author: "Kyle O'Neil"
date: "March 30, 2016"
output: 
  html_document
  keep_md: yes
---




# Point Delineation Documentaiton

-Tools referenced are ArcMap 10.2.

## Source Layers


| Description            | Filename            | Directory                                          |
|:-----------------------|:--------------------|:---------------------------------------------------|
| Catchment Layer        | Catchment01         | HRD\V2\gisFiles\NHDH01\arcHydro\vectors.gdb\Layers |
| Flow direction grid    | Fdr01               | HRD\V2\gisFiles\NHDH01\arcHydro\Layers             |
| Flow accumulation grid | Fac01               | HRD\V2\gisFiles\NHDH01\arcHydro\Layers             |
| Stream grid (final)    | strFinal01          | HRD\V2\gisFiles\NHDH01\arcHydro\Layers             |
| Drainage line (final)  | DrainageLineFinal01 | HRD\V2\gisFiles\NHDH01\arcHydro\vectors.gdb\Layers |
| High res flowlines     | detailedFlowlines01 | HRD\V2\products\hydrography.gdb                    |


## Layer Prep

1. The processing zone shapefile is created, encompasing the full extent of the potential 
contributing drainage area to the points being processed. This can be based on  
a HUC boundary layer, selected catchments, or some other processing area 
designation layer. Whatever the method, it is important to maintain network 
connectivity within the desired watershed. Splitting a watershed by excluding 
contributing drainage area will result in incorrect delineation.

2. The processing zone shapefile is buffered (*Analysis Tools > Proximity > Buffer*)
to ensure all features are included. 1 or 2 km is a reasonable buffer length. 

3. Features from each of the Drainage Line and Catchment layers that intersect 
the buffer layer are selected and export as new layers.

4. The final stream grid as well as the flow direction and accumulation grids are clipped to the buffer layer 
using the Extract by Mask tool (*Spatial Analyst Tools > Extraction > Extract by Mask*).

5. The Drainage Line layer is rasterized (*Conversion Tools > To Raster > Feature To Raster*) 
to create the flow grid (strFinal). The 

6. A stream grid for snapping points is created using the Reclassify tool (*Spatial Analyst Tools > Reclass > Reclassify*).
In this case, cells in the the flow accumulation layer with 50 or more contributing cells define the snapping grid. All other cells are treated as "NoData"


## Location Editing

The delineation process requires location points to be snapped to the snap stream grid (`strSnap50`) (Figure 1). Before this snapping is completed, the points must be  manually inspected to ensure that the points will snap to sensible locations on the stream grid. For visual inspection, the stream grid (`strFinal`) is displayed over the snap stream grid. The high resolution flowline vector layer is also used in this manual inspection process. 

![Figure 1](https://cloud.githubusercontent.com/assets/6216239/14295484/d84dbcf6-fb43-11e5-9909-d578fddea8db.png)
Figure 1: Example of snapping a point to the snap stream grid
<br><br>

As a general rule, relative positioning of the point on the vector layer should be reflected in it's position on the stream grid after snapping. Figure 2 shows an example of a correction to ensure the point is located on the correct branch of the flow grid with respect to it's location on the vector layer. 

![Figure 2](https://cloud.githubusercontent.com/assets/6216239/14295485/d850c892-fb43-11e5-942f-757504d4fe0b.png)
Figure 2: Adjustment of a point to the correct position on the stream grid
<br><br>


Differences between the stream and snap grids also require adjustment of points to ensure they fall on the correct channel. Figure 3 shows how a point may fall onto a seemingly accurate position on the snap stream grid, but actually needs to be corrected to fall into the main channel of the stream. 

![Figure 3](https://cloud.githubusercontent.com/assets/6216239/14295486/d852824a-fb43-11e5-8c52-5ea70749c804.png)
Figure 3: Location adjustment to ensure point falls on the main stream channel
<br><br>

In some cases locations are on such small, undocumented streams that snapping should be turned off for that particular point (Figure 4). These points are noted and will be identified in the "SnapOn" column of the Batch Point Setup step of the next section.

![Figure 4](https://cloud.githubusercontent.com/assets/6216239/14295483/d84c727e-fb43-11e5-9d05-b4aedbf056b1.png)
Figure 4: Example of a point located on an undocumented stream, resulting in snapping being turned off
<br><br>


## Watershed Delineation
The watershed delineation process takes advantage of the ArcHydro tools. Layers are conformed to the specifications of these tools.

1. Adjoint Catchment Processing

  *Input* 

  Drainage Line: DrainageLineFinal 

  Catchment: Catchment 

  *Output* 

  Adjoint Catchment: AdjointCatchment 


2. Batch Point Setup

  Five columns are added to the point location layer. These columns are necessary for batch delineation and are described in the table below.


| Name      | Type          | Value     | Description                                                                                                                    |
|:----------|:--------------|:----------|:-------------------------------------------------------------------------------------------------------------------------------|
| SnapOn    | Short integer | 1         | Identifies whether or not the site gets snapped to the steram grid. 0 = don't snap, 1 = snap                                   |
| BatchDone | Short integer | 0         | Identified whether or not the point has been processed by the Batch Waterhsed Delineation tool. 0 = unprocessed, 1 = processed |
| SrcType   | Short integer | 0         | Defines the point type. 0 = outlet, 1 = inlet                                                                                  |
| Name      | String        | XYCroCode | The unique ID assigned to the watershed                                                                                        |
| Descript  | String        | StrmName  | The description of the site                                                                                                    |

**Batch Watershed Delineation**

*Input*
Batch Point: crossings_delineation
Flow Direction Grid: fdr
Stream Grid: strFinal
Snap Stream Grid: strSnap50
Catchment: Catchment
Adjoint Catchment: AdjointCatchment
*Output*
Watershed: Watershed
Watershed Point: WatershedPoint


**Longest Flow Path**
*Input*
Drainage Area: Watersheds
Flow Direction Grid: fdr
*Output*
Longest Flow Path: LongestFlowPath

**Flow Path Parameters from 2D Line**
*Input*
Longest Flow Path:
Raw DEM:
*Output*
Slope 1085 Point: 



Post Processing

Run attributes script

Run zonal stats script

Run R script
