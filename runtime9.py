import requests
import xarray as xr
import matplotlib.pyplot as plt
import cmocean
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime, timedelta
import geopandas
from shapely.geometry import box
import netCDF4 as nc
import os
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject, Resampling
import fiona
import packaging
import numpy
import pandas
import scipy

# I placed a user feedback list over here so that after running the ask_coord, the response will be appended
# to this list and the other functions can have access to it.
user_feedback = []

def ask_coord():
    user_datee = input("Please enter a date (YYYY-MM-DD): ")
    print("You entered:", user_datee)
    user_date = str(user_datee)
    # Asking for coordinates
    user_coordinates = input(
        "Please enter coordinates for the bbox (latitude up ,latitude low , longitude left ,longitude right ): ")
    latitudee_A, latitudee_B, longitudee_A, longitudee_B = map(float, user_coordinates.split(','))
    latitude_A = str(latitudee_A)
    latitude_B = str(latitudee_B)
    longitude_A = str(longitudee_A)
    longitude_B = str(longitudee_B)
    print("Latitude:", latitude_A, latitude_B)
    print("Longitude:", longitude_A, longitude_B)
    patricio = os.path.join(
        "https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.nc?CRW_DHW%5B(" + user_date + "T12:00:00Z):1:(" + user_date + "T12:00:00Z)%5D%5B(" + latitude_B + "):1:(" + latitude_A + ")%5D%5B(" + longitude_A + "):1:(" + longitude_B + ")%5D")
    print(patricio)
    response = requests.get(patricio)
    print(response)
    user_feedback.append(response)


# You have to pass the ask_coord function into this function for
def open_netcdf():
    dataset = xr.open_dataset(user_feedback[0].content)
    # Extract relevant data
    sst = dataset['CRW_DHW'][0].values
    lats = dataset['latitude'].values
    lons = dataset['longitude'].values

    # Create a Cartopy plot
    plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.gridlines(draw_labels=True)
    # crs = CRS.from_epsg(32651)
    # Plot sea surface temperature
    cax = plt.pcolormesh(lons, lats, sst, shading='auto', cmap=cmocean.cm.thermal, transform=ccrs.PlateCarree())
    plt.colorbar(cax, label='Degree Heat Week', orientation='horizontal', pad=0.06)

    plt.title('Degree Heat Week')


# Setting the boundary box
def set_boundary():
    # I needed to define the sst in this function so i created the dataset variable again in this function
    dataset = xr.open_dataset(user_feedback[0].content)
    # Extract relevant data
    sst = dataset['CRW_DHW'][0].values
    # Replace this with the actual bounding box you want
    target_bbox = {
        'minx': 80,
        'miny': -24,
        'maxx': 172,
        'maxy': 20
    }

    tiff_path = '/Users/alonso.gonzalez.glez/Desktop/Boundaries/chaqueton_1.tif'
    phi = '/Users/alonso.gonzalez.glez/Desktop/Boundaries/Chichita.shp'
    phil = gpd.read_file(phi)

    # Get the variables here from the Numpy array
    height, width = sst.shape

    # Calculate the transform based on the target bounding box
    transform = from_origin(target_bbox['minx'], target_bbox['maxy'],
                            (target_bbox['maxx'] - target_bbox['minx']) / width,
                            (target_bbox['miny'] - target_bbox['maxy']) / height)

    # Write the GeoTIFF with the specified bounding box
    with rasterio.open(tiff_path, 'w', driver='GTiff', height=height, width=width, count=1,
                       dtype=str(sst.dtype), crs=4326, transform=transform) as dst:
        # Write the data array to the GeoTIFF
        dst.write(sst, 1)

def shapes():
    # I also had to redefine the dataset here
    dataset = xr.open_dataset(user_feedback[0].content)
    with fiona.open("/Users/alonso.gonzalez.glez/Desktop/Boundaries/Clone.shp", "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]

    with rasterio.open("/Users/alonso.gonzalez.glez/Desktop/Boundaries/phil_1.tif") as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta
        lats = dataset['latitude'].values
        lons = dataset['longitude'].values

        print(lats)


# Running the functions one by one
ask_coord()
print(user_feedback)
open_netcdf()
set_boundary()
shapes()
