# %%
# Importing necessary libraries
import pandas as pd # For data manipulation and analysis
import pooch # For downloading and caching files
from pathlib import Path # For handling file paths

# Configure Pooch to manage necessary files 
BASE_URL = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/Data_EcoCompt_Combined//"
pooch_data = pooch.create(
    path=pooch.os_cache("BikeProjectTeam7"),  # Directory for cached files
    base_url=BASE_URL,                       # Base URL for dowlaoding files
    registry={                               # Files to manage with their SHA256 hashes
        "fichier_combined.csv": "840b3ceca9445ee9bbe55fd27be884f84d1acf827afbe6327dc007812d172b49"
    },
)

# Download and load the combined file
combined_file_path = pooch_data.fetch("fichier_combined.csv")  # Fetch or verify the file
combined_df = pd.read_csv(combined_file_path, sep=';')         # Load the data using pandas

# Extract the columns `laneId`, `latitude`, and `longitude`
coords_df = combined_df[['laneId', 'latitude', 'longitude']].drop_duplicates()

# Define the save path for the output file 'ecocompteurs_coords.csv'
current_folder = Path.cwd()
coords_file_path = current_folder / 'ecocompteurs_coords.csv'

# Save the extracted data into a CSV file
coords_df.to_csv(coords_file_path, index=False)

print(f"The file 'ecocompteurs_coords.csv' has been created in the folder {coords_file_path}.")

# %%
