#%%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Définir un chemin relatif pour accéder au fichier depuis deux niveaux au-dessus
file_path = Path(__file__).resolve().parents[2] / 'Data' / 'Data_EcoCompt_clean' / 'fichier_combined.csv'

# Charger les données
data = pd.read_csv(file_path, sep=';')

# Convertir la colonne 'date' en format datetime
data['date'] = pd.to_datetime(data['date'])

# Charger les données
data = pd.read_csv(file_path, sep=';')

# Statistiques descriptives
stats = data.describe()

# Afficher les premières lignes pour vérifier
print(data.head())
print(stats)

#%%
# Visualisation des données

# Histogramme de l'intensité
plt.figure(figsize=(10, 6))
sns.distplot(data['intensity'], kde=True, color='blue', bins=30)
plt.title('Distribution de l\'intensité du trafic')
plt.xlabel('Intensité')
plt.ylabel('Fréquence')
plt.show()

# Diagramme de dispersion de l'intensité par date
plt.figure(figsize=(10, 6))
sns.scatterplot(x=data['date'], y=data['intensity'], color='orange')
plt.title('Intensité du trafic par date')
plt.xlabel('Date')
plt.ylabel('Intensité')
plt.xticks(rotation=45)
plt.show()

# Carte des positions de vélo (longitude vs latitude)
plt.figure(figsize=(10, 6))
sns.scatterplot(x=data['longitude'], y=data['latitude'], hue=data['vehicleType'], palette='Set1', alpha=0.7)
plt.title('Carte des positions de vélos')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend(title='Type de véhicule')
plt.show()

# %%
#Série Temporelle qui permet de visualiser l'évolution de l'intensité du trafic dans le temps.
import matplotlib.pyplot as plt

# S'assurer que la colonne 'date' est de type datetime
data['date'] = pd.to_datetime(data['date'])

# Mettre 'date' comme index pour pouvoir utiliser resample
data.set_index('date', inplace=True)

# Agréger par mois en prenant la moyenne d’intensité
monthly_data = data['intensity'].resample('M').mean()

# Tracer le graphique
plt.figure(figsize=(12, 6))
plt.plot(monthly_data.index, monthly_data.values, color='blue', marker='o', linestyle='-')
plt.title("Évolution mensuelle de l'intensité du trafic")
plt.xlabel("Mois")
plt.ylabel("Intensité moyenne")
plt.grid(True)
plt.show()
