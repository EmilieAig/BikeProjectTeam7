# %%
import pandas as pd
from prophet import Prophet
from pathlib import Path

# Chemin vers le fichier de données (ajustez selon votre structure)
file_path = Path(__file__).resolve().parents[3] / 'Code' / 'Data' / 'Data_EcoCompt_clean' / 'fichier_combined.csv'

# Charger les données
data = pd.read_csv(file_path, sep=';')

# Garder les colonnes d'intérêt
data = data[['date', 'intensity', 'laneId', 'latitude', 'longitude']]

# Convertir la colonne 'date' en format datetime
data['date'] = pd.to_datetime(data['date'])

# Définir la période de prévision (du 1er novembre 2023 au 31 décembre 2024)
start_date = pd.to_datetime('2023-11-01')
end_date = pd.to_datetime('2024-12-31')

# Créer la période de prévision
future_dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Dictionnaire pour stocker les prévisions
predictions = []

# Boucle pour chaque `laneId` unique
for lane in data['laneId'].unique():
    lane_data = data[data['laneId'] == lane]
    lane_data = lane_data[['date', 'intensity']].rename(columns={'date': 'ds', 'intensity': 'y'})
    
    # Initialiser et ajuster le modèle Prophet
    model = Prophet()
    model.fit(lane_data)
    
    # Créer un DataFrame pour les dates de prévision
    future_df = pd.DataFrame(future_dates, columns=['ds'])
    
    # Faire la prévision
    forecast = model.predict(future_df)
    
    # Ajouter les prévisions au DataFrame
    forecast['laneId'] = lane
    forecast = forecast[['ds', 'yhat', 'laneId']]
    forecast.rename(columns={'ds': 'date', 'yhat': 'predicted_intensity'}, inplace=True)
    
    # Ajouter les résultats des prévisions à la liste
    predictions.append(forecast)

# Concaténer toutes les prévisions en un seul DataFrame
all_predictions = pd.concat(predictions)

# Calculer l'intensité totale prédite sur toute la période
total_predicted_intensity = all_predictions['predicted_intensity'].sum()

# Répartition de l'intensité totale entre les écocompteurs
# Normalisation pour que la somme des intensités des écocompteurs soit égale à l'intensité totale
all_predictions['relative_intensity'] = all_predictions['predicted_intensity'] / total_predicted_intensity
all_predictions['dispatched_intensity'] = all_predictions['relative_intensity'] * total_predicted_intensity

# Sauvegarder le résultat dans un fichier CSV
output_file = 'dispatched_bike_intensity_nov2023_dec2024.csv'
all_predictions.to_csv(output_file, index=False)

print(f"Les prévisions pour la période entre le 1er novembre 2023 et le 31 décembre 2024 ont été sauvegardées dans {output_file}")

# %%
import pandas as pd
import folium
from folium.plugins import HeatMap
from pathlib import Path

# Charger les prévisions depuis le fichier généré précédemment
file_path = 'dispatched_bike_intensity_nov2023_dec2024.csv'
predictions = pd.read_csv(file_path)

# Charger le fichier de données original pour les coordonnées géographiques
original_data_path = Path(__file__).resolve().parents[3] / 'Code' / 'Data' / 'Data_EcoCompt_clean' / 'fichier_combined.csv'
original_data = pd.read_csv(original_data_path, sep=';')

# Garder les colonnes d'intérêt (pour la géolocalisation)
original_data = original_data[['laneId', 'latitude', 'longitude']].drop_duplicates()

# Joindre les données géographiques avec les prévisions sur la base de `laneId`
predictions = predictions.merge(original_data, on='laneId', how='left')

# Vérifier que les informations de latitude et longitude sont bien présentes
print(predictions[['laneId', 'latitude', 'longitude', 'dispatched_intensity']].head())

# Créer une carte centrée sur Montpellier
map_center = [43.6117, 3.8767]  # Coordonnées de Montpellier
m = folium.Map(location=map_center, zoom_start=12)

# Ajouter des marqueurs sur la carte pour chaque écocompteur avec les prévisions d'intensité
for _, row in predictions.iterrows():
    # On prend les informations nécessaires
    latitude = row['latitude']
    longitude = row['longitude']
    intensity = row['dispatched_intensity']  # L'intensité dispatchée
    
    # Ajouter un cercle pour chaque écocompteur
    folium.Circle(
        location=[latitude, longitude],
        radius=50,  # Taille du cercle
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=f"Lane: {row['laneId']}<br>Intensité: {intensity:.2f}",
    ).add_to(m)

# Ajouter une HeatMap si vous souhaitez avoir une vue thermique des prévisions
heat_data = [[row['latitude'], row['longitude'], row['dispatched_intensity']] for _, row in predictions.iterrows()]
HeatMap(heat_data).add_to(m)

# Sauvegarder la carte dans un fichier HTML
map_filename = "bike_traffic_map.html"
m.save(map_filename)

print(f"La carte a été sauvegardée dans {map_filename}")

# %%
