# %% Extract coordinates of counters

import pandas as pd
import os
# File path setup
data_folder = os.path.join("..", "Data", "Data_EcoCompt_Combined")  # Path to the data folder
file_path = os.path.join(data_folder, "fichier_combined.csv")  # File path

# Read the CSV file
df = pd.read_csv(file_path, delimiter=";")  

# Extract base IDs of counters
df['counter_id'] = df['id'].str.extract(r'(MMM_EcoCompt_\w+?)_')  

# Extract unique counter IDs and coordinates
unique_counters = df[['counter_id', 'longitude', 'latitude']].drop_duplicates()

# Display the first few rows of the extracted results
print(unique_counters.head())

# Save the results to a new CSV file
output_folder = data_folder  # Save to the same directory
output_path = os.path.join(output_folder, "counter_coordinates.csv")
unique_counters.to_csv(output_path, index=False)

print(f"Counter data has been extracted and saved to:{output_path}")




# %% Extract the network graph, select the appropriate range, and filter based on road types to retain suitable road density

import osmnx as ox
ox.settings.use_cache=True
ox.__version__
import osmnx as ox
import networkx as nx
from shapely.geometry import Point

# Define the center point and radius
center_point = (43.606, 3.877)  # (latitude, longitude)
radius = 9280  # Radius: 9.28 kilometers, unit in meters

# 1. Create a circular polygon
center = Point(center_point[1], center_point[0])  # Coordinates are in the format (lon, lat)
circle = center.buffer(radius / 111320)  # Use an approximate conversion of 1° latitude = 111.32 km

# 2. Extract the bicycle network within the circular area
G = ox.graph_from_polygon(circle, network_type='bike')


# Define the road types to retain
desired_highways = {'primary', 'trunk', 'secondary', 'tertiary', 'secondary_link', 'trunk_link', 'primary_link', 'tertiary_link', 'living_street',  'bridleway'}

# Iterate through the edges in the graph and apply filters
edges_to_remove = []
for u, v, key, data in G.edges(keys=True, data=True):
    highway = data.get('highway', None)
    if isinstance(highway, list):
        # If 'highway' is a list, check for intersections with 'desired_highways'
        if not any(h in desired_highways for h in highway):
            edges_to_remove.append((u, v, key))
    elif highway not in desired_highways:
        # If 'highway' is a single value, directly check if it's in 'desired_highways'
        edges_to_remove.append((u, v, key))

# Remove unwanted edges
G.remove_edges_from(edges_to_remove)

# Remove isolated nodes
isolated_nodes = list(nx.isolates(G))  # Identify all isolated nodes
G.remove_nodes_from(isolated_nodes)  # Remove isolated nodes

# Remove some isolated and scattered roads
# 1. Identify all connected components in the network
connected_components = nx.connected_components(G.to_undirected())

# 2. Identify the largest connected component
largest_cc = max(connected_components, key=len)

# 3. Create a subgraph containing the largest connected component
G_largest = G.subgraph(largest_cc).copy()

# 4. Output the number of nodes and edges after cleaning
print(f"After cleaning, the network contains {G_largest.number_of_nodes()} nodes and {G_largest.number_of_edges()} edges.")

# Update the original graph
G = G_largest

# Visualize the network
print(f"nb edges: {G.number_of_edges()}")
print(f"nb nodes: {G.number_of_nodes()}")
fig, ax = ox.plot_graph(G)




# %% Match the counter coordinates with the network node coordinates

import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt

# 1. Read the counter data
counter_file_path = "../Data/Data_EcoCompt_Combined/counter_coordinates.csv"
counters = pd.read_csv(counter_file_path)

# 2. Remove counters that are too far away (counter_id = MMM_EcoCompt_X2H22104765)
counters = counters[counters['counter_id'] != 'MMM_EcoCompt_X2H22104765']

# 3. Find the nearest network nodes
counters['nearest_node'] = counters.apply(
    lambda row: ox.nearest_nodes(G, row['longitude'], row['latitude']), axis=1
)

# 4. Retrieve the coordinates of the nearest nodes
nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
counters['node_longitude'] = counters['nearest_node'].map(nodes['x'])
counters['node_latitude'] = counters['nearest_node'].map(nodes['y'])

# 5. Visualize the network and mark the nodes
fig, ax = ox.plot_graph(G, show=False, close=False)

# 6. Plot the positions of the nearest nodes (marked in red)
nearest_positions = counters[['node_longitude', 'node_latitude']].values
ax.scatter(nearest_positions[:, 0], nearest_positions[:, 1], c='red', s=50, label='Nearest Nodes')

# Add a legend and display
ax.legend()
plt.show()




# %% Select the desired dates and match each counter node with intensity

import pandas as pd
import os

# File path setup
combined_file_path = "../Data/Data_EcoCompt_Combined/fichier_combined.csv"

