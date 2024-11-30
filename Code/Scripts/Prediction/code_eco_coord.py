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













#VERSION 2
# %%
import pandas as pd
import pooch
from pathlib import Path

# Configurer Pooch pour gérer les fichiers nécessaires
BASE_URL = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/Data_EcoCompt_clean/"
pooch_data = pooch.create(
    path=pooch.os_cache("BikeProjectTeam7"),  # Cache pour les fichiers téléchargés
    base_url=BASE_URL,                       # URL de base pour les fichiers
    registry={                               # Fichiers à gérer avec leurs hachages SHA256
        "fichier_combined.csv": "sha256:08c71a1718b279efe1ebb60f6446e19c8b786d93a2a16bcb8504ab1a888dc3f8"
    },
)

# Télécharger et charger le fichier combiné
combined_file_path = pooch_data.fetch("fichier_combined.csv")  # Récupérer ou vérifier le fichier
combined_df = pd.read_csv(combined_file_path, sep=';')         # Charger les données avec pandas

# Extraire les colonnes `laneId`, `latitude`, et `longitude`
coords_df = combined_df[['laneId', 'latitude', 'longitude']].drop_duplicates()

# Définir le chemin de sauvegarde pour le fichier 'ecocompteurs_coords.csv'
project_root = Path(__file__).resolve().parents[2]
prediction_folder = project_root / 'Code' / 'Scripts' / 'Prediction'
prediction_folder.mkdir(parents=True, exist_ok=True)  # Créer le dossier si nécessaire
coords_file_path = prediction_folder / 'ecocompteurs_coords.csv'

# Sauvegarder les données extraites dans un fichier CSV
coords_df.to_csv(coords_file_path, index=False)

print(f"Le fichier 'ecocompteurs_coords.csv' a été créé dans le dossier {coords_file_path}.")
