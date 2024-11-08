#%%
import os
import glob
import pandas as pd

# Chemin exact du dossier contenant les fichiers CSV
dossier = "/home/anne_laure/HA712X/BikeProjectTeam7/Code/Data/Data_EcoCompt_clean/"

# Vérifier si le dossier existe
if not os.path.isdir(dossier):
    print(f"Le dossier spécifié n'existe pas : {dossier}")
else:
    # Trouver tous les fichiers CSV dans le dossier
    fichiers_csv = glob.glob(os.path.join(dossier, "*.csv"))
    print(f"Fichiers CSV trouvés : {fichiers_csv}")

    if fichiers_csv:
        # Lire et combiner les fichiers CSV
        dfs = [pd.read_csv(fichier) for fichier in fichiers_csv]
        df_combine = pd.concat(dfs, ignore_index=True)

        # Sauvegarder le fichier combiné
        df_combine.to_csv(os.path.join(dossier, "fichier_combined.csv"), index=False)
        print("Les fichiers ont été combinés avec succès.")
    else:
        print("Aucun fichier CSV trouvé dans le dossier.")
#########################################################################################
# %%
import os
# Vérification si le fichier existe
file_path = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Data/Data_EcoCompt_clean/fichier_combined.csv'
file_exists = os.path.exists(file_path)
print(f"Le fichier existe-t-il ? {file_exists}")

# Si le fichier existe, essayer de le charger
if file_exists:
    data = pd.read_csv(file_path, sep=';')
    print(data.head())  # Affiche les premières lignes pour vérifier le contenu
########################################################################################
# %%
print(data.describe())

######################################################################################
# %%
from sklearn.metrics import root_mean_squared_error

# Calculer le RMSE
rmse = root_mean_squared_error(y_test, y_pred)

print(f"Erreur quadratique moyenne (RMSE) : {rmse}")
 
###################################################################################
# %%
import matplotlib.pyplot as plt

# Visualiser la distribution de la variable cible
plt.hist(data['intensity'], bins=50)
plt.title('Distribution de l\'intensité')
plt.xlabel('Intensité')
plt.ylabel('Fréquence')
plt.show()

######################################################################################
#Traitement des variables continues (longitude, latitude)
# %%
from sklearn.preprocessing import StandardScaler

# Standardisation des variables continues
scaler = StandardScaler()
data[['longitude', 'latitude']] = scaler.fit_transform(data[['longitude', 'latitude']])

#######################################################################################
#crer week et semaine
# %%
data['weekend'] = data['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

##############################################################################################
# Moyenne et ecart type
# %%
from sklearn.model_selection import cross_val_score

# Validation croisée pour évaluer le modèle
cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')

# Afficher la moyenne et l'écart-type des scores de la validation croisée
print(f'Mean CV score: {-cv_scores.mean()}')
print(f'Standard deviation of CV score: {cv_scores.std()}')


# %%
from sklearn.model_selection import GridSearchCV

# Paramètres à tester
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(estimator=RandomForestRegressor(random_state=42), param_grid=param_grid, cv=5, n_jobs=-1)
grid_search.fit(X_train, y_train)

print(f"Meilleurs paramètres : {grid_search.best_params_}")



###########################################################################################
#%%
# Affichage des prévisions pour les premières lignes de l'ensemble de test
print("Prévisions de l'intensité (pour l'ensemble de test) :")
print(y_pred[:10])  # Affiche les 10 premières prévisions

###############################################################################
#Vérifier si tous les mêmes valeurs
# %%
# Afficher les valeurs uniques de chaque colonne
print("Valeurs uniques de 'type':", data['type'].unique())
print("Valeurs uniques de 'vehicleType':", data['vehicleType'].unique())
print("Valeurs uniques de 'reversedLane':", data['reversedLane'].unique())

#########################################################################################
# Code pour les prédictions intensités
# %%
import pandas as pd
import numpy as np

# Dernière date de votre jeu de données
last_date = data['date'].max()

# Générer des dates futures (1er novembre 2023 à 31 décembre 2024, soit 15 mois de prévision)
future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), end='2024-12-31', freq='MS')  # 'MS' : début de chaque mois

