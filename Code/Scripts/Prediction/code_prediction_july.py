# %%# %%
import os
from pathlib import Path
import pandas as pd
from prophet import Prophet

# Construire le chemin relatif vers le fichier CSV
#file_path = Path(__file__).resolve().parents[2] / 'Data' / 'Data_EcoCompt_clean' / 'fichier_combined.csv'

# Définir le chemin absolu du fichier CSV
file_path = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Data/Data_EcoCompt_clean/fichier_combined.csv'

# Charger les données
data = pd.read_csv(file_path, sep=';')

# Conversion des dates en format datetime
data['date'] = pd.to_datetime(data['date'])

# Filtrer les données entre le 2023-04-01 et le 2023-07-09
data = data[(data['date'] >= '2023-04-01') & (data['date'] <= '2023-07-09')]

# Dictionnaire pour stocker les prédictions par `laneId`
predictions_all_lanes = {}

# Filtrage et configuration de Prophet pour chaque `laneId`
for lane_id, lane_data in data.groupby('laneId'):
    # Filtrer les colonnes nécessaires pour Prophet : date et intensité
    lane_data = lane_data[['date', 'intensity']].rename(columns={'date': 'ds', 'intensity': 'y'})
    
    # Création et entraînement du modèle Prophet
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=True)
    model.fit(lane_data)
    
    # Générer les dates futures pour une prévision d'une semaine (7 jours supplémentaires)
    future = model.make_future_dataframe(periods=7)  # Prévoir 7 jours après le 09/07/2023
    forecast = model.predict(future)
    
    # Filtrer les prévisions pour la période du 2023-07-10 au 2023-07-16
    forecast = forecast[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'predicted_intensity'})
    forecast = forecast[(forecast['date'] >= '2023-07-10') & (forecast['date'] <= '2023-07-16')]
    
    # Ajouter les prévisions dans le dictionnaire par `laneId`
    predictions_all_lanes[lane_id] = forecast[['date', 'predicted_intensity']].set_index('date')['predicted_intensity']

# Combiner toutes les prédictions par `laneId` en un seul DataFrame
predictions_df = pd.DataFrame(predictions_all_lanes)

# Remplacer les valeurs négatives ou manquantes par interpolation
predictions_df = predictions_df.applymap(lambda x: x if x >= 0 else None)
predictions_df.interpolate(method='linear', axis=0, inplace=True)

# Réinitialiser l'index pour obtenir une colonne `date` au lieu de l'index
predictions_df.reset_index(inplace=True)

# Sauvegarder les résultats dans un fichier CSV
save_directory = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction'
os.makedirs(save_directory, exist_ok=True)
predictions_path = os.path.join(save_directory, 'predictions_bike_intensity_july_week.csv')
predictions_df.to_csv(predictions_path, index=False, sep=';')

print(f"Les prédictions ont été enregistrées dans : {predictions_path}")
