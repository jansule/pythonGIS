# pythonGIS
Final Assignment for Python in GIS

## Prerequisites

 - QGIS Desktop 2.8 or higher
 - tested on Python 2.7.12

 ## Installing

 1. Download or clone this repository and if necessary unzip all files.
 2. Download Landcover image (this script has been tested with and optimized for [g100_clc12_V18_5.tif](http://land.copernicus.eu/pan-european/corine-land-cover/clc-2012/view))
 3. Download DEM (this script has been tested with and optimized for `dgm1_5meter.img`. This file was provided within the course)
 
**Note:** Two of three of the provided shapefiles are missing a projection. Therefore the `.prj` of the third shapefile needs to be duplicated twice and renamed according to the filenames of the other shapefiles. 

 ## How to run

 1. Open evaluater.py in a text editor
 2. Add paths to input and output files in lines 23-37 (description of allowed types and variable definitions is given within evaluater.py)
 3. Open QGIS
 4. Open `Python Console` in QGIS
 5. Click on `Show Editor` in `Python Console`
 6. Click on `Open File` in `Editor` and select `evaluater.py`
 7. Click on `Run Script` in `Editor`

 ## Results

 The script creates three outputs:
 
1. reprojected shapefile with CRS of DEM and added field `DEM_elev`
2. reprojected shapefile with CRS of Landcover file and added field `Land_cov`
3. png file containing 
    1. bar chart of elevation differences between GPS and DEM elevation, classified in landcover types
    2. time series of elevation differences between GPS and DEM elevation, classified in landcover types

Example .png outputs have been added to this repository 