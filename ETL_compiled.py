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
import gdown
import geopandas as gpd
import zipfile
import requests
from datetime import datetime, timedelta
import rasterio
from rasterio.transform import from_origin
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject, Resampling
import psycopg2
from shapely.wkt import dumps

desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
folder = 'GeoCoral'
new_folder_path = os.path.join(desktop, folder)
if not os.path.exists(new_folder_path):
    os.makedirs(new_folder_path)
    print(f"Folder '{folder}' created successfully at {desktop}")
else:
    print(f"Folder '{folder}' already exists at {desktop}")

def download_file_from_google_drive(file_id, dest_path):
    url = f'https://drive.google.com/uc?id={file_id}'
    gdown.download(url, dest_path, quiet=False)

def extract_zip(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

file_id = '1LNiRXvsiWqoUuGHSQduWBFjfsuy83Efs'
zip_destination = 'Corals.zip'
download_file_from_google_drive(file_id, zip_destination)
extraction_folder = new_folder_path
if not os.path.exists(extraction_folder):
    os.makedirs(extraction_folder)
extract_zip(zip_destination, extraction_folder)

#20,-24,89,172
current_date = datetime.now()
two = current_date - timedelta(days=6)
date_two = two.strftime('%Y-%m-%d')
link= "https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.nc?CRW_DHW%5B("+date_two+"T12:00:00Z):1:(2024-02-15T12:00:00Z)%5D%5B(-24.0):1:(20.0)%5D%5B(89.0):1:(172.0)%5D"
response = requests.get(link)
print(response)

# Opening NetCDF
dataset = xr.open_dataset(response.content)
sst = dataset['CRW_DHW'][0].values
lats = dataset['latitude'].values
lons = dataset['longitude'].values

# Create a Cartopy plot
plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.gridlines(draw_labels=True)
# Plotting DHW
cax = plt.pcolormesh(lons, lats, sst, shading='auto', cmap=cmocean.cm.thermal, transform=ccrs.PlateCarree())
plt.colorbar(cax, label='Degree Heat Week', orientation='horizontal', pad=0.06)

plt.title('Degree Heat Week')

min_value = dataset['latitude'].values
height, width = sst.shape

# Replace this with the actual bounding box you want
target_bbox = {
    'minx': 89,
    'miny': 64,
    'maxx': 172,
    'maxy': 20
}

tiff_name = new_folder_path+"/DHW_"+date_two+".tif"
print(tiff_name)
height, width = sst.shape

transform = from_origin(target_bbox['minx'], target_bbox['maxy'],
                        (target_bbox['maxx'] - target_bbox['minx']) / width,
                        (target_bbox['miny'] - target_bbox['maxy']) / height)

with rasterio.open(tiff_name, 'w', driver='GTiff', height=height, width=width, count=1,
                   dtype=str(sst.dtype), crs=4326, transform=transform) as dst:
    dst.write(sst, 1)

new_connection = psycopg2.connect(user = "postgres",
                                  password = "postgres", host = "localhost", port = "5432")
new_connection.autocommit = True
cursor = new_connection.cursor()

query = "CREATE DATABASE geocoral_c"
cursor.execute(query)

new_connection = psycopg2.connect(database='geocoral_c' ,user = "postgres",
                                  password = "postgres", host = "localhost", port = "5432")
new_connection.autocommit = True
cursor = new_connection.cursor()

table_query = """
CREATE TABLE IF NOT EXISTS corals (
    id SERIAL PRIMARY KEY,
    geometry GEOMETRY(Polygon, 4326) 
);
"""

new_connection.autocommit = True
cursor = new_connection.cursor()
cursor.execute(table_query)

shapefile_path = new_folder_path + '/Corals.geojson'
print(shapefile_path)
gdf = gpd.read_file(shapefile_path)
print(gdf)










