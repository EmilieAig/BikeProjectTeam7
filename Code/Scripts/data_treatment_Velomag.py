import pooch
import pandas as pd
import numpy as np

# URL où le fichier est hébergé
url = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/DataBike2023.csv"

# Calculer ou obtenir le hachage SHA256 du fichier
known_hash = "81e2c763a0995e501cb6857160078331ac5a80cc165dd672abaf11c0f4d99d8f"  # Remplacez ceci par le vrai hachage SHA256 du fichier

# Emplacement local pour stocker le fichier téléchargé
cache_dir = pooch.os_cache("my_data_cache")  # Le cache sera sauvegardé dans un répertoire par défaut

# Téléchargement du fichier avec pooch (il sera mis en cache localement)
dataset = pooch.retrieve(url, path=cache_dir, downloader=pooch.HTTPDownloader(), known_hash=known_hash)

# Charger le fichier CSV téléchargé dans un DataFrame
df = pd.read_csv(dataset, encoding='utf-8', low_memory=False)

# Nettoyer les noms de colonnes
df.columns = df.columns.str.strip().str.replace('°', 'C').str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

# Fonction de nettoyage des caractères spéciaux
def clean_text(text):
    return str(text).replace('√©', 'e') \
                     .replace('√®', 'e') \
                     .replace('√†', 'a') \
                     .replace('√ç', 'c')

# Appliquer le nettoyage à toutes les colonnes
df = df.applymap(clean_text)

# Séparer la colonne 'Departure' en deux : une pour la date et l'autre pour l'heure
df[['Departure_Date', 'Departure_Time']] = df['Departure'].str.split(' ', expand=True)

# Séparer la colonne 'Return' en deux : une pour la date et l'autre pour l'heure
df[['Return_Date', 'Return_Time']] = df['Return'].str.split(' ', expand=True)

# Conversion des colonnes de date et d'heure en format DateTime
df['Departure_DateTime'] = pd.to_datetime(df['Departure_Date'] + ' ' + df['Departure_Time'])
df['Return_DateTime'] = pd.to_datetime(df['Return_Date'] + ' ' + df['Return_Time'])

# Suppression des colonnes dont on n'a plus besoin
df = df.drop(['Departure', 'Return', 'Departure_DateTime', 'Return_DateTime', 'Lock_duration_sec.', 'Number_of_bike_locks', 'Manager', 'new_account'], axis=1)

# Générer des données aléatoires de latitude et de longitude autour de Montpellier
# Plage de latitude autour de 43.61 (de 43.55 à 43.67 pour rester proche)
latitudes_dep = np.random.uniform(43.55, 43.67, len(df))

# Plage de longitude autour de 3.88 (de 3.82 à 3.93 pour rester proche)
longitudes_dep = np.random.uniform(3.82, 3.93, len(df))

# Plage de latitude autour de 43.61 (de 43.55 à 43.67 pour rester proche)
latitudes_ret = np.random.uniform(43.55, 43.67, len(df))

# Plage de longitude autour de 3.88 (de 3.82 à 3.93 pour rester proche)
longitudes_ret = np.random.uniform(3.82, 3.93, len(df))

# Ajouter les colonnes Latitude et Longitude au DataFrame
df['Departure latitude'] = latitudes_dep
df['Departure longitude'] = longitudes_dep
df['Return latitude'] = latitudes_ret
df['Return longitude'] = longitudes_ret

# Sauvegarder le DataFrame dans un fichier CSV
df.to_csv('cleaned_data.csv', index=False, encoding='utf-8')

print("Les données ont été nettoyées et enregistrées dans 'cleaned_data.csv'.")
