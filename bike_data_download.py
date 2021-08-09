# Python Code to Pull Data
import json
import requests
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

# Import the API Key
# It is assumed that this is stored in the api_key folder
api_key = Path("api_key/key.txt").read_text()
api_key = api_key.replace('\n', '')

# Making a request for a station
station_query = 'https://api.jcdecaux.com/vls/v1/stations?contract=%(city)s&apiKey=%(key)s' % {'key': api_key, 'city': "dublin"}

# make the api request
r = requests.get(station_query)

# extract as json
response_json = r.json()

# Flatten the json file and store as data frame
df = pd.json_normalize(response_json, sep='_')

# Converting the timezones
df['last_update_utc']=(pd.to_datetime(df['last_update'],unit='ms')) 
df['last_update_local'] = df['last_update_utc'].dt.tz_localize('utc').dt.tz_convert('Europe/Dublin')

# Calculating the availability percentage
df['avail_percent'] = df['available_bikes'] / df['bike_stands']

# Saving data as a csv file
df.to_csv('bike_logging.csv', mode='a', header=False)
