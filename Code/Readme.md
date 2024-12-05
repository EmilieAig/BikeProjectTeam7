# File Description:
In this document, we will describe the contents of each file located in the `Data` and `Scripts` directories.

# Data
This folder contains all the databases used to successfully carry out our project.

### Data_EcoCompt
   This file contains all the JSON files corresponding to data from various bicycle counters in Montpellier. These data were retrieved directly from the Open Data Montpellier website. Each file represents the data for a specific counter.
 
### Data_EcoCompt_Combined  
   This file contains the code we created to combine all the individual data from the JSON files in `Data_EcoCompt` into a single consolidated file. This code was designed to simplify data manipulation and analysis.

### Data_EcoCompt_clean 
   This file is the final result of combining and cleaning the data. It contains all the data from the bicycle counters in CSV format, ready to be used for statistical analyses or further processing.

### Video_Data
This file includes two CSV files: one containing the geographical data of Velomagg stations, and the other used to create the video.

# Scripts
This file contains all the code scripts we created to successfully complete our project:


### Animation_Bike.py 
   This file contains a Python class that allowed us to create the video of cyclists' trips, visualizing their movements over time.

### DataProcessing.py
   This file includes the code for cleaning and processing the initial data, ensuring it was ready for analysis and further use in the project.

### Statistics.py
   In this file, you’ll find the code used to perform statistical analysis on our data to address our research question, helping us derive insights and conclusions.

### data_treatment_EcoCompt.py
   This file contains the code responsible for converting the bicycle counters' data from JSON to CSV format, making it easier to work with and analyze.

### data_treatment_Velomag.py 
   This file includes the code used to clean the data from Velomagg stations, ensuring the dataset was accurate and ready for further processing.

### map.py  
   This file contains the code used to generate maps and visualizations related to the bike counters and stations.
