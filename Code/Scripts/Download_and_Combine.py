import os
import pooch
import requests # obtenir le contenu de la page web
from bs4 import BeautifulSoup # transforme le contenu HTML en une structure navigable, facilitant l'extraction des liens spécifiques aux fichiers
import numpy as np
import glob
import calendar
import json
from datetime import datetime
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from cycler import cycler
from IPython import get_ipython

sns.set_palette("colorblind")
palette = sns.color_palette("twilight", n_colors=12)
pd.options.display.max_rows = 8

## data processing

# %%下载
# 基础 URL 和下载目录
base_url = "https://data.montpellier3m.fr/sites/default/files/ressources/"
page_url = "https://data.montpellier3m.fr/dataset/comptages-velo-et-pieton-issus-des-compteurs-de-velo"  
path_target = "../Data/Data_EcoCompt/"

# 获取包含文件列表的网页
response = requests.get(page_url)
soup = BeautifulSoup(response.text, 'html.parser')

# 查找所有符合条件的文件链接
file_links = []
for link in soup.find_all('a'):
    href = link.get('href')
    if href and href.startswith(base_url) and "MMM_EcoCompt_" in href and href.endswith("_archive.json"):
        file_links.append(href)

# 下载符合条件的文件
for url in file_links:
    file_name = url.split("/")[-1]
    full_path = os.path.join(path_target, file_name)

    # 删除文件（如果存在）
    if os.path.exists(full_path):
        os.remove(full_path)
        print(f"删除已存在文件: {full_path}")
    
    # 重新下载
    print(f"正在下载 {file_name}...")
    pooch.retrieve(
        url,
        path=path_target,
        fname=file_name,
        known_hash=None,
    )
    
print("所有符合条件的文件下载完成！")


## data treatment 


# %% Conversion and selection of data 

def convert_json_to_csv(input_file, output_dir):
    # Create output file name in data_clean folder
    input_filename = os.path.basename(input_file)
    output_filename = input_filename.replace('.json', '.csv')
    output_file = os.path.join(output_dir, output_filename)
    
    # Read file and store data
    data_list = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            # Read the file line by line
            for line in file:
                # Ignore empty lines
                line = line.strip()
                if not line:
                    continue
                    
                # Separate JSON objects that could be glued together
                json_strings = line.replace('}{', '}\n{').split('\n')
                
                for json_str in json_strings:
                    try:
                        if not json_str.strip():
                            continue
                        # Load JSON object   
                        json_obj = json.loads(json_str)
                        
                        # Vérifier si des valeurs importantes sont nulles
                        if any(json_obj.get(key) is None for key in ['intensity', 'laneId', 'dateObserved', 'location', 'id', 'type', 'vehicleType', 'reversedLane']):
                            continue
                            
                        # Vérifier si les coordonnées sont nulles
                        if json_obj['location'].get('coordinates') is None or None in json_obj['location']['coordinates']:
                            continue
                        
                        # Extract date
                        date = json_obj['dateObserved'].split('T')[0]
                        
                        # Creating a flattened dictionary
                        flat_data = {
                            'intensity': json_obj['intensity'],
                            'laneId': json_obj['laneId'],
                            'date': date,
                            # Extract coordinates
                            'longitude': json_obj['location']['coordinates'][0],
                            'latitude': json_obj['location']['coordinates'][1],
                            'id': json_obj['id'],
                            'type': json_obj['type'],
                            'vehicleType': json_obj['vehicleType'],
                            'reversedLane': json_obj['reversedLane']
                        }
                        
                        # Vérifier si une des valeurs du dictionnaire est nulle
                        if any(value is None for value in flat_data.values()):
                            continue
                        
                        data_list.append(flat_data)
                    except json.JSONDecodeError as e:
                        print(f"JSON decoding error: {str(e)}\nIn the object: {json_str[:50]}...")
                        continue
                    except KeyError as e:
                        print(f"Key missing from object: {str(e)}")
                        continue
        
        # If no data was found, raise an exception
        if not data_list:
            raise ValueError("No valid data found in the file")
        
        # Convert to DataFrame pandas
        df = pd.DataFrame(data_list)
        
        # If the DataFrame is empty, stop and return False
        if df.empty:
            print(f"No data to save for {input_filename}. The file will not be created.")
            return False
        
        # Supprimer les lignes contenant des valeurs nulles
        df = df.dropna()
        
        # Convert date column to datetime format
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter data for April-October 2023
        mask = (df['date'] >= '2023-04-01') & (df['date'] <= '2023-10-31')
        df_filtered = df.loc[mask]
        
        # Sort by date
        df_filtered = df_filtered.sort_values('date')
        
        # Convert date back to string format YYYY-MM-DD for CSV
        df_filtered['date'] = df_filtered['date'].dt.strftime('%Y-%m-%d')
        
        # Save as CSV with explicit parameters
        df_filtered.to_csv(output_file, 
                          index=False,
                          sep=';',
                          encoding='utf-8-sig',
                          float_format='%.6f')
        
        # Print success message before returning
        print(f"\nSuccessful conversion: {input_filename} -> {output_filename}")
        print(f"Total number of recordings: {len(data_list)}")
        print(f"Number of recordings in the period: {len(df_filtered)}")
        if not df_filtered.empty:
            print(f"Période: du {df_filtered['date'].min()} au {df_filtered['date'].max()}")
        
        # Indique le succès de la conversion
        return True if not df_filtered.empty else False
        
    except Exception as e:
        print(f"\nError when processing {input_filename}")
        print(f"Error: {str(e)}")
        return False

