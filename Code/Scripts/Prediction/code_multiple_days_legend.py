#%%
# Importing necessary libraries
import pandas as pd # Manipulation of data in tabular form (DataFrames)
import folium # Creation of interactive maps
import osmnx as ox # Downloading and manipulating OpenStreetMap data, particularly road networks
from geopy.distance import geodesic # Calculation of geographical distances between two points
from folium import LayerControl # Managing layers on a Folium map
from tqdm import tqdm # Displaying a progress bar in loops
import pooch # For downloading and caching files
import os # For interacting with the file system

# Function to download files using Pooch
def download_file(url, target_path, known_hash):
    """
    Downloads a file from a URL and verifies its integrity using a SHA256 hash.
    
    Args:
        url (str): The file's URL.
        target_path (str): The local path where the file will be saved.
        known_hash (str): The expected SHA256 hash of the file.
        
    Returns:
        str: The path where the downloaded file is stored.
    """
    path, fname = os.path.split(target_path)
    return pooch.retrieve(url=url, fname=fname, path=path, known_hash=known_hash)

# File URLs and their respective hash values
files_info = {
    "ecocompteur_file": {
        "url": "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Scripts/Prediction/ecocompteurs_coords.csv",
        "target_path": "./data/ecocompteurs_coords.csv",
        "known_hash": "08c71a1718b279efe1ebb60f6446e19c8b786d93a2a16bcb8504ab1a888dc3f8"  # SHA256 hash of ecocompteurs_coords.csv
    },
    "predictions_file": {
        "url": "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Scripts/Prediction/predictions_long_format_july.csv",
        "target_path": "./data/predictions_long_format_july.csv",
        "known_hash": "1c57f8aae4ef6eb940319776a9b66e7a1d3731fa1b5f2cced8493fa27928bf42"
    },
    "stations_file": {
        "url": "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/Video_Data/GeolocalisationStation.csv",
        "target_path": "./GeolocalisationStation.csv",
        "known_hash": "9638579e4d6e416196bd2ed7c7c0b9f9bc1d5a39e7a9ca6e5d45336c02ad3ab6"
    },
}

# Download the necessary files
for key, info in files_info.items():
    print(f"Downloading {key}...")
    files_info[key]["local_path"] = download_file(
        url=info["url"],
        target_path=info["target_path"],
        known_hash=info["known_hash"]
    )

# Load the downloaded files
ecocompteur_file = files_info["ecocompteur_file"]["local_path"]
predictions_file = files_info["predictions_file"]["local_path"]
stations_file = files_info["stations_file"]["local_path"]

# Read and process the downloaded data
ecocompteur = pd.read_csv(ecocompteur_file, sep=',')
ecocompteur.rename(columns=lambda x: x.strip(), inplace=True)
ecocompteur.rename(columns={"LaneID": "laneId"}, inplace=True)

predictions = pd.read_csv(predictions_file, sep=';')
predictions['date'] = pd.to_datetime(predictions['date'])

stations = pd.read_csv(stations_file)

# Select data for the period between July 10th and 16th, 2023
dates_of_interest = pd.date_range('2023-07-10', '2023-07-16')
predictions_filtered = predictions[predictions['date'].isin(dates_of_interest)]

# Merge the predictions with the eco-compteur coordinates based on laneId
merged_data = pd.merge(ecocompteur, predictions_filtered, on='laneId', how='inner')

# Filter points within a 15 km radius of Montpellier
map_center = [43.6117, 3.8777]
radius_km = 15

# Function to check if a point is within the specified radius
def is_within_radius(lat, lon, center, radius):
    return geodesic(center, (lat, lon)).km <= radius

# Apply the radius filter to the merged data
merged_data['within_radius'] = merged_data.apply(
    lambda row: is_within_radius(row['latitude'], row['longitude'], map_center, radius_km),
    axis=1
)
merged_data = merged_data[merged_data['within_radius']]

# Reload the stations file (to ensure it's available)
stations = pd.read_csv(stations_file)

# Function to find the nearest station name based on coordinates
def find_station_name(lat, lon, stations):
    stations_copy = stations.copy()
    stations_copy['distance'] = stations_copy.apply(
        lambda row: geodesic((lat, lon), (row['Latitude'], row['Longitude'])).km,
        axis=1
    )
    closest_station = stations_copy.loc[stations_copy['distance'].idxmin()]
    return closest_station['Station']

