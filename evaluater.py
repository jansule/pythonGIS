# During the process multiple shapefiles will be generated
# At first, the original shapefile will be reprojected to fit the CRS of the DEM
# The output file will be stored in the location defined in 
# out_shp_dem
# Second, the reprojected shapefile will be reprojected again, to fit the CRS of the landcover file
# The output file will be stored in the location defined in 
# out_shp_land
# Additionally, a png file will be created that contains some visualizations of the data
# This file will be stored in the location defined in 
# out_png
# Please define their filenames in the following.
import os
import osr
import ogr
import gdal
import numpy as np
import math
from datetime import datetime
from matplotlib import pyplot as plt
################## USER INPUT REQUIRED ################################

# set base directory
data_dir = os.path.join('')

# set path to gpx shapefile
in_path_shp = os.path.join(data_dir, '')
# set path to landcover file (type should be .tif)
in_path_tif = os.path.join(data_dir, '')
# set path to DEM file (type should be .img)
in_path_dem = os.path.join(data_dir, '')

# allowed file type: .shp
out_shp_dem = os.path.join(data_dir, '')
# allowed file type: .shp
out_shp_land = os.path.join(data_dir, '')
# allowed file type: .png
out_png = os.path.join(data_dir, '')

######################### END USER INPUT REQUIRED ###########################



# set input reference system
input_ref = osr.SpatialReference()
input_ref.ImportFromEPSG(4326)

# set target reference system for DEM
target_ref_dem = osr.SpatialReference()
target_ref_dem.ImportFromEPSG(25832)

# set target reference system for landcover
target_ref_land = osr.SpatialReference()
target_ref_land.ImportFromEPSG(3035)

def reprojectShapefile(in_path_shp, out_path_shp, input_ref, target_ref):
    # open shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.Open(in_path_shp, 0)

    if shp is None:
        print 'could not open shp'
    else:
        print 'opened shp'
        layer = shp.GetLayer(0)
        spatRef = layer.GetSpatialRef()
        print 'spatial ref of {} is {}'.format(in_path_shp, spatRef)
        
        transform = osr.CoordinateTransformation(input_ref, target_ref)
        
        if os.path.exists(out_path_shp):
            print 'exists, deleting'
            driver.DeleteDataSource(out_path_shp)
        out_ds = driver.CreateDataSource(out_path_shp)
        if out_ds is None:
            print 'Could not create {}'.format(out_path_shp)
        
        out_lyr = out_ds.CreateLayer('test', target_ref, ogr.wkbPoint)
       
        out_lyr.CreateFields(layer.schema)
        out_defn = out_lyr.GetLayerDefn()
        out_feat = ogr.Feature(out_defn)
        for in_feat in layer:
            geom = in_feat.geometry()
            geom.Transform(transform)
            out_feat.SetGeometry(geom)
            for i in range(in_feat.GetFieldCount()):
                value = in_feat.GetField(i)
                out_feat.SetField(i, value)
            out_lyr.CreateFeature(out_feat)
        del out_ds
        print 'reprojected shapefile'
        # test if file has been reprojected correctly
        dr = ogr.GetDriverByName('ESRI Shapefile')
        shape = dr.Open(out_path_shp, 0)
        lyr = shape.GetLayer(0)
        print 'new spat ref {}'.format(lyr.GetSpatialRef())
        
def evalDem(in_path_shp, out_path_shp, input_ref, target_ref_dem, in_path_dem):
    # reproject shapefile
    reprojectShapefile(in_path_shp, out_path_shp, input_ref, target_ref_dem)
    # read DEM values
    raster = gdal.Open(in_path_dem)
    raster_band = raster.GetRasterBand(1)
    raster_spat = raster.GetProjection()
    print 'raster spat is {}'.format(raster_spat)
    geotransform = raster.GetGeoTransform()
    print 'geotransform: {}'.format(geotransform)
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.Open(out_path_shp, 1)
    layer = shp.GetLayer(0)
    print 'evalDem ref is {}'.format(layer.GetSpatialRef())
    dem_field_name = ogr.FieldDefn('DEM_elev', ogr.OFTString)
    layer.CreateField(dem_field_name)
    # add values to features
    for feat in layer:
        pt = feat.geometry()
        x = pt.GetX()
        y = pt.GetY()
        px = int((x - geotransform[0]) / geotransform[1])
        py = int((y - geotransform[3]) / geotransform[5])
        val_tmp = raster_band.ReadAsArray(px, py, 1, 1)
        val = float(val_tmp[0][0])
        feat.SetField('DEM_elev', val)
        layer.SetFeature(feat)
    del shp
        