def load_daily_node_intensity(dates, counters, combined_file_path):
    """
    Load data for multiple dates and return a dictionary containing daily data.
    
    Parameters:
    - dates: list, containing the dates to process (e.g., "2023-07-10").
    - counters: DataFrame, containing the mapping of counters to their nearest nodes.
    - combined_file_path: str, the file path to the original counter data.
    
    Returns:：
    - daily_data: dict, with each date corresponding to a DataFrame in the format {date: DataFrame}
    """
    # 1. Read the original counter data
    combined_data = pd.read_csv(combined_file_path, delimiter=";")

    # Dictionary to store daily data
    daily_data = {}

    for date in dates:
        # 2. Filter the data for the current date
        filtered_data = combined_data[combined_data['date'] == date].copy()

        # 3. Extract the base IDs of counters
        filtered_data['counter_id'] = filtered_data['id'].str.extract(r'(MMM_EcoCompt_\w+?)_')

        # 4. Match the counters with their nearest nodes
        merged_data = pd.merge(counters, filtered_data, on='counter_id', how='inner')

        # 5. Summarize the count information for each node
        node_intensity = merged_data[['nearest_node', 'intensity']]

        # 6. Store the DataFrame in the dictionary
        daily_data[date] = node_intensity
        print(f"The node traffic data for {date} has been successfully loaded.")
    
    return daily_data

# Define the date range
dates_to_load = [
    "2023-07-10", "2023-07-11", "2023-07-12",
    "2023-07-13", "2023-07-14", "2023-07-15", "2023-07-16"
]

# File path
combined_file_path = "../Data/Data_EcoCompt_Combined/fichier_combined.csv"

# Call the function to load the data
daily_data = load_daily_node_intensity(dates_to_load, counters, combined_file_path)

# Check the data for a specific day
print(daily_data["2023-07-10"].head())




# %% Estimate the intensity of unknown nodes

import numpy as np
import pandas as pd
from scipy.spatial import KDTree
import os

def estimate_unknown_intensity(daily_data, G):
    """
    Estimate the traffic of unknown nodes using known node data and update the graph G.
    
    Parameters:
    - daily_data: dict, daily traffic data for known nodes, formatted as {date: DataFrame}.
    - G: networkx graph object containing the bicycle network structure.

    Returns:
    - estimated_data: dict, the estimated daily traffic for unknown nodes, formatted as {date: DataFrame}.
    """
    from scipy.spatial import KDTree
    import numpy as np
    import pandas as pd

    # Dictionary to store the estimation results
    estimated_data = {}

    for date, node_data in daily_data.items():
        print(f"Processing date: {date}")

        # Extract information for known nodes
        known_nodes = node_data['nearest_node'].tolist()
        known_coords = np.array([[G.nodes[node]['x'], G.nodes[node]['y']] for node in known_nodes])
        known_intensities = node_data['intensity'].values

        # Retrieve all nodes
        all_nodes = list(G.nodes())
        all_coords = np.array([[G.nodes[node]['x'], G.nodes[node]['y']] for node in all_nodes])

        # Identify unknown nodes
        unknown_nodes = [node for node in all_nodes if node not in known_nodes]
        unknown_coords = np.array([[G.nodes[node]['x'], G.nodes[node]['y']] for node in unknown_nodes])

        # Build a KD-Tree
        kd_tree = KDTree(known_coords)

        # Initialize the intensity for unknown nodes
        unknown_intensity = []

        # Iterate over unknown nodes to calculate the weighted average using the nearest 4 known nodes
        for coord in unknown_coords:
            distances, indices = kd_tree.query(coord, k=4)  
            weights = 1 / distances  # The weights are the inverse of the distances
            weighted_intensity = np.sum(weights * known_intensities[indices]) / np.sum(weights)
            unknown_intensity.append(weighted_intensity)

        # Save the estimation results to a DataFrame
        estimated_data[date] = pd.DataFrame({
            'node': unknown_nodes,
            'intensity': unknown_intensity
        })

        # Update the intensity of unknown nodes in graph G
        for i, node in enumerate(unknown_nodes):
            G.nodes[node]['intensity'] = unknown_intensity[i]

        print(f"The estimation of traffic for unknown nodes on {date} has been completed.")

    return estimated_data

estimated_daily_data = estimate_unknown_intensity(daily_data, G)

# Check the results for a some day
print(estimated_daily_data["2023-07-10"])





# %% Visualize traffic intensity across multiple dates
import folium
import numpy as np

# Create a folium map
center_coords = [43.607, 3.877]  # Map center
m = folium.Map(location=center_coords, zoom_start=13)

