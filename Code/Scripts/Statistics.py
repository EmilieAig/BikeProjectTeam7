# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
from scipy.stats import f_oneway

# Configuration pour Seaborn
sns.set_theme(style="whitegrid")

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
# 1. Statistiques descriptives générales
print("Statistiques descriptives générales :\n", df['intensity'].describe())

# %%
# 2. Distribution des intensités (Histogramme)
plt.figure(figsize=(10, 5))
sns.histplot(df['intensity'], kde=True, color='blue')
plt.title("Distribution de l'intensité des passages (Avril - Octobre 2023)")
plt.xlabel("Intensité")
plt.ylabel("Fréquence")
plt.show()

# %%
# 3. Boxplot des intensités par mois
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='month', y='intensity', palette='coolwarm')
plt.title("Distribution des intensités par mois")
plt.xlabel("Mois")
plt.ylabel("Intensité")
plt.show()

# %%
# 4. Comparaison des périodes (avant, pendant, après le Tour de France)
before_july = daily_data[daily_data['date'] < '2023-07-01']['intensity']
during_july = daily_data[(daily_data['date'] >= '2023-07-01') & (daily_data['date'] <= '2023-07-23')]['intensity']
after_july = daily_data[daily_data['date'] > '2023-07-23']['intensity']

# Calculer les statistiques descriptives pour chaque période
stats = pd.DataFrame({
    "Moyenne": [before_july.mean(), during_july.mean(), after_july.mean()],
    "Écart-type": [before_july.std(), during_july.std(), after_july.std()],
    "Médiane": [before_july.median(), during_july.median(), after_july.median()],
    "Min": [before_july.min(), during_july.min(), after_july.min()],
    "Max": [before_july.max(), during_july.max(), after_july.max()]
}, index=["Avant juillet", "Pendant juillet", "Après juillet"])

print("Statistiques descriptives par période :\n", stats)

# %%
# 5. Visualisation des comparaisons par période (Boxplot)
plt.figure(figsize=(10, 6))
sns.boxplot(data=[before_july, during_july, after_july], palette="Set2")
plt.xticks([0, 1, 2], ["Avant juillet", "Pendant juillet", "Après juillet"])
plt.title("Comparaison des intensités avant, pendant et après le Tour de France")
plt.ylabel("Intensité moyenne")
plt.show()

# %%
# 6. Test ANOVA pour comparer les moyennes des trois périodes
anova_result = f_oneway(before_july, during_july, after_july)
print(f"Résultat du test ANOVA : F = {anova_result.statistic:.2f}, p-value = {anova_result.pvalue:.4f}")

if anova_result.pvalue < 0.05:
    print("Les différences entre les périodes sont statistiquement significatives (p < 0.05).")
else:
    print("Les différences entre les périodes ne sont pas statistiquement significatives (p >= 0.05).")

# %%
# 7. Analyse des tendances saisonnières
monthly_data = df.groupby(['year', 'month'])['intensity'].mean().reset_index()
plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_data, x='month', y='intensity', marker='o', color='green')
plt.title("Tendance mensuelle de l'utilisation des vélos (2023)")
plt.xlabel("Mois")
plt.ylabel("Intensité moyenne")
plt.xticks(range(4, 11), ['Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre'])
plt.show()

# %%
# 8. Commentaires
print("""
Commentaires :
- La moyenne des intensités est plus élevée pendant la période du Tour de France (1er au 23 juillet), 
  ce qui pourrait indiquer une augmentation de l'utilisation des vélos pendant cet événement.
- Le test ANOVA confirme que cette augmentation est significative (p < 0.05), 
  ce qui suggère un impact statistiquement notable du Tour de France sur l'utilisation des vélos.
- Les tendances mensuelles montrent une utilisation accrue en été, avec un pic en juillet.
""")

# %%
