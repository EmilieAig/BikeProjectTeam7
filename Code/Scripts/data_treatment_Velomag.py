# %% 1. Import packages

import pooch
import pandas as pd
import numpy as np

# %% 2. Define the URL and download

# URL where the file is hosted 
url = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/DataBike2023.csv"

# Compute or provide the known SHA256 hash of the file  
known_hash = "81e2c763a0995e501cb6857160078331ac5a80cc165dd672abaf11c0f4d99d8f"

# Local directory to cache the downloaded file 
cache_dir = pooch.os_cache("my_data_cache")

# Download the file with `pooch` (it will be cached locally)  
dataset = pooch.retrieve(url, path=cache_dir, downloader=pooch.HTTPDownloader(), known_hash=known_hash)

# Load the downloaded CSV file into a DataFrame 
df = pd.read_csv(dataset, encoding='utf-8', low_memory=False)

# %% 3. Clean the dataset

# Clean column names (strip spaces, remove special characters) 
df.columns = df.columns.str.strip().str.replace('°', 'C').str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

# Function to clean special characters in the dataset  
def clean_text(text):
    return str(text).replace('√©', 'e') \
                     .replace('√®', 'e') \
                     .replace('√†', 'a') \
                     .replace('√ç', 'c')

# Apply the cleaning function to all DataFrame cells 
df = df.applymap(clean_text)

# %% 4. Process date and time columns

# Split the 'Departure' column into two: one for the date and another for the time  
df[['Departure_Date', 'Departure_Time']] = df['Departure'].str.split(' ', expand=True)

# Split the 'Return' column into two: one for the date and another for the time 
df[['Return_Date', 'Return_Time']] = df['Return'].str.split(' ', expand=True)

# Convert date and time columns into DateTime format 
df['Departure_DateTime'] = pd.to_datetime(df['Departure_Date'] + ' ' + df['Departure_Time'])
df['Return_DateTime'] = pd.to_datetime(df['Return_Date'] + ' ' + df['Return_Time'])

# %% 5. Remove unnecessary columns

# Remove columns that are no longer needed 
df = df.drop(['Departure', 'Return', 'Departure_DateTime', 'Return_DateTime', 'Lock_duration_sec.', 'Number_of_bike_locks', 'Manager', 'new_account'], axis=1)

# %% 6.  Generate random latitude and longitude data (to fill in the columns, but which will be replaced by the real data afterwards)

# Latitude range near 43.61 (from 43.55 to 43.67 to stay close)
latitudes_dep = np.random.uniform(43.55, 43.67, len(df))

# Longitude range near 3.88 (from 3.82 to 3.93 to stay close)
longitudes_dep = np.random.uniform(3.82, 3.93, len(df))

# Latitude range near 43.61 (from 43.55 to 43.67 to stay close)
latitudes_ret = np.random.uniform(43.55, 43.67, len(df))

# Longitude range near 3.88 (from 3.82 to 3.93 to stay close) 
longitudes_ret = np.random.uniform(3.82, 3.93, len(df))

# Add Latitude and Longitude columns to the DataFrame 
df['Departure latitude'] = latitudes_dep
df['Departure longitude'] = longitudes_dep
df['Return latitude'] = latitudes_ret
df['Return longitude'] = longitudes_ret

# %% 7. Save the cleaned dataset

# Save the cleaned DataFrame to a CSV file  
df.to_csv('cleaned_data.csv', index=False, encoding='utf-8')

print("Les données ont été nettoyées et enregistrées dans 'cleaned_data.csv'.")