# Legend section
legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; width: 300px; height: 180px; 
    background-color: white; z-index:9999; font-size:14px;
    border:2px solid grey; border-radius:5px; padding: 10px;">
    <b>Intensity Legend</b><br>
    <i style="background:#D12315; width:15px; height:15px; display:inline-block;"></i> > 1500 (High Intensity)<br>
    <i style="background:#FE4528; width:15px; height:15px; display:inline-block;"></i> > 1200<br>
    <i style="background:#FB9234; width:15px; height:15px; display:inline-block;"></i> > 900<br>
    <i style="background:#FFEF3A; width:15px; height:15px; display:inline-block;"></i> > 600<br>
    <i style="background:#6CD932; width:15px; height:15px; display:inline-block;"></i> > 300<br>
    <i style="background:#038C05; width:15px; height:15px; display:inline-block;"></i> <= 300 (Low Intensity)<br>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Define color mapping rules
def get_color(intensity):
    if intensity > 1500:
        return '#D12315'
    elif intensity > 1200:
        return '#FE4528'
    elif intensity > 900:
        return '#FB9234'
    elif intensity > 600:
        return '#FFEF3A'
    elif intensity > 300:
        return '#6CD932'
    else:
        return '#23C326'

# Create layers for each day's data
for date, known_data in daily_data.items():
    print(f"Processing date: {date}")
    layer = folium.FeatureGroup(name=f"Data {date}")

    # Retrieve the traffic intensity for unknown nodes from estimated_daily_data
    estimated_data = estimated_daily_data[date]

    # 1. Update the node intensity in graph G
    for node in G.nodes:
        if node in known_data['nearest_node'].values:
            # Use the known node traffic from daily_data
            G.nodes[node]['intensity'] = known_data.set_index('nearest_node').loc[node, 'intensity']
        elif node in estimated_data['node'].values:
            # Use the estimated values from estimated_daily_data
            G.nodes[node]['intensity'] = estimated_data.set_index('node').loc[node, 'intensity']
        else:
            # Set nodes without data to NaN
            G.nodes[node]['intensity'] = np.nan

    # 2. Update the edge intensity
    for u, v, data in G.edges(data=True):
        node_u_intensity = G.nodes[u].get('intensity', np.nan)
        node_v_intensity = G.nodes[v].get('intensity', np.nan)

        # Get the number of connecting edges between nodes u and v
        degree_u = G.degree(u)
        degree_v = G.degree(v)# Did not use degree_u = len(list(G.edges(u))) because some roads we removed still distribute bicycle traffic, so the information from the original graph is used instead.
        if (
            np.isscalar(node_u_intensity) and np.isscalar(node_v_intensity) and not (np.isnan(node_u_intensity) or np.isnan(node_v_intensity)) and degree_u > 0 and degree_v > 0
        ):
            data['intensity'] = (node_u_intensity / degree_u) + (node_v_intensity / degree_v)# Each edge has two nodes (u, v), and each node will distribute intensity to the edges it is connected to.
        else:
            data['intensity'] = np.nan  # Set to NaN if no value

    # 3. Draw edges in the layer
    for u, v, data in G.edges(data=True):
        intensity = data.get('intensity', None)
        highway_type = data.get('highway', 'Unknown')  # Retrieve road types

        if intensity is not None and not np.isnan(intensity):
            # Set colors based on intensity
            color = get_color(intensity)

            # Check for geometry to make paths smoother
            if 'geometry' in data:
                coords = [(point[1], point[0]) for point in data['geometry'].coords]
            else:
                coords = [
                    (G.nodes[u]['y'], G.nodes[u]['x']),
                    (G.nodes[v]['y'], G.nodes[v]['x'])
                ]

            # Draw paths or segments
            folium.PolyLine(
                coords,
                color=color,
                weight=4,  
                opacity=0.9,
                tooltip=folium.Tooltip(f"Road Type: {highway_type}")
            ).add_to(layer)

    # 4. Mark counter nodes in the layer
    for _, row in known_data.iterrows():
        node = row['nearest_node']
        intensity = row['intensity']
        lat, lon = G.nodes[node]['y'], G.nodes[node]['x']
        folium.Marker(
        location=(lat, lon),
        icon=folium.Icon(color="blue"),  # Set the icon
        popup=folium.Popup(f"Intensity: {intensity}", max_width=200)  # Set the popup box
    ).add_to(layer)

    # Add the layer to the map
    layer.add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Save the map
output_map_path = "../Result/real_data_map.html"
m.save(output_map_path)
print(f"The multi-date map has been saved to: {output_map_path}")




# %% Check the attributes of each edge to understand the types available
'''
from collections import Counter

# Extract the 'highway' attribute of all edges
highway_types = []

for u, v, data in G.edges(data=True):
    highway = data.get('highway', None)  # Retrieve the 'highway' attribute
    if highway:
        if isinstance(highway, list):  # If it's a list, expand and add
            highway_types.extend(highway)
        else:
            highway_types.append(highway)

# Count the number of each road type
highway_counter = Counter(highway_types)

# Output all road types and their counts
print("Included road types and their counts:")
for highway, count in highway_counter.items():
    print(f"{highway}: {count}")
'''