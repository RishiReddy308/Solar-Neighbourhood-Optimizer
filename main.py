# source https://open-meteo.com/en/docs?bounding_box=-90,-180,90,180&hourly=temperature_2m,shortwave_radiation
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

import plotly.express as px

def estimate_demand(row):
    date = row['date']
    temp = row['temperature_2m']
    return (temp - 18) * 0.

def solar_energy(row):
    rad = row['shortwave_radiation']
    return rad * 2




# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 43.47,
	"longitude": -79.41,
	"hourly": ["temperature_2m", "shortwave_radiation"],
}
responses = openmeteo.weather_api(url, params=params)

response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_shortwave_radiation = hourly.Variables(1).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["shortwave_radiation"] = hourly_shortwave_radiation

hourly_dataframe = pd.DataFrame(data = hourly_data)

hourly_dataframe["estimated demand"] = hourly_dataframe.apply(estimate_demand, axis = 1)

# Create the graph using Plotly 
fig = px.line(hourly_dataframe, x = 'date', y = 'shortwave_radiation', title = 'solar rad')
fig2 = px.line(hourly_dataframe, x = 'date', y = 'temperature_2m', title = 'temp')


f = open('index.html', 'w')

# write header
f.write("<html><head><title>Solar Dashboard</title></head><body>")

# write main title
f.write("<h1 style= 'text-align: center; '> Daily Solar & Temperature Forecast</h1>")

#write graphs
#cdn to draw the graphs
f.write(fig.to_html(full_html = False, include_plotlyjs = 'cdn'))
f.write(fig2.to_html(full_html = False, include_plotlyjs = 'cdn'))

f.write("</body></html>")
