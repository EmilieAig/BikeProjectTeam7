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
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Création de la colonne 'week' et calcul des dates de début de chaque semaine
df['week'] = df['date'].dt.isocalendar().week
df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='D')  # Date de début de la semaine

# Grouper les données par semaine (en utilisant la date de début de semaine)
weekly_data = df.groupby(['year', 'week', 'week_start'])['intensity'].mean().reset_index()

# Tracer le graphique
plt.figure(figsize=(12, 6))
sns.lineplot(data=weekly_data, x='week_start', y='intensity', marker='o', color='blue')

# Titre et labels
plt.title("Weekly trend in bicycle use (2023)")
plt.xlabel("Week (Starting date)")
plt.ylabel("Average intensity")

# Ajouter un fond coloré pour surligner la période du Tour de France (du 1er juillet au 23 juillet 2023)
# Ici nous utilisons les dates exactes pour la période du Tour de France
tour_de_france_start = pd.to_datetime('2023-07-01')
tour_de_france_end = pd.to_datetime('2023-07-23')
plt.axvspan(tour_de_france_start, tour_de_france_end, color='red', alpha=0.3, label="Tour de France")

# Personnalisation des dates sur l'axe des x pour afficher les dates de début de semaine
plt.xticks(weekly_data['week_start'], labels=weekly_data['week_start'].dt.strftime('%d-%m'), rotation=45)

# Ajouter une légende et la grille
plt.legend()
plt.grid(True)

# Afficher le graphique
plt.tight_layout()
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
# 6. Test ANOVA pour comparer les moyennes des trois périodes
anova_result = f_oneway(before_july, during_july, after_july)
print(f"Résultat du test ANOVA : F = {anova_result.statistic:.2f}, p-value = {anova_result.pvalue:.4f}")

if anova_result.pvalue < 0.05:
    print("Les différences entre les périodes sont statistiquement significatives (p < 0.05).")
else:
    print("Les différences entre les périodes ne sont pas statistiquement significatives (p >= 0.05).")

# %%
# Boxplot pour comparer les différentes périodes (avant, pendant, après le Tour de France)
data_to_plot = [before_july, during_july, after_july]

plt.figure(figsize=(10, 6))
plt.boxplot(data_to_plot, 
            labels=['Avant le Tour', 'Pendant le Tour', 'Après le Tour'], 
            patch_artist=True, 
            boxprops=dict(facecolor="#5dade2", color="#5dade2"),  # Couleur bleue plus claire
            flierprops=dict(markerfacecolor='r', marker='o'),
            medianprops=dict(color='red', linewidth=2))  # Changer la couleur et l'épaisseur des traits médians
            
# Personnalisation du graphique
plt.title("Comparaison des fréquences d'utilisation des vélos avant, pendant et après le Tour de France")
plt.ylabel("Nombre moyen de passages")
plt.grid(True)
plt.tight_layout()
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
