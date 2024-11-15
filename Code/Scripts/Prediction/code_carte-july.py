# %%
import folium
import pandas as pd
import requests

# Charger les données de prédictions et de coordonnées
predictions_path = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/predictions_long_format_july.csv'
coords_path = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/ecocompteurs_coords.csv'

predictions_df = pd.read_csv(predictions_path, sep=';')
coords_df = pd.read_csv(coords_path)
merged_df = pd.merge(predictions_df, coords_df, on='laneId', how='left')

# Filtrer pour une date et trier par intensité
date_to_filter = '2023-07-10'
filtered_df = merged_df[merged_df['date'] == date_to_filter].sort_values(by='predicted_intensity', ascending=False)
locations = list(zip(filtered_df['longitude'], filtered_df['latitude']))

# Créer une carte centrée sur Montpellier
m = folium.Map(location=[43.6117, 3.8777], zoom_start=12)

# URL de l'API OSRM
osrm_url = "http://router.project-osrm.org/route/v1/cycling/"

# Générer des itinéraires entre les points consécutifs
for i in range(len(locations) - 1):
    # Points de départ et d'arrivée
    start = locations[i]
    end = locations[i+1]
    
    # Créer l'URL pour l'API OSRM
    url = f"{osrm_url}{start[0]},{start[1]};{end[0]},{end[1]}?overview=full&geometries=geojson"
    
    # Envoyer la requête GET à OSRM
    response = requests.get(url)
    
    if response.status_code == 200:
        route = response.json()
        folium.GeoJson(route, name='route').add_to(m)
    else:
        print(f"Erreur avec OSRM pour les points {start} et {end}")
    
# Ajouter des marqueurs pour chaque écocompteur
for idx, (lon, lat) in enumerate(locations):
    intensity = filtered_df.iloc[idx]['predicted_intensity']
    folium.CircleMarker(
        location=(lat, lon),
        radius=5,
        color='green',
        fill=True,
        fill_color='green',
        fill_opacity=0.7,
        popup=f"Intensité: {intensity}",
    ).add_to(m)

# Sauvegarder la carte
m.save('/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/map_with_paths_july10_osrm.html')
print("Carte sauvegardée sous 'map_with_paths_july10_osrm.html'")

# %%
