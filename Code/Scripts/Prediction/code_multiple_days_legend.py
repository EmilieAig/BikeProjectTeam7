# %%
import pandas as pd
import folium
import osmnx as ox
from geopy.distance import geodesic
from folium import LayerControl
from tqdm import tqdm

# Chemin des fichiers
ecocompteur_file = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/ecocompteurs_coords.csv'
predictions_file = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/predictions_long_format_july.csv'
stations_file = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/GeolocalisationStation.csv'

# Charger les données des éco-compteurs
ecocompteur = pd.read_csv(ecocompteur_file, sep=',')
ecocompteur.rename(columns=lambda x: x.strip(), inplace=True)
ecocompteur.rename(columns={"LaneID": "laneId"}, inplace=True)

# Charger les prédictions
predictions = pd.read_csv(predictions_file, sep=';')
predictions['date'] = pd.to_datetime(predictions['date'])

# Sélectionner les dates spécifiques (10 au 16 juillet 2023)
dates_of_interest = pd.date_range('2023-07-10', '2023-07-16')
predictions_filtered = predictions[predictions['date'].isin(dates_of_interest)]

# Joindre les prédictions aux coordonnées des éco-compteurs
merged_data = pd.merge(ecocompteur, predictions_filtered, on='laneId', how='inner')

# Filtrer les points dans un rayon de 15 km autour de Montpellier
map_center = [43.6117, 3.8777]
radius_km = 15

def is_within_radius(lat, lon, center, radius):
    return geodesic(center, (lat, lon)).km <= radius

merged_data['within_radius'] = merged_data.apply(
    lambda row: is_within_radius(row['latitude'], row['longitude'], map_center, radius_km),
    axis=1
)
merged_data = merged_data[merged_data['within_radius']]

# Charger les données des stations
stations = pd.read_csv(stations_file)

# Associer les noms de stations aux éco-compteurs via coordonnées
def find_station_name(lat, lon, stations):
    stations_copy = stations.copy()
    stations_copy['distance'] = stations_copy.apply(
        lambda row: geodesic((lat, lon), (row['Latitude'], row['Longitude'])).km,
        axis=1
    )
    closest_station = stations_copy.loc[stations_copy['distance'].idxmin()]
    return closest_station['Station']

merged_data['station_name'] = merged_data.apply(
    lambda row: find_station_name(row['latitude'], row['longitude'], stations),
    axis=1
)

# Charger un graphe routier élargi pour Montpellier
print("Téléchargement du graphe routier d'OSM...")
graph = ox.graph_from_point(map_center, dist=radius_km * 1000, network_type='bike', simplify=True)

# Vérifier si les points sont reliés au graphe
def safe_nearest_node(graph, x, y):
    try:
        return ox.distance.nearest_nodes(graph, X=x, Y=y)
    except Exception as e:
        print(f"Erreur pour les coordonnées ({y}, {x}): {e}")
        return None

print("Association des points aux nœuds OSM...")
merged_data['osmid'] = merged_data.apply(
    lambda row: safe_nearest_node(graph, row['longitude'], row['latitude']),
    axis=1
)

# Retirer les points non associés à un nœud
merged_data.dropna(subset=['osmid'], inplace=True)

# Créer une carte Folium
m = folium.Map(location=map_center, zoom_start=13)

# Ajouter la légende
legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; width: 250px; height: 140px; 
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

# Fonction pour ajouter les points et les routes à un FeatureGroup selon le jour sélectionné
def create_layer_for_date(date, graph, merged_data):
    day_data = merged_data[merged_data['date'] == date]
    feature_group = folium.FeatureGroup(name=f"{date.strftime('%Y-%m-%d')}")

    # Ajouter les chemins entre tous les points connectés avec intensités colorées
    for i, row1 in tqdm(day_data.iterrows(), total=len(day_data), desc=f"Processing {date}"):
        for j, row2 in day_data.iterrows():
            if i >= j:
                continue
            
            osmid1 = row1['osmid']
            osmid2 = row2['osmid']
            intensity = (row1['predicted_intensity'] + row2['predicted_intensity']) / 2  # Moyenne d'intensité

            # Déterminer la couleur en fonction de l'intensité
            if intensity > 1500:
                color = '#FE4528'  # Rouge
            elif intensity > 1200:
                color = '#FD6121'  # Orange
            elif intensity > 900:
                color = '#D95018'    # Orange clair
            elif intensity > 600:
                color = '#FFEF3A'  # Jaune
            elif intensity > 300:
                color = '#6CD932'  # Vert clair
            else:
                color = '#038C05'  # Vert foncé
            
            try:
                shortest_path = ox.shortest_path(graph, osmid1, osmid2, weight='length')
                if shortest_path:
                    path_coords = [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in shortest_path]
                    folium.PolyLine(path_coords, color=color, weight=5, opacity=0.7).add_to(feature_group)
            except Exception as e:
                print(f"Impossible de relier les points {osmid1} et {osmid2}: {e}")

    # Ajouter les prédictions sur la carte avec les noms des stations
    for _, row in day_data.iterrows():
        lat, lon = row['latitude'], row['longitude']
        station_name = row['station_name']
        
        # Ajouter un marqueur avec le nom de la station
        folium.Marker(
            location=[lat, lon],
            popup=f"Station: {station_name}"
        ).add_to(feature_group)

    return feature_group