# %% Detection of file to analyse and folder to save data clean

def process_all_json_files():
    # Define folder paths
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(current_directory, 'Data', 'Data_EcoCompt')
    output_dir = os.path.join(current_directory, 'Data', 'Data_EcoCompt_clean')

    
    # Check if the entry file exists
    if not os.path.exists(input_dir):
        print(f"Error: folder 'data' doesn't exists in {current_directory}")
        return
    
    # Create output folder if none exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Folder 'data_clean' created in {current_directory}")
    
    # Search for all .json files in the data folder
    json_files = glob.glob(os.path.join(input_dir, '*.json'))
    
    if not json_files:
        print("No .json files found in the 'data' folder.")
        return
    
    print(f"Number of .json files found: {len(json_files)}")
    
    # Report counters
    success_count = 0
    error_count = 0
    
    # Process each file
    for json_file in json_files:
        print(f"\nTreatment of: {os.path.basename(json_file)}")
        # Si la conversion échoue, supprimer le fichier CSV créé
        if not convert_json_to_csv(json_file, output_dir):
            output_filename = os.path.basename(json_file).replace('.json', '.csv')
            output_file = os.path.join(output_dir, output_filename)
            if os.path.exists(output_file):
                os.remove(output_file)
                print(f"{output_filename} deleted as empty.")
            error_count += 1
        else:
            success_count += 1
    
    # View final report
    print("\n=== Conversion report ===")
    print(f"Files successfully processed: {success_count}")
    print(f"Files without registration for the desired period: {error_count}")
    print(f"Total files: {len(json_files)}")
    print(f"\nThe CSV files have been saved in: {output_dir}")

# %% Run the treatment

if __name__ == "__main__":
    print("Start processing JSON files...")
    process_all_json_files()
    print("\nTreatment completed.")


# %%
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
# 构造新的输出路径
output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data", "Data_EcoCompt_Combined", "fichier_combined.csv")

# 如果目标文件夹不存在，则创建
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# 保存合并后的数据到指定位置
all_data.to_csv(output_path, index=False, sep=';')

print(f"Tous les fichiers dans le dossier ont été combinés avec succès dans {output_path}")
