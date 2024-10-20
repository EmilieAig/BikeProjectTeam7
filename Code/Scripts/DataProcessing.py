# %%
import os
import numpy as np
import calendar
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from cycler import cycler
import pooch  # download data / avoid re-downloading
from IPython import get_ipython


sns.set_palette("colorblind")
palette = sns.color_palette("twilight", n_colors=12)
pd.options.display.max_rows = 8
# %%
url = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/DataBike2023.csv"

path_target = "./DataBike2023.csv"
path, fname = os.path.split(path_target)
pooch.retrieve(url, path=path, fname=fname, known_hash=None)  # if needed `pip install pooch`
# %%
df_DataBike_raw = pd.read_csv(url)
df_DataBike_raw.head(n=10)
# %%
