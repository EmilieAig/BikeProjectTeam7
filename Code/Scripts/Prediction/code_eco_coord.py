# %%
import pandas as pd
import os

# Charger le fichier combiné
combined_df = pd.read_csv('/home/anne_laure/HA712X/BikeProjectTeam7/Code/Data/Data_EcoCompt_clean/fichier_combined.csv', sep=';')

# Extraire les colonnes laneId, latitude et longitude
coords_df = combined_df[['laneId', 'latitude', 'longitude']].drop_duplicates()

# Définir le chemin du dossier 'Prediction'
prediction_folder = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/'

# Créer le chemin complet pour le fichier CSV
coords_file_path = os.path.join(prediction_folder, 'ecocompteurs_coords.csv')

# Sauvegarder ces données dans un fichier CSV dans le dossier 'Prediction'
coords_df.to_csv(coords_file_path, index=False)

print(f"Le fichier 'ecocompteurs_coords.csv' a été créé dans le dossier {prediction_folder}.")

# %%
