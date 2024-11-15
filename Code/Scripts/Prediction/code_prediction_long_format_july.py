#%%
import pandas as pd

# Chargement des données de prédictions
data_path = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/predictions_bike_intensity_july_week.csv'
predictions_df = pd.read_csv(data_path, sep=';')

# Transformation des données en format long
melted_df = pd.melt(predictions_df, id_vars=['date'], var_name='laneId', value_name='predicted_intensity')

# Conversion de la date en format datetime
melted_df['date'] = pd.to_datetime(melted_df['date'])

# Sauvegarde du DataFrame transformé dans un nouveau fichier CSV
output_path = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/predictions_long_format_july.csv'
melted_df.to_csv(output_path, index=False, sep=';')

print(f"Transformation terminée et sauvegardée sous '{output_path}'")

##########On voit que il y a un troue ##############################################################
# %%
import pandas as pd

# Chargement des données de prédictions
data_path = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/predictions_bike_intensity_july_week.csv'
predictions_df = pd.read_csv(data_path, sep=';')

# Vérifier les valeurs manquantes dans la colonne '253757735'
missing_values = predictions_df['253757735'].isna().sum()
print(f"Nombre de valeurs manquantes pour '253757735' : {missing_values}")

######################## Bon code ###############################################################################################

#%%
import pandas as pd

# Chargement des données de prédictions
data_path = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/predictions_bike_intensity_july_week.csv'
predictions_df = pd.read_csv(data_path, sep=';')

# Série de valeurs à remplacer pour les valeurs manquantes de '253757735'
replacement_values = [
    461.34576511247957, 562.0277158350742, 543.6324160701633, 537.5385273355084,
    401.0681366893027, 245.31856472538269, 168.9334585514308
]

# Identifier les indices où les valeurs sont manquantes pour la colonne '253757735'
missing_indices = predictions_df[predictions_df['253757735'].isna()].index

# Remplacer les valeurs manquantes par les valeurs spécifiques
for idx, value in zip(missing_indices, replacement_values):
    predictions_df.at[idx, '253757735'] = value

# Transformer les données en format long
melted_df = pd.melt(predictions_df, id_vars=['date'], var_name='laneId', value_name='predicted_intensity')

# Conversion de la date en format datetime
melted_df['date'] = pd.to_datetime(melted_df['date'])

# Sauvegarde du DataFrame transformé dans un nouveau fichier CSV
output_path = '/home/anne_laure/HA712X/BikeProjectTeam7/Code/Scripts/Prediction/predictions_long_format_july.csv'
melted_df.to_csv(output_path, index=False, sep=';')

print(f"Transformation terminée et sauvegardée sous '{output_path}'")