def evalLand(in_path_shp, out_path_shp, input_ref, target_ref_dem, in_path_dem):
    # reproject shapefile
    reprojectShapefile(in_path_shp, out_path_shp, input_ref, target_ref_dem)
    # read DEM values
    raster = gdal.Open(in_path_dem)
    raster_band = raster.GetRasterBand(1)
    raster_spat = raster.GetProjection()
    print 'raster spat is {}'.format(raster_spat)
    geotransform = raster.GetGeoTransform()
    print 'geotransform: {}'.format(geotransform)
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.Open(out_path_shp, 1)
    layer = shp.GetLayer(0)
    print 'evalDem ref is {}'.format(layer.GetSpatialRef())
    dem_field_name = ogr.FieldDefn('Land_cov', ogr.OFTString)
    layer.CreateField(dem_field_name)
    # add values to features
    for feat in layer:
        pt = feat.geometry()
        x = pt.GetX()
        y = pt.GetY()
        px = int((x - geotransform[0]) / geotransform[1])
        py = int((y - geotransform[3]) / geotransform[5])
        val_tmp = raster_band.ReadAsArray(px, py, 1, 1)
        val = float(val_tmp[0][0])
        feat.SetField('Land_cov', val)
        layer.SetFeature(feat)
    del shp

def classify(in_path_shp):
    # set classes manually? so far its 2,3,18,29
    # open shp
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.Open(in_path_shp, 0)
    layer = shp.GetLayer(0)
    diffs = []
    land_cov_a = {}
    land_cov_a["2"] = []
    land_cov_a["3"] = []
    land_cov_a["18"] = []
    land_cov_a["29"] = []
    fmt = "%Y-%m-%d_%H-%M-%S"
    for feat in layer:
        dem_elev = float(feat.GetField('DEM_elev'))
        land_cov = int(feat.GetField('Land_cov'))
        gps_elev = float(feat.GetField('altitude'))
        timestamp = datetime.strptime(feat.GetField("date"), fmt)
        diff = abs(gps_elev - dem_elev)
        diffs.append({'diff': diff, 'land_cov': land_cov, 'timestamp': timestamp})
        land_cov_a[str(land_cov)].append(diff)
    del shp
    means = {}
    means["2"] = np.mean(land_cov_a['2'])
    means["3"] = np.mean(land_cov_a['3'])
    means["18"] = np.mean(land_cov_a['18'])
    means["29"] = np.mean(land_cov_a['29'])
    return {'diffs_per_feature': diffs, 'means_overall': means}

def visualize(data_obj, out_png):
    y = data_obj['means_overall']
    f, axarr = plt.subplots(2,1)
    if math.isnan(y['18']):
        bar1 = axarr[0].bar(1, y['2'], color='red')
        bar2 = axarr[0].bar(2, y['3'], color='purple')
        bar3 = axarr[0].bar(3, y['29'], color='brown')
        axarr[0].set_ylabel('Average elevation differences in meters')
        axarr[0].set_xlabel('Landcover types')
        axarr[0].set_xticks([])
    else:
        bar1 = axarr[0].bar(1, y['2'], color='red')
        bar2 = axarr[0].bar(2, y['3'], color='purple')
        bar3 = axarr[0].bar(3, y['18'], color='green')
        bar4 = axarr[0].bar(4, y['29'], color='brown')
        axarr[0].set_xticks([])
    axarr[0].set_title('Mean elevation differences of GPS and DEM by landcover types')
    axarr[0].set_ylabel('Elevation in [m]')
    axarr[0].set_xlabel('Landcover types')
    time = {}
    time["2"] = []
    time["3"] = []
    time["18"] = []
    time["29"] = []
    diffs = {}
    diffs["2"] = []
    diffs["3"] = []
    diffs["18"] = []
    diffs["29"] = []
    for feat in data_obj['diffs_per_feature']:
        time[str(feat['land_cov'])].append(feat['timestamp'])
        diffs[str(feat['land_cov'])].append(feat['diff'])
    if len(time["2"]) != 0: axarr[1].plot(time["2"], diffs["2"], color='red', marker='.', linestyle="", label="Discontinuous urban fabric")
    if len(time["3"]) != 0: axarr[1].plot(time["3"], diffs["3"], color='purple', marker='.', linestyle="", label="Industrial or commercial units")
    if len(time["18"]) != 0: axarr[1].plot(time["18"], diffs["18"], color='green', marker='.', linestyle="", label="Transitional woodland-shrub")
    if len(time["29"]) != 0: axarr[1].plot(time["29"], diffs["29"], color='brown', marker='.', linestyle="", label="Pastures")
    axarr[1].set_title('Timeseries of elevation differences of GPS and DEM')
    axarr[1].set_ylabel('Elevation in [m]')
    axarr[1].set_xlabel('Time')
    f.subplots_adjust(hspace = 0.5, bottom = 0.3)
    if math.isnan(float(y['18'])): 
        axarr[1].legend(loc=3, bbox_to_anchor=(0, -1.1))
    else: 
        axarr[1].legend(loc=3, bbox_to_anchor=(0, -1.3))

    plt.savefig(out_png, dpi=300, format='png')

# calling functions
evalDem(in_path_shp, out_shp_dem, input_ref, target_ref_dem, in_path_dem)
evalLand(out_shp_dem, out_shp_land, target_ref_dem, target_ref_land, in_path_tif)
classes = classify(out_shp_land)
visualize(classes, out_png)
print 'Evaluated all data successfully. Final shapefile is: {}. Created graph is: {}'.format(out_shp_land, out_png)