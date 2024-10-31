# %% Import packages

import json
import pandas as pd
from datetime import datetime
import os
import glob

# %% Conversion and selection of data 

def convert_json_to_csv(input_file, output_dir):
    # Create output file name in data_clean folder
    input_filename = os.path.basename(input_file)
    output_filename = input_filename.replace('.json', '.csv')
    output_file = os.path.join(output_dir, output_filename)
    
    # Read file and store data
    data_list = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            for line in file:
                # Ignore empty lines
                if line.strip():
                    try:
                        # Load JSON object
                        json_obj = json.loads(line.strip())
                        
                        # Extract coordinates
                        longitude = json_obj['location']['coordinates'][0]
                        latitude = json_obj['location']['coordinates'][1]
                        
                        # Extract date (first part of dateObserved)
                        date = json_obj['dateObserved'].split('T')[0]
                        
                        # Creating a flattened dictionary
                        flat_data = {
                            'intensity': json_obj['intensity'],
                            'laneId': json_obj['laneId'],
                            'date': date,
                            'longitude': longitude,
                            'latitude': latitude,
                            'id': json_obj['id'],
                            'type': json_obj['type'],
                            'vehicleType': json_obj['vehicleType'],
                            'reversedLane': json_obj['reversedLane']
                        }
                        data_list.append(flat_data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding a line in {input_filename}")
                        print(f"Error : {e}")
                        continue
        
        # If no data was found, raise an exception
        if not data_list:
            raise ValueError("No valid data found in the file")
        
        # Convert to DataFrame pandas
        df = pd.DataFrame(data_list)
        
        # Convert date column to datetime format
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter data for April-October 2023
        mask = (df['date'] >= '2023-04-01') & (df['date'] <= '2023-10-31')
        df_filtered = df.loc[mask]
        
        # Sort by date
        df_filtered = df_filtered.sort_values('date')
        
        # Convert date back to string format YYYY-MM-DD for CSV
        df_filtered['date'] = df_filtered['date'].dt.strftime('%Y-%m-%d')
        
        # Save as CSV with explicit parameters
        df_filtered.to_csv(output_file, 
                          index=False,
                          sep=';',
                          encoding='utf-8-sig',
                          float_format='%.6f')
        
        print(f"\nSuccessful conversion: {input_filename} -> {output_filename}")
        print(f"Number of recordings: {len(df_filtered)}")
        print(f"Period: from {df_filtered['date'].min()} to {df_filtered['date'].max()}")
        
        return True
        
    except Exception as e:
        print(f"\nError when processing {input_filename}")
        print(f"Error: {str(e)}")
        return False

# %% Detection of file to analyse and folder to save data clean

def process_all_json_files():
    # Define folder paths
    current_directory = os.getcwd()
    input_dir = os.path.join(current_directory, 'data')
    output_dir = os.path.join(current_directory, 'data_clean')
    
    # Check if the entry file exists
    if not os.path.exists(input_dir):
        print(f"Error: folder 'data' doesn't exists in {current_directory}")
        return
    
    # Create output folder if none exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Folder 'data_clean' created in {current_directory}")
    
    # Search for all .json files in the data folder
    json_files = glob.glob(os.path.join(input_dir, '*.json'))
    
    if not json_files:
        print("No .json files found in the 'data' folder.")
        return
    
    print(f"Number of .json files found: {len(json_files)}")
    
    # Report counters
    success_count = 0
    error_count = 0
    
    # Process each file
    for json_file in json_files:
        print(f"\nTreatment of: {os.path.basename(json_file)}")
        if convert_json_to_csv(json_file, output_dir):
            success_count += 1
        else:
            error_count += 1
    
    # View final report
    print("\n=== Conversion report ===")
    print(f"Files successfully processed: {success_count}")
    print(f"Files with errors: {error_count}")
    print(f"Total files: {len(json_files)}")
    print(f"\nThe CSV files have been saved in: {output_dir}")

# %% Run the treatment

if __name__ == "__main__":
    print("Start processing JSON files...")
    process_all_json_files()
    print("\nTreatment completed.")