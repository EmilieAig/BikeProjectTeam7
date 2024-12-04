# %%
import os
import numpy as np
import pandas as pd
import seaborn as sns
import pooch  # download data / avoid re-downloading

# Configuration de Seaborn
sns.set_palette("colorblind")
palette = sns.color_palette("twilight", n_colors=12)
pd.options.display.max_rows = 8

# URL et chemin du fichier
url = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/DataBike2023.csv"
path_target = "./DataBike2023.csv"
path, fname = os.path.split(path_target)

# Téléchargement des données
known_hash = '81e2c763a0995e501cb6857160078331ac5a80cc165dd672abaf11c0f4d99d8f'  # Remplacez par le hachage si nécessaire
pooch.retrieve(url, path=path, fname=fname, known_hash=known_hash)

# Chargement des données
df_DataBike_raw = pd.read_csv(url, low_memory=False)  # Vous pouvez spécifier dtype ici si nécessaire
df_DataBike_raw.info()  # Affichez les informations sur les données
df_DataBike_raw.head(n=10)  # Affichez les 10 premières lignes
# %%

# %%

# %%

# Configuration de Seaborn
sns.set_palette("colorblind")
palette = sns.color_palette("twilight", n_colors=12)
pd.options.display.max_rows = 8

# URL et chemin du fichier
url = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/DataBike2023.csv"
path_target = "./DataBike2023.csv"
path, fname = os.path.split(path_target)

# Téléchargement des données
known_hash = '81e2c763a0995e501cb6857160078331ac5a80cc165dd672abaf11c0f4d99d8f'  # Remplacez par le hachage si nécessaire
pooch.retrieve(url, path=path, fname=fname, known_hash=known_hash)

# Chargement des données
df_DataBike_raw = pd.read_csv(path_target, low_memory=False)  # Utilisez le chemin local

# Assurez-vous que la colonne "Departure" est bien au format datetime
df_DataBike_raw['Departure'] = pd.to_datetime(df_DataBike_raw['Departure'])

# Filtrer les données d'Avril (04) à Octobre (10)
df_filtered = df_DataBike_raw[(df_DataBike_raw['Departure'].dt.month >= 4) & (df_DataBike_raw['Departure'].dt.month <= 10)]

# Afficher les informations et les 10 premières lignes du DataFrame filtré
df_filtered.info()
df_filtered.head(n=10)