# Créer un DataFrame avec ces dates futures
future_data = pd.DataFrame({
    'date': future_dates,
    'laneId': [label_encoder.transform([lane])[0] for lane in ['10429699']*len(future_dates)],  # Exemple pour laneId, répété pour chaque date
    'longitude': [3.893790]*len(future_dates),  # Exemple pour longitude
    'latitude': [43.629590]*len(future_dates),  # Exemple pour latitude
})

# Extraire les caractéristiques temporelles pour ces nouvelles dates
future_data['day_of_week'] = future_data['date'].dt.dayofweek
future_data['month'] = future_data['date'].dt.month
future_data['year'] = future_data['date'].dt.year
future_data['day'] = future_data['date'].dt.day
future_data['hour'] = future_data['date'].dt.hour

# Variables indépendantes pour la prédiction
X_future = future_data[['laneId', 'longitude', 'latitude', 'day_of_week', 'month', 'year', 'day', 'hour']]

# Faire les prévisions sur ces nouvelles données
future_predictions = model.predict(X_future)

# Afficher les prévisions
future_data['predicted_intensity'] = future_predictions
print(future_data[['date', 'predicted_intensity']])





# %%
import pandas as pd
import numpy as np
import folium
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor

# Charger votre fichier CSV
data = pd.read_csv("fichier_combined.csv", delimiter=';')
data['date'] = pd.to_datetime(data['date'])

# Encoder les laneId si nécessaire (ici nous assumons qu'ils sont déjà numériques ou encodés)
label_encoder = LabelEncoder()
data['laneId'] = label_encoder.fit_transform(data['laneId'])

# Extraire les caractéristiques et la cible
X = data[['laneId', 'longitude', 'latitude', 'day_of_week', 'month', 'year', 'day', 'hour']]
y = data['intensity']

# Entraîner le modèle
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Dernière date de votre jeu de données
last_date = data['date'].max()

# Générer des dates futures pour la prévision (de novembre 2023 à décembre 2024)
future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), end='2024-12-31', freq='MS')

# Liste des `laneId` (routes) à prédire, extraite directement du fichier CSV
lane_ids = data['laneId'].unique()  # Récupérer tous les laneId uniques du fichier

# Créer un DataFrame pour les données futures
future_data = pd.DataFrame({
    'date': np.tile(future_dates, len(lane_ids)),  # Répéter les dates pour chaque laneId
    'laneId': np.repeat(lane_ids, len(future_dates)),  # Répéter les laneIds pour chaque date
})

# Ajouter les coordonnées (latitude, longitude) pour chaque laneId
lane_coords = data[['laneId', 'longitude', 'latitude']].drop_duplicates()
future_data = pd.merge(future_data, lane_coords, on='laneId', how='left')

# Extraire les caractéristiques temporelles
future_data['day_of_week'] = future_data['date'].dt.dayofweek
future_data['month'] = future_data['date'].dt.month
future_data['year'] = future_data['date'].dt.year
future_data['day'] = future_data['date'].dt.day
future_data['hour'] = future_data['date'].dt.hour

# Variables indépendantes pour la prédiction
X_future = future_data[['laneId', 'longitude', 'latitude', 'day_of_week', 'month', 'year', 'day', 'hour']]

# Faire les prévisions sur ces nouvelles données
future_predictions = model.predict(X_future)

# Ajouter les prédictions au DataFrame
future_data['predicted_intensity'] = future_predictions

# Afficher les résultats des prévisions
print(future_data[['date', 'laneId', 'longitude', 'latitude', 'predicted_intensity']])

# Créer une carte Folium centrée sur une position générique (ici Montpellier)
map_center = [43.629590, 3.893790]  # Centré sur Montpellier, exemple de coordonnées
mymap = folium.Map(location=map_center, zoom_start=12)

# Ajouter des cercles sur la carte pour chaque prédiction
for _, row in future_data.iterrows():
    folium.Circle(
        location=[row['latitude'], row['longitude']],
        radius=50,  # Rayon du cercle, ajustez selon l'intensité
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=f"Date: {row['date']}<br>Lane ID: {row['laneId']}<br>Intensity: {row['predicted_intensity']:.2f}"
    ).add_to(mymap)

# Sauvegarder la carte sous forme de fichier HTML
mymap.save("predictions_map.html")

# %%
