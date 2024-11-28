#%%
import pandas as pd
import glob
import os

# Chemin relatif vers le dossier de données, basé sur le dossier actuel du script
dossier = os.path.join(os.path.dirname(__file__), "..", "Data", "Data_EcoCompt_clean")

# Obtenez la liste de tous les fichiers CSV dans le dossier
file_paths = glob.glob(os.path.join(dossier, "*.csv"))

# Afficher les fichiers trouvés pour vérifier que le chemin fonctionne
print("Fichiers trouvés :", file_paths)

# Vérifiez si des fichiers ont été trouvés
if not file_paths:
    raise ValueError("Aucun fichier CSV n'a été trouvé dans le dossier spécifié.")

# Charger et concaténer tous les fichiers CSV
all_data = pd.concat([pd.read_csv(file, sep=';') for file in file_paths])

# Enregistrer dans un fichier CSV combiné dans le même dossier ou un autre répertoire de votre choix
output_path = os.path.join(os.path.dirname(__file__), "fichier_combined.csv")
all_data.to_csv(output_path, index=False, sep=';')

print(f"Tous les fichiers dans le dossier ont été combinés avec succès dans {output_path}")

# %%
