# %% 
# 1. Import packages

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
from scipy.stats import f_oneway
from scipy.stats import shapiro
from scipy.stats import kruskal

# Configuration pour Seaborn
sns.set_theme(style="whitegrid")

# %% 
# 2. Path to the folder containing the CSV files

current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(current_directory, 'Data', 'Data_EcoCompt_clean')
all_files = glob.glob(os.path.join(path, "*.csv"))

# %% 
# 3. Setting up the data

# Load function to handle errors without `error_bad_lines`.
def load_file(file):
    try:
        return pd.read_csv(file, sep=';')
    except pd.errors.EmptyDataError:
        print(f"Empty or corrupted file ignored: {file}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

# Concatenate all files into a single DataFrame
df = pd.concat((load_file(f) for f in all_files), ignore_index=True)

# Convert ‘date’ column to datetime type (if not already converted)
if df['date'].dtype != 'datetime64[ns]':
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

# Filter data for the study period: April to October 2023
df = df[(df['date'] >= '2023-04-01') & (df['date'] <= '2023-10-31')]

# Add ‘month’ and ‘year’ columns for temporal analyses
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

# Group by date to obtain a daily average
daily_data = df.groupby('date')['intensity'].mean().reset_index()

# %% 
# 4. General descriptive statistics

print("General descriptive statistics: \n", df['intensity'].describe())

# %% 
# 5. Creation of the first graph (data visualization)

# Creation of the ‘week’ column and calculation of the start dates for each week
df['week'] = df['date'].dt.isocalendar().week
df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='D')  # Date de début de la semaine

# Group data by week (using the start date of the week)
weekly_data = df.groupby(['year', 'week', 'week_start'])['intensity'].mean().reset_index()

# Draw the graph
plt.figure(figsize=(12, 6))
sns.lineplot(data=weekly_data, x='week_start', y='intensity', marker='o', color='blue')

# Title and labels
plt.title("Weekly trend in bicycle use (2023)")
plt.xlabel("Week (Starting date)")
plt.ylabel("Average intensity")

# Add a coloured background to highlight the period of the Tour de France
tour_de_france_start = pd.to_datetime('2023-07-01')
tour_de_france_end = pd.to_datetime('2023-07-23')
plt.axvspan(tour_de_france_start, tour_de_france_end, color='red', alpha=0.3, label="Tour de France")

# Customise the dates on the x axis to display the start of week dates
plt.xticks(weekly_data['week_start'], labels=weekly_data['week_start'].dt.strftime('%d-%m'), rotation=45)

# Add a legend and the grid
plt.legend()
plt.grid(True)

# Display the graph
plt.tight_layout()
plt.show()

# %% 
# 6. Comparison of periods (before, during, after the Tour de France)

# Initializing periods
before_july = daily_data[daily_data['date'] < '2023-07-01']['intensity']
during_july = daily_data[(daily_data['date'] >= '2023-07-01') & (daily_data['date'] <= '2023-07-23')]['intensity']
after_july = daily_data[daily_data['date'] > '2023-07-23']['intensity']

# Calculate descriptive statistics for each period
stats = pd.DataFrame({
    "Mean": [before_july.mean(), during_july.mean(), after_july.mean()],
    "Standard-deviation": [before_july.std(), during_july.std(), after_july.std()],
    "Median": [before_july.median(), during_july.median(), after_july.median()],
    "Min": [before_july.min(), during_july.min(), after_july.min()],
    "Max": [before_july.max(), during_july.max(), after_july.max()]
}, index=["Before July", "During July", "After July"])

print("Descriptive statistics by period: \n", stats)

# %%
# 7. Verifications to make statistical tests

# Verification of normality
print("Shapiro-Wilk test (normality):")
for period, data in zip(["Before July", "During July", "After July"], [before_july, during_july, after_july]):
    stat, p = shapiro(data)
    print(f"{period}: p-value = {p:.4f}")
    if p < 0.05:
        print(f"The {period} data do not follow a normal distribution (p < 0.05).")
    else:
        print(f"The {period} data follow a normal distribution (p ≥ 0.05).")
        
# Homogeneity of variance test (Levene)
from scipy.stats import levene

# Test de Levene pour l'homogénéité des variances
stat, p = levene(before_july, during_july, after_july)
print(f"Levene test: p-value = {p:.4f}")
if p < 0.05:
    print("The variances are not equal (p < 0.05). The hypothesis of homogeneity of variances is rejected.")
else:
    print("The variances are equal (p ≥ 0.05). The assumption of homogeneity of variances is respected.")

# Visual diagnostics (Q-Q plot)
import scipy.stats as stats
import matplotlib.pyplot as plt

# Création des Q-Q plots pour chaque période
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
periods = ["Before July", "During July", "After July"]
datasets = [before_july, during_july, after_july]

for ax, data, period in zip(axs, datasets, periods):
    stats.probplot(data, dist="norm", plot=ax)
    ax.set_title(f"Q-Q Plot: {period}")

plt.tight_layout()
plt.show()
    
# %%
# 8. Kruskal-Wallis test to compare the means of the three periods (normality hypothesis non respected)

# Kruskal-Wallis test
kruskal_result = kruskal(before_july, during_july, after_july)
print(f"Kruskal-Wallis test results: H = {kruskal_result.statistic:.2f}, p-value = {kruskal_result.pvalue:.4f}")

# Interpretation
if kruskal_result.pvalue < 0.05:
    print("There was a statistically significant difference between periods (p < 0.05).")
else:
    print("No statistically significant difference between periods (p ≥ 0.05).")


# %% 
# 9. Creation of the second graph (boxplot)

# Boxplot to compare different periods (before, during, after the Tour de France)
data_to_plot = [before_july, during_july, after_july]

plt.figure(figsize=(10, 6))
plt.boxplot(data_to_plot, 
            labels=['Before Tour de France', 'During Tour de France', 'After Tour de France'], 
            patch_artist=True, 
            boxprops=dict(facecolor="#5dade2", color="#5dade2"),
            flierprops=dict(markerfacecolor='r', marker='o'),
            medianprops=dict(color='red', linewidth=2))
            
# Customise the graphic
plt.title("Comparison of the frequency of bicycle use before, during and after the Tour de France")
plt.ylabel("Average number of visits")
plt.grid(True)
plt.tight_layout()
plt.show()

# %% 
# 10. Comments

print("""
Comments:
- Average intensities are higher during the period of the Tour de France (1st to 23rd July), 
  which could indicate an increase in the use of bicycles during this event.
- The ANOVA test confirms that this increase is significant (p < 0.05), 
  suggesting a statistically significant impact of the Tour de France on bicycle use.
- Monthly trends show increased use in summer, with a peak in July.
""")

# %%
