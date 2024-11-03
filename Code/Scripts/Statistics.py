# %%

import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# %%

# Chemin vers le dossier contenant les fichiers CSV
current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(current_directory, 'Data', 'Data_EcoCompt_clean')
all_files = glob.glob(os.path.join(path, "*.csv"))

# %%

# Fonction de chargement pour gérer les erreurs sans `error_bad_lines`
def load_file(file):
    try:
        return pd.read_csv(file, sep=';')
    except pd.errors.EmptyDataError:
        print(f"Fichier vide ou corrompu ignoré : {file}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

# Concaténer tous les fichiers en un seul DataFrame
df = pd.concat((load_file(f) for f in all_files), ignore_index=True)

# Conversion de la colonne 'date' en type datetime (si elle ne l'est pas déjà)
if df['date'].dtype != 'datetime64[ns]':
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

# Filtrer les données de la période d'étude : avril à octobre 2023
df = df[(df['date'] >= '2023-04-01') & (df['date'] <= '2023-10-31')]

# Ajouter les colonnes 'mois' et 'année' pour des analyses temporelles
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

# Grouper par date pour obtenir une moyenne quotidienne
daily_data = df.groupby('date')['intensity'].mean().reset_index()

# %%

# Visualisation de l’utilisation quotidienne
plt.figure(figsize=(12, 6))
plt.plot(daily_data['date'], daily_data['intensity'], label='Intensité quotidienne')
plt.axvspan('2023-07-01', '2023-07-23', color='yellow', alpha=0.3, label="Tour de France")
plt.title("Utilisation quotidienne des vélos (Avril - Octobre 2023)")
plt.xlabel("Date")
plt.ylabel("Nombre moyen de passages")
plt.legend()
plt.show()

# %%

# Calcul des moyennes mensuelles
monthly_data = df.groupby(['year', 'month'])['intensity'].mean().reset_index()

# Statistiques de comparaison avant, pendant et après le Tour de France
before_july = daily_data[(daily_data['date'] < '2023-07-01')]['intensity']
during_july = daily_data[(daily_data['date'] >= '2023-07-01') & (daily_data['date'] <= '2023-07-31')]['intensity']
after_july = daily_data[(daily_data['date'] > '2023-07-31')]['intensity']

# %%

# Calculer les moyennes et les écarts-types
print("Moyenne avant juillet:", before_july.mean())
print("Moyenne en juillet:", during_july.mean())
print("Moyenne après juillet:", after_july.mean())
print("Écart type avant juillet:", before_july.std())
print("Écart type en juillet:", during_july.std())
print("Écart type après juillet:", after_july.std())

# %%
