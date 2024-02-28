import requests
from datetime import datetime, timedelta


def get_coral():
    # 20,-24,89,172
    current_date = datetime.now()
    two = current_date - timedelta(days=2)
    date_two = two.strftime('%Y-%m-%d')
    link = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.nc?CRW_DHW%5B("+date_two+"T12:00:00Z):1:(2024-02-15T12:00:00Z)%5D%5B(-24.0):1:(20.0)%5D%5B(89.0):1:(172.0)%5D"
    response = requests.get(link)
    print(response)


get_coral()

