#%%
# Importing necessary libraries
import pandas as pd # For data manipulation and analysis
import pooch # For downloading and caching files
from pathlib import Path # For handling file paths

# Configure Pooch to manage the necessary files
BASE_URL = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/Prediction_Data/"
pooch_data = pooch.create(
    path=pooch.os_cache("BikeProjectTeam7"),  # Cache for downloaded files
    base_url=BASE_URL,                       # Base URL for files
    registry={                               # Files to manage with their SHA256 hashes
        "predictions_bike_intensity_july_week.csv": "6a384fa7960da607f14b5dbee0241783b8e8c510a971a8c7439a2a587449e53b"
    },
)

# Define the output directory for the saved files
output_dir = Path(__file__).resolve().parents[2] / 'Data' / 'Prediction_Data'  # Going 2 levels up from the script location to reach the root 'Code'
output_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

# Download and load the predictions file
data_path = pooch_data.fetch("predictions_bike_intensity_july_week.csv")  # Fetch or verify the file
predictions_df = pd.read_csv(data_path, sep=';')

# Series of replacement values for missing data in '253757735'
replacement_values = [
    461.34576511247957, 562.0277158350742, 543.6324160701633, 537.5385273355084,
    401.0681366893027, 245.31856472538269, 168.9334585514308
]

# Identify indices with missing values in the '253757735' column
missing_indices = predictions_df[predictions_df['253757735'].isna()].index

# Replace missing values with the specific values
for idx, value in zip(missing_indices, replacement_values):
    predictions_df.at[idx, '253757735'] = value

# Transform the data into a long format
melted_df = pd.melt(predictions_df, id_vars=['date'], var_name='laneId', value_name='predicted_intensity')

# Convert the date column to datetime format
melted_df['date'] = pd.to_datetime(melted_df['date'])

# Define the output path relative to the Prediction_Data directory
output_path = output_dir / 'predictions_long_format_july.csv'  # Save the file in Prediction_Data

# Save the results to a CSV file in the 'Prediction_Data' directory
melted_df.to_csv(output_path, index=False, sep=';')  # Save the transformed data as a CSV file

print(f"Transformation complete and saved to '{output_path}'.")

# %%