# Ajouter une couche pour chaque jour
for date in dates_of_interest:
    layer = create_layer_for_date(date, graph, merged_data)
    layer.add_to(m)

# Ajouter un contrôle de couches
LayerControl(collapsed=False).add_to(m)

# Sauvegarder la carte
output_file = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/map_prediction_multiple_days_with_layers_and_legend.html'
m.save(output_file)

print(f"La carte a été enregistrée sous '{output_file}'.")

















#Version avec chemin non local
#%%
import pandas as pd
import folium
import osmnx as ox
from geopy.distance import geodesic
from folium import LayerControl
from tqdm import tqdm
import pooch
import os

# Fonction pour télécharger les fichiers avec Pooch
def download_file(url, target_path, known_hash):
    """
    Télécharge un fichier depuis une URL et vérifie son intégrité à l'aide d'un hachage SHA256.
    
    Args:
        url (str): URL du fichier.
        target_path (str): Chemin où le fichier sera enregistré localement.
        known_hash (str): Hachage SHA256 attendu du fichier.
        
    Returns:
        str: Chemin du fichier téléchargé.
    """
    path, fname = os.path.split(target_path)
    return pooch.retrieve(url=url, fname=fname, path=path, known_hash=known_hash)

# URLs et hachages des fichiers nécessaires
files_info = {
    "ecocompteur_file": {
        "url": "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Scripts/Prediction/ecocompteurs_coords.csv",
        "target_path": "./data/ecocompteurs_coords.csv",
        "known_hash": "md5:5d41402abc4b2a76b9719d911017c592",  # Remplace par le vrai hachage SHA256
    },
    "predictions_file": {
        "url": "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Scripts/Prediction/predictions_long_format_july.csv",
        "target_path": "./data/predictions_long_format_july.csv",
        "known_hash": "md5:6b3a55e0261b0304143f805a249ae3dc",  # Remplace par le vrai hachage SHA256
    },
    "stations_file": {
        "url": "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Scripts/Prediction/GeolocalisationStation.csv",
        "target_path": "./data/GeolocalisationStation.csv",
        "known_hash": "md5:92eb5ffee6ae2fec3ad71c777531578f",  # Remplace par le vrai hachage SHA256
    },
}

# Télécharger les fichiers
for key, info in files_info.items():
    print(f"Téléchargement de {key}...")
    files_info[key]["local_path"] = download_file(
        url=info["url"],
        target_path=info["target_path"],
        known_hash=info["known_hash"]
    )

# Charger les fichiers téléchargés
ecocompteur_file = files_info["ecocompteur_file"]["local_path"]
predictions_file = files_info["predictions_file"]["local_path"]
stations_file = files_info["stations_file"]["local_path"]

# Reste du script inchangé
ecocompteur = pd.read_csv(ecocompteur_file, sep=',')
ecocompteur.rename(columns=lambda x: x.strip(), inplace=True)
ecocompteur.rename(columns={"LaneID": "laneId"}, inplace=True)

predictions = pd.read_csv(predictions_file, sep=';')
predictions['date'] = pd.to_datetime(predictions['date'])

stations = pd.read_csv(stations_file)

# Sélectionner les dates spécifiques (10 au 16 juillet 2023)
dates_of_interest = pd.date_range('2023-07-10', '2023-07-16')
predictions_filtered = predictions[predictions['date'].isin(dates_of_interest)]

# Joindre les prédictions aux coordonnées des éco-compteurs
merged_data = pd.merge(ecocompteur, predictions_filtered, on='laneId', how='inner')

