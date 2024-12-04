#%%
# Importing necessary libraries
import pandas as pd  # For data manipulation and analysis
from prophet import Prophet  # For time series forecasting
from pathlib import Path  # For handling file paths
import os  # For interacting with the file system
import pooch  # For downloading and caching files

# Configure Pooch to manage the required files
BASE_URL = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/Data_EcoCompt_clean/"
pooch_data = pooch.create(
    path=pooch.os_cache("BikeProjectTeam7"),  # Local cache for the files
    base_url=BASE_URL,                       # Base URL to fetch the files
    registry={                               # File registry with its hash for verification
        "fichier_combined.csv": "840b3ceca9445ee9bbe55fd27be884f84d1acf827afbe6327dc007812d172b49"
    },
)

# Fetch and load the dataset
file_path = Path(pooch_data.fetch("fichier_combined.csv"))  # Download and fetch the file locally
data = pd.read_csv(file_path, sep=';')                     # Load the CSV data into a pandas DataFrame

# Convert the 'date' column to a datetime format
data['date'] = pd.to_datetime(data['date'])

# Filter the data for the period between April 1, 2023, and July 9, 2023
data = data[(data['date'] >= '2023-04-01') & (data['date'] <= '2023-07-09')]

# Initialize a dictionary to store predictions for each `laneId`
predictions_all_lanes = {}

# Loop through each `laneId` and forecast bike traffic
for lane_id, lane_data in data.groupby('laneId'):  # Group data by `laneId`
    # Prepare the data for Prophet: rename columns to 'ds' (date) and 'y' (intensity)
    lane_data = lane_data[['date', 'intensity']].rename(columns={'date': 'ds', 'intensity': 'y'})
    
    # Create and fit the Prophet model
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=True)  # Enable all seasonalities
    model.fit(lane_data)  # Train the model on the lane-specific data
    
    # Generate future dates for a 7-day forecast
    future = model.make_future_dataframe(periods=7)  # Add 7 days after July 9, 2023
    forecast = model.predict(future)  # Generate predictions
    
    # Extract relevant columns and filter forecasts for the period July 10–16, 2023
    forecast = forecast[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'predicted_intensity'})
    forecast = forecast[(forecast['date'] >= '2023-07-10') & (forecast['date'] <= '2023-07-16')]
    
    # Save the predictions for this `laneId` in the dictionary
    predictions_all_lanes[lane_id] = forecast[['date', 'predicted_intensity']].set_index('date')['predicted_intensity']

# Combine predictions for all `laneId`s into a single DataFrame
predictions_df = pd.DataFrame(predictions_all_lanes)

# Replace negative or missing values with None and interpolate to fill the gaps
predictions_df = predictions_df.applymap(lambda x: x if x >= 0 else None)  # Replace negative values
predictions_df.interpolate(method='linear', axis=0, inplace=True)  # Fill missing values using linear interpolation

# Reset the index to have the 'date' column instead of an index
predictions_df.reset_index(inplace=True)

# Save the results to a CSV file in the same directory as this script
current_dir = Path(__file__).resolve().parent  # Get the directory of the script
predictions_path = current_dir / 'predictions_bike_intensity_july_week.csv'  # Define the output file path
predictions_df.to_csv(predictions_path, index=False, sep=';')  # Save the predictions as a CSV file

# Print the location of the saved file
print(f"Predictions have been saved to: {predictions_path}")
