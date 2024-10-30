import json
import pandas as pd
from datetime import datetime
import os
import glob

def convert_json_to_csv(input_file, output_dir):
    # Créer le nom du fichier de sortie dans le dossier data_clean
    input_filename = os.path.basename(input_file)
    output_filename = input_filename.replace('.json', '.csv')
    output_file = os.path.join(output_dir, output_filename)
    
    # Lire le fichier et stocker les données
    data_list = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            for line in file:
                # Ignorer les lignes vides
                if line.strip():
                    try:
                        # Charger l'objet JSON
                        json_obj = json.loads(line.strip())
                        
                        # Extraire les coordonnées
                        longitude = json_obj['location']['coordinates'][0]
                        latitude = json_obj['location']['coordinates'][1]
                        
                        # Extraire la date (première partie de dateObserved)
                        date = json_obj['dateObserved'].split('T')[0]
                        
                        # Créer un dictionnaire aplati
                        flat_data = {
                            'intensity': json_obj['intensity'],
                            'laneId': json_obj['laneId'],
                            'date': date,
                            'longitude': longitude,
                            'latitude': latitude,
                            'id': json_obj['id'],
                            'type': json_obj['type'],
                            'vehicleType': json_obj['vehicleType'],
                            'reversedLane': json_obj['reversedLane']
                        }
                        data_list.append(flat_data)
                    except json.JSONDecodeError as e:
                        print(f"Erreur lors du décodage d'une ligne dans {input_filename}")
                        print(f"Erreur : {e}")
                        continue
        
        # Si aucune donnée n'a été trouvée, lever une exception
        if not data_list:
            raise ValueError("Aucune donnée valide trouvée dans le fichier")
        
        # Convertir en DataFrame pandas
        df = pd.DataFrame(data_list)
        
        # Convertir la colonne date en format datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Filtrer les données pour avril-octobre 2023
        mask = (df['date'] >= '2023-04-01') & (df['date'] <= '2023-10-31')
        df_filtered = df.loc[mask]
        
        # Trier par date
        df_filtered = df_filtered.sort_values('date')
        
        # Reconvertir la date en format string YYYY-MM-DD pour le CSV
        df_filtered['date'] = df_filtered['date'].dt.strftime('%Y-%m-%d')
        
        # Sauvegarder en CSV avec des paramètres explicites
        df_filtered.to_csv(output_file, 
                          index=False,
                          sep=';',
                          encoding='utf-8-sig',
                          float_format='%.6f')
        
        print(f"\nConversion réussie : {input_filename} -> {output_filename}")
        print(f"Nombre d'enregistrements : {len(df_filtered)}")
        print(f"Période : du {df_filtered['date'].min()} au {df_filtered['date'].max()}")
        
        return True
        
    except Exception as e:
        print(f"\nErreur lors du traitement de {input_filename}")
        print(f"Erreur : {str(e)}")
        return False

def process_all_json_files():
    # Définir les chemins des dossiers
    current_directory = os.getcwd()
    input_dir = os.path.join(current_directory, 'data')
    output_dir = os.path.join(current_directory, 'data_clean')
    
    # Vérifier si le dossier d'entrée existe
    if not os.path.exists(input_dir):
        print(f"Erreur : Le dossier 'data' n'existe pas dans {current_directory}")
        return
    
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Dossier 'data_clean' créé dans {current_directory}")
    
    # Chercher tous les fichiers .json dans le dossier data
    json_files = glob.glob(os.path.join(input_dir, '*.json'))
    
    if not json_files:
        print("Aucun fichier .json trouvé dans le dossier 'data'.")
        return
    
    print(f"Nombre de fichiers .json trouvés : {len(json_files)}")
    
    # Compteurs pour le rapport
    success_count = 0
    error_count = 0
    
    # Traiter chaque fichier
    for json_file in json_files:
        print(f"\nTraitement de : {os.path.basename(json_file)}")
        if convert_json_to_csv(json_file, output_dir):
            success_count += 1
        else:
            error_count += 1
    
    # Afficher le rapport final
    print("\n=== Rapport de conversion ===")
    print(f"Fichiers traités avec succès : {success_count}")
    print(f"Fichiers avec erreurs : {error_count}")
    print(f"Total des fichiers : {len(json_files)}")
    print(f"\nLes fichiers CSV ont été sauvegardés dans : {output_dir}")

# Exécuter le traitement
if __name__ == "__main__":
    print("Début du traitement des fichiers JSON...")
    process_all_json_files()
    print("\nTraitement terminé.")