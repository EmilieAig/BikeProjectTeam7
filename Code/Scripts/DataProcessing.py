# %% Import packages 

import os
import numpy as np
import pandas as pd
import seaborn as sns
import pooch                    # download data / avoid re-downloading

# Seaborn configuration
sns.set_palette("colorblind")
palette = sns.color_palette("twilight", n_colors=12)
pd.options.display.max_rows = 8

# URL and file path
url = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/DataBike2023.csv"
path_target = "./DataBike2023.csv"
path, fname = os.path.split(path_target)

# Downloading data
known_hash = '81e2c763a0995e501cb6857160078331ac5a80cc165dd672abaf11c0f4d99d8f'
pooch.retrieve(url, path=path, fname=fname, known_hash=known_hash)

# Loading data
df_DataBike_raw = pd.read_csv(url, low_memory=False)
df_DataBike_raw = pd.read_csv(path_target, low_memory=False)
df_DataBike_raw.info()                  # Display data information
df_DataBike_raw.head(n=10)              # Display the first 10 lines


# %%

# Make sure that the ‘Departure’ column is in datetime format
df_DataBike_raw['Departure'] = pd.to_datetime(df_DataBike_raw['Departure'])

# Filter data from April (04) to October (10)
df_filtered = df_DataBike_raw[(df_DataBike_raw['Departure'].dt.month >= 4) & (df_DataBike_raw['Departure'].dt.month <= 10)]

# Display the information and the first 10 lines of the filtered DataFrame
df_filtered.info()
df_filtered.head(n=10)
