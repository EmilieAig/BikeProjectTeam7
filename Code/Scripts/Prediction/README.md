# Instructions for Bike Traffic Forecast Map (July 10-16, 2023)

Follow these steps to generate the bike traffic forecast map:

## Step 1: Generate Eco-comptage Coordinates
Run the file `code_eco_coord.py`.  
➡️ The file `ecocompteurs_coords.csv` will be saved in `Code/Data/Prediction_Data`.

## Step 2: Generate Weekly Predictions
Run the file `code_prediction_july.py`.  
➡️ The file `predictions_bike_intensity_july_week.csv` will be saved in `Code/Data/Prediction_Data`.

## Step 3: Convert Predictions to Long Format
Run the file `code_prediction_long_format_july.py`.  
➡️ The file `predictions_long_format_july.csv` will be saved in `Code/Data/Prediction_Data`.

## Step 4: Generate the Bike Traffic Prediction Map
Run the file `code_bike_traffic_prediction.py`.  
⚠️ **Note:** This code requires at least 1 hour to run.  
➡️ The map `bike_traffic_prediction_map.html` will be saved in `Code/Result`.