# Filtrer les points dans un rayon de 15 km autour de Montpellier
map_center = [43.6117, 3.8777]
radius_km = 15

def is_within_radius(lat, lon, center, radius):
    return geodesic(center, (lat, lon)).km <= radius

merged_data['within_radius'] = merged_data.apply(
    lambda row: is_within_radius(row['latitude'], row['longitude'], map_center, radius_km),
    axis=1
)
merged_data = merged_data[merged_data['within_radius']]

# Charger les données des stations
stations = pd.read_csv(stations_file)

# Associer les noms de stations aux éco-compteurs via coordonnées
def find_station_name(lat, lon, stations):
    stations_copy = stations.copy()
    stations_copy['distance'] = stations_copy.apply(
        lambda row: geodesic((lat, lon), (row['Latitude'], row['Longitude'])).km,
        axis=1
    )
    closest_station = stations_copy.loc[stations_copy['distance'].idxmin()]
    return closest_station['Station']

merged_data['station_name'] = merged_data.apply(
    lambda row: find_station_name(row['latitude'], row['longitude'], stations),
    axis=1
)

# Charger un graphe routier élargi pour Montpellier
print("Téléchargement du graphe routier d'OSM...")
graph = ox.graph_from_point(map_center, dist=radius_km * 1000, network_type='bike', simplify=True)

# Vérifier si les points sont reliés au graphe
def safe_nearest_node(graph, x, y):
    try:
        return ox.distance.nearest_nodes(graph, X=x, Y=y)
    except Exception as e:
        print(f"Erreur pour les coordonnées ({y}, {x}): {e}")
        return None

print("Association des points aux nœuds OSM...")
merged_data['osmid'] = merged_data.apply(
    lambda row: safe_nearest_node(graph, row['longitude'], row['latitude']),
    axis=1
)

# Retirer les points non associés à un nœud
merged_data.dropna(subset=['osmid'], inplace=True)

# Créer une carte Folium
m = folium.Map(location=map_center, zoom_start=13)

# Ajouter la légende
legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; width: 250px; height: 140px; 
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

# Fonction pour ajouter les points et les routes à un FeatureGroup selon le jour sélectionné
def create_layer_for_date(date, graph, merged_data):
    day_data = merged_data[merged_data['date'] == date]
    feature_group = folium.FeatureGroup(name=f"{date.strftime('%Y-%m-%d')}")

    # Ajouter les chemins entre tous les points connectés avec intensités colorées
    for i, row1 in tqdm(day_data.iterrows(), total=len(day_data), desc=f"Processing {date}"):
        for j, row2 in day_data.iterrows():
            if i >= j:
                continue
            
            osmid1 = row1['osmid']
            osmid2 = row2['osmid']
            intensity = (row1['predicted_intensity'] + row2['predicted_intensity']) / 2  # Moyenne d'intensité

            # Déterminer la couleur en fonction de l'intensité
            if intensity > 1500:
                color = '#FE4528'  # Rouge
            elif intensity > 1200:
                color = '#FD6121'  # Orange
            elif intensity > 900:
                color = '#D95018'    # Orange clair
            elif intensity > 600:
                color = '#FFEF3A'  # Jaune
            elif intensity > 300:
                color = '#6CD932'  # Vert clair
            else:
                color = '#038C05'  # Vert foncé
            
            try:
                shortest_path = ox.shortest_path(graph, osmid1, osmid2, weight='length')
                if shortest_path:
                    path_coords = [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in shortest_path]
                    folium.PolyLine(path_coords, color=color, weight=5, opacity=0.7).add_to(feature_group)
            except Exception as e:
                print(f"Impossible de relier les points {osmid1} et {osmid2}: {e}")

    # Ajouter les prédictions sur la carte avec les noms des stations
    for _, row in day_data.iterrows():
        lat, lon = row['latitude'], row['longitude']
        station_name = row['station_name']
        
        # Ajouter un marqueur avec le nom de la station
        folium.Marker(
            location=[lat, lon],
            popup=f"Station: {station_name}"
        ).add_to(feature_group)

    return feature_group

# Ajouter une couche pour chaque jour
for date in dates_of_interest:
    layer = create_layer_for_date(date, graph, merged_data)
    layer.add_to(m)

# Ajouter un contrôle de couches
LayerControl(collapsed=False).add_to(m)

# Sauvegarder la carte
output_file = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/map_prediction_multiple_days_with_layers_and_legend.html'
m.save(output_file)

print(f"La carte a été enregistrée sous '{output_file}'.")