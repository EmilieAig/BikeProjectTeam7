#%%
import folium
import pandas as pd

# Charger le fichier CSV des prédictions
predictions_path = 'predictions_long_format.csv'
predictions_df = pd.read_csv(predictions_path, sep=';')

# Créer une carte centrée sur Montpellier
map_center = [43.6117, 3.8777]  # Latitude et longitude de Montpellier
m = folium.Map(location=map_center, zoom_start=12)

# Créer un dictionnaire pour les coordonnées des écocompteurs
ecocompteurs_coords = {
    8584788: (43.6001, 3.8776),  # Exemple : écocompteur avec latitude/longitude
    8584789: (43.6051, 3.8806),
    8584790: (43.6091, 3.8836),
    # Ajoute d'autres écocompteurs ici
}

# Ajouter les points (écocompteurs) sur la carte
for _, row in predictions_df.iterrows():
    date = row['date']
    
    # Trier les écocompteurs par intensité pour ce jour-là (en excluant la colonne 'date')
    sorted_lane_ids = row.drop('date').sort_values(ascending=False).index.tolist()
    
    # Créer une liste de coordonnées triées par intensité
    sorted_coords = [(ecocompteurs_coords[int(lane_id)], row[lane_id]) for lane_id in sorted_lane_ids if lane_id.isdigit()]
    
    # Ajouter des marqueurs pour chaque écocompteur trié
    for (lat, lon), intensity in sorted_coords:
        folium.CircleMarker(
            location=(lat, lon),
            radius=5,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.7,
            popup=f"Date: {date}<br>Intensity: {intensity}",
        ).add_to(m)
    
    # Relier les écocompteurs dans l'ordre de l'intensité
    for i in range(len(sorted_coords) - 1):
        lat1, lon1 = sorted_coords[i][0]
        lat2, lon2 = sorted_coords[i + 1][0]
        
        folium.PolyLine(
            locations=[(lat1, lon1), (lat2, lon2)],
            color='red',
            weight=2.5,
            opacity=1
        ).add_to(m)

# Sauvegarder la carte dans un fichier HTML
m.save('map_with_paths_sorted1.html')

print("Carte interactive sauvegardée dans 'map_with_paths_sorted.html'")

# %%
