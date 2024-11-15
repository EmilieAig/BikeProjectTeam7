
# %%
import os
import pandas as pd
from prophet import Prophet

# Chargement des données
data_path = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Data/Data_EcoCompt_clean/fichier_combined.csv'
data = pd.read_csv(data_path, sep=';')

# Transformation des dates en format datetime
data['date'] = pd.to_datetime(data['date'])

# Dictionnaire pour stocker les prédictions par laneId
predictions_all_lanes = {}

# Filtrage et configuration de Prophet pour chaque `laneId`
for lane_id, lane_data in data.groupby('laneId'):
    # Filtrer les colonnes nécessaires pour Prophet : date et intensité
    lane_data = lane_data[['date', 'intensity']].rename(columns={'date': 'ds', 'intensity': 'y'})
    
    # Création et entraînement du modèle Prophet
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=True)
    model.fit(lane_data)
    
    # Génération des futures dates pour les prévisions : du 2023-11-01 au 2024-12-31
    future = model.make_future_dataframe(periods=425)  # Ajusté à 425 jours
    forecast = model.predict(future)
    
    # Filtrer les prévisions pour la période souhaitée
    forecast = forecast[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'predicted_intensity'})
    forecast = forecast[forecast['date'] >= '2023-11-01']
    
    # Ajout des informations `laneId` et des prévisions dans le dictionnaire
    predictions_all_lanes[lane_id] = forecast[['date', 'predicted_intensity']].set_index('date')['predicted_intensity']

# Combiner toutes les prédictions par `laneId` en un seul DataFrame
predictions_df = pd.DataFrame(predictions_all_lanes)

# Appliquer l'interpolation pour remplacer les valeurs négatives ou manquantes
predictions_df = predictions_df.applymap(lambda x: x if x >= 0 else None)  # Remplacer les négatifs par None
predictions_df.interpolate(method='linear', axis=0, inplace=True)  # Interpolation sur l'axe des jours

# Réinitialiser l'index pour avoir une colonne `date` au lieu de l'index
predictions_df.reset_index(inplace=True)

# Sauvegarde des résultats dans un fichier CSV
save_directory = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction'
os.makedirs(save_directory, exist_ok=True)
predictions_path = os.path.join(save_directory, 'predictions_bike_intensity1.csv')
predictions_df.to_csv(predictions_path, index=False, sep=';')

print(f"Les prédictions ont été enregistrées dans : {predictions_path}")

# %%
