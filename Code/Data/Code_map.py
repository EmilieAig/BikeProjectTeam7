#%%
# %%
import pandas as pd
import folium
import os

# Obtenir le répertoire du script actuel
script_dir = os.path.dirname(__file__)

# Construire le chemin relatif vers le fichier CSV de données
data_file_path = os.path.join(script_dir, '..', 'Data', 'Data_EcoCompt_clean', 'fichier_combined.csv')

# Charger les données historiques
historical_data = pd.read_csv(data_file_path, sep=';')

# Créer une carte centrée sur Montpellier (latitude, longitude approximatives)
map_center = [43.611, 3.8767]  # Coordonnées approximatives de Montpellier
m = folium.Map(location=map_center, zoom_start=12)

# Ajouter un marqueur pour chaque ligne de données dans le fichier "combined"
for _, row in historical_data.iterrows():
    # Extraire les informations
    lane_id = row['laneId']
    intensity = row['intensity']
    latitude = row['latitude']
    longitude = row['longitude']
    
    # Texte de l'infobulle avec les informations
    popup_text = f"Lane ID: {lane_id}<br>Intensity: {intensity}<br>Latitude: {latitude}<br>Longitude: {longitude}"
    
    # Ajouter un marqueur sur la carte
    folium.CircleMarker(
        location=[latitude, longitude],
        radius=8,
        color='green',  # Couleur du cercle
        fill=True,
        fill_color='green',
        fill_opacity=0.6,
        popup=popup_text
    ).add_to(m)

# Sauvegarder la carte interactive en HTML
# Construire le chemin relatif pour enregistrer la carte HTML
map_file_path = os.path.join(script_dir, '..', 'Data', 'bike_data_map.html')
m.save(map_file_path)

# Afficher un message pour indiquer que la carte a été générée
print(f"La carte interactive a été générée et sauvegardée sous '{map_file_path}'.")
# %%