# Apply the station name assignment to the merged data
merged_data['station_name'] = merged_data.apply(
    lambda row: find_station_name(row['latitude'], row['longitude'], stations),
    axis=1
)

# Download a bike-friendly road graph around Montpellier
print("Downloading road graph from OSM...")
graph = ox.graph_from_point(map_center, dist=radius_km * 1000, network_type='bike', simplify=True)

# Function to safely retrieve the nearest node in the road graph for a given point
def safe_nearest_node(graph, x, y):
    try:
        return ox.distance.nearest_nodes(graph, X=x, Y=y)
    except Exception as e:
        print(f"Error for coordinates ({y}, {x}): {e}")
        return None

# Apply the nearest node association to the merged data
print("Associating points with OSM nodes...")
merged_data['osmid'] = merged_data.apply(
    lambda row: safe_nearest_node(graph, row['longitude'], row['latitude']),
    axis=1
)

# Remove points that couldn't be associated with a node
merged_data.dropna(subset=['osmid'], inplace=True)

# Create a Folium map centered around Montpellier
m = folium.Map(location=map_center, zoom_start=13)

# Add a legend for intensity levels
legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; width: 300px; height: 180px; 
    background-color: white; z-index:9999; font-size:14px;
    border:2px solid grey; border-radius:5px; padding: 10px;">
    <b>Intensity Legend</b><br>
    <i style="background:#FE4528; width:15px; height:15px; display:inline-block;"></i> > 1500 (High Intensity)<br>
    <i style="background:#FD6121; width:15px; height:15px; display:inline-block;"></i> > 1200<br>
    <i style="background:#D95018; width:15px; height:15px; display:inline-block;"></i> > 900<br>
    <i style="background:#FFEF3A; width:15px; height:15px; display:inline-block;"></i> > 600<br>
    <i style="background:#6CD932; width:15px; height:15px; display:inline-block;"></i> >= 300<br>
    <i style="background:#038C05; width:15px; height:15px; display:inline-block;"></i> < 300 (Low Intensity)<br>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Function to create a layer for each selected date, adding connected paths and station names to the map
def create_layer_for_date(date, graph, merged_data):
    day_data = merged_data[merged_data['date'] == date]
    feature_group = folium.FeatureGroup(name=f"{date.strftime('%Y-%m-%d')}")

    # Add paths between connected points with color-coded intensity
    for i, row1 in tqdm(day_data.iterrows(), total=len(day_data), desc=f"Processing {date}"):
        for j, row2 in day_data.iterrows():
            if i >= j:
                continue
            
            osmid1 = row1['osmid']
            osmid2 = row2['osmid']
            intensity = (row1['predicted_intensity'] + row2['predicted_intensity']) / 2  # Average intensity

            # Determine path color based on intensity
            if intensity > 1500:
                color = '#FE4528'  # Red
            elif intensity > 1200:
                color = '#FD6121'  # Orange
            elif intensity > 900:
                color = '#D95018'  # Light Orange
            elif intensity > 600:
                color = '#FFEF3A'  # Yellow
            elif intensity > 300:
                color = '#6CD932'  # Light Green
            else:
                color = '#038C05'  # Dark Green
            
            try:
                shortest_path = ox.shortest_path(graph, osmid1, osmid2, weight='length')
                if shortest_path:
                    path_coords = [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in shortest_path]
                    folium.PolyLine(path_coords, color=color, weight=4, opacity=0.6).add_to(feature_group)
            except Exception as e:
                print(f"Error while creating path for nodes {osmid1} and {osmid2}: {e}")

    # Add station names and intensity markers
    for _, row in day_data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Station: {row['station_name']}<br>Intensity: {row['predicted_intensity']}",
            icon=folium.Icon(color="blue")
        ).add_to(feature_group)
    
    feature_group.add_to(m)

# Create layers for each date in the filtered predictions
for date in dates_of_interest:
    create_layer_for_date(date, graph, merged_data)

# Add layer control to toggle between date layers
LayerControl().add_to(m)

# Save the map to an HTML file
map_file = "bike_traffic_prediction_map"
m.save(map_file)
print(f"Map saved as {map_file}")
