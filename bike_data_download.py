#!/usr/bin/env python3

# Python Code to Pull Data
import json
import requests
from pathlib import Path
import pandas as pd
import datetime
import os
import time

# Import the API Key
# It is assumed that this is stored in the api_key folder
api_key = Path("api_key/key.txt").read_text()
api_key = api_key.replace('\n', '')

# Function to check if time in a certain range
# Dublin bikes are only available between 05:00 to 00:30 
def time_in_range(start, end, x):
    # Return true if x is in the range [start, end]
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def getLiveData():
    try:
        # Making a request for a station
        station_query = 'https://api.jcdecaux.com/vls/v1/stations?contract=%(city)s&apiKey=%(key)s' % {'key': api_key, 'city': "dublin"}
        
        # make the api request
        r = requests.get(station_query)
        
        # extract as json
        response_json = r.json()
        
        # Flatten the json file and store as data frame
        df = pd.json_normalize(response_json, sep='_')

        # Add current time zone
        df['run_datetime_local'] = pd.Timestamp.utcnow().tz_convert('Europe/Dublin')

        # Converting the timezones
        df['last_update_utc']=(pd.to_datetime(df['last_update'],unit='ms')) 
        df['last_update_local'] = df['last_update_utc'].dt.tz_localize('utc').dt.tz_convert('Europe/Dublin')

        # Calculating the availability percentage
        df['avail_percent'] = df['available_bikes'] / df['bike_stands']

    except:
        print("Failed to download data")
        return None
    return df

# Downloading the API data every 10 minutes
i=0
start = datetime.time(5, 0, 0)
end = datetime.time(00, 30, 0)

while True:

    if time_in_range(start, end, datetime.datetime.now().time()):
        df=getLiveData()
        df.insert(0, 'request_number', i)

        if df.empty:
            print('Data frame is empty')
        else:
            # Saving data as a csv file    
            if os.path.exists('data/bike_logging1.csv') == False:
                df.to_csv('data/bike_logging1.csv', mode='a', header=True, index=False)
            else:
                df.to_csv('data/bike_logging1.csv', mode='a', header=False, index=False)

    else:
        print("Stations are closed")

    print("Sleeping for 10 minutes")
    i+=1
    time.sleep(600)


