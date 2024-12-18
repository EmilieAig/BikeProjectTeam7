#  Scripts folder description:

This file contains all the code scripts we created to successfully complete our project.

Before running the scripts we will describe below, the first step is to run the requirements.txt file (detailed explanations in the file) present at the root of the project to create the associated virtual environment and install the packages you will need to run the code.

### Animation_Bike.py 
   This file contains a Python class that allowed us to create the video of cyclists' trips, visualizing their movements over time.

 ⚠️ **Execution Time Notice**

⏳ **This script requires at least 2 hours to execute.You must execute the code in the terminal for it to run properly.**

### Statistics.py
   In this file, you’ll find the code used to perform statistical analysis on our data to address our research question, helping us derive insights and conclusions.

### data_treatment_EcoCompt.py
   This file contains the code responsible for converting the bicycle counters' data from JSON to CSV format, making it easier to work with and analyze.

### ecoCompt_Download_and_Combine.py  
   This file is designed to streamline the process of downloading, cleaning, filtering, and merging counter data from the website in one step, allowing users to directly download the latest data from the site.

### map.py  
   This file contains the code used to generate maps and visualizations related to the bike counters and stations.   

## Prediction

Go to the [Readme of the Prediction folder](Prediction/Readme.md) to know the steps to generate the prediction map.

### code_eco_coord.py
   This file processes the data related to the eco-counters, which contain information about bike paths (path ID, GPS coordinates). It renames the columns and prepares the data to merge with the traffic predictions in the other files.

### code_prediction_july.py
   This file allows to filter the predictions for the period from July 10 to 16 and prepares the data for analysis by merging it with the eco-counter data.

### code_prediction_long_format_july.py
   This file contains the code to handle traffic predictions in a specific data format (long format), in order to make the data compatible with those in other files for display on the map.

### code_bike_traffic_prediction.py
   This file contains the code that is responsible for creating an interactive map that visualizes the paths between data points and bike stations, coloring the paths based on traffic intensity from July 10 to 16, 2023.
