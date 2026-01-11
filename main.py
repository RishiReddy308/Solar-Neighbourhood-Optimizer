# source https://open-meteo.com/en/docs?bounding_box=-90,-180,90,180&hourly=temperature_2m,shortwave_radiation
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

import plotly.express as px

def excess_energy(row):
    return row['Solar Energy'] - row['Estimated Demand']

def solar_energy_output(row):
    rad = row['Shortwave Radiation']
    effiency = 0.2
    coverage = 30.0 #m^2

    return (rad / 1000) * effiency * coverage


def estimate_demand(row):
    hour = row['date'].hour
    day_of_week = row['date'].dayofweek
    outside_temp = row['Temperature']
    target_temp = 21.0 #celcius
    base_demand = 0.3   #kwh always used by home
    hvac_demand = 0.0
    
    temp_diff = outside_temp - target_temp

    #cooling
    if temp_diff > 0:
        hvac_demand = temp_diff * 0.08

    #heating
    elif temp_diff < 0:
        hvac_demand = abs(temp_diff) * 0.01

    #weekends
    if day_of_week >= 5:
        #waking up energy use
        if 9 <= hour <= 11: 
            base_demand += 0.8
        #casual energy use
        elif 12 <= hour <= 17:
            base_demand += 0.6 
        #evening use
        elif 18 <= hour <= 23:
            base_demand += 1.8

    #weekdays
    else:
        #mornings
        if 7 <= hour <= 8:
            base_demand += 1.0
        # no one is home at this time
        elif 9 <= hour <= 16:
            base_demand += 0.0 
        # Evenings
        elif 17 <= hour <= 22:
            base_demand += 1.5

        
    return hvac_demand + base_demand
    



# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
    #milton  43.47, -79.87
    #aus    25.27,79.87
	"latitude": 43.47,
	"longitude": -79.87,
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

hourly_data["Temperature"] = hourly_temperature_2m
hourly_data["Shortwave Radiation"] = hourly_shortwave_radiation

hourly_dataframe = pd.DataFrame(data = hourly_data)

hourly_dataframe["Estimated Demand"] = hourly_dataframe.apply(estimate_demand, axis = 1)
hourly_dataframe["Solar Energy"] = hourly_dataframe.apply(solar_energy_output, axis = 1)
hourly_dataframe["Excess"] = hourly_dataframe.apply(excess_energy, axis = 1)

print("\nHourly data\n", hourly_dataframe)



# Create the graph using Plotly 
fig = px.bar(hourly_dataframe, x = 'date', y = 'Excess', title = 'Net Energy (Produced - Demand)',labels={'Excess': 'Energy (kWh)'}, color='Excess', color_continuous_scale='RdYlGn')
fig.add_hline(y=0, line_dash="solid", line_color="black")
fig2 = px.line(hourly_dataframe, x = 'date', y = ['Solar Energy','Estimated Demand'], title = 'Solar Energy and House Demand',labels={'value': 'Energy (kWh)', 'variable': 'Source'})
fig2.add_hline(y=0, line_dash="solid", line_color="black")

f = open('index.html', 'w')

# write header
f.write("<html><head><title>Solar Dashboard</title></head><body>")

# write main title
f.write("<h1 style= 'text-align: center; '> Excess Energy From Solar Panels Forecast</h1>")
f.write("<h1 style= 'text-align: center; '> Best Time to Use Electricity</h1>")


#write graphs
#cdn to draw the graphs
f.write(fig.to_html(full_html = False, include_plotlyjs = 'cdn'))
f.write(fig2.to_html(full_html = False, include_plotlyjs = 'cdn'))

f.write("</body></html>")

print("done")
