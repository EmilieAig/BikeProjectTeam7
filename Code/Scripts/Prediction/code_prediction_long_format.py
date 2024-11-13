
# %%
import os
import pandas as pd

# Chargement des données de prédictions
data_path = 'predictions_bike_intensity1.csv'
predictions_df = pd.read_csv(data_path, sep=';')

# Répertoire de sortie pour le fichier transformé
output_dir = 'Code/Scripts/Prediction'

# Vérifier si le répertoire existe, sinon le créer
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Transformer les données en format long
# La première colonne est la date, et les autres sont les écocompteurs avec leurs intensités
melted_df = pd.melt(predictions_df, id_vars=['date'], var_name='laneId', value_name='predicted_intensity')

# Conversion de la date en format datetime
melted_df['date'] = pd.to_datetime(melted_df['date'])

# Sauvegarde du DataFrame dans un nouveau fichier CSV au format long
output_path = os.path.join(output_dir, 'predictions_long_format.csv')
melted_df.to_csv(output_path, index=False, sep=';')

print(f"Transformation terminée et sauvegardée sous '{output_path}'")

# %%
