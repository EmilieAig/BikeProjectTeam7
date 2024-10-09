# BikeProjectTeam7
This is our project of the UE HAX712X for the year 2024-2025.
The name of our project is BikeProjectTeam7.
The members of the group are :
- AIGOIN Emilie
- MAMANE SIDI Samira
- THOMAS Anne-Laure
- ZHU Qingjian
1. ## Introduction:  
Our project will focus on the following question: "What is the impact of the 2023 Tour de France on bicycle usage in Montpellier, and how have cyclists' behaviors evolved before and after this major event?". The goal is to analyze whether this sporting event, which took place in July 2023, had a significant effect on cycling in the city and if there were notable changes in cycling habits.

To conduct this study, we have chosen to analyze data on bicycle usage spanning from April to October 2023. This time frame allows us to examine bike traffic before, during, and after the Tour de France, providing a comprehensive view of usage patterns around this event. The selection of this period is crucial for capturing short-term trends related to the Tour and distinguishing them from seasonal or contextual factors that might also influence cycling behavior.

Through this analysis, we aim to provide a clear and detailed understanding of how cyclists' behaviors in Montpellier have evolved in relation to this major sporting event.
2. ## Description of our project:
a. Architecture
The project will have the following structure:

    **Front-end (website)**:
        A website where users can browse and interact with various visualizations.
        The site will feature charts and an interactive map displaying bike traffic predictions for Montpellier.

    **Back-end (data processing)**:
        Data analysis from April to October 2023, based on bike counting data, public bike-sharing trip data, and OpenStreetMap data.
        A prediction model based on time series analysis (using tools like Prophet, ARIMA, or Machine Learning methods) to forecast bike traffic for the coming days.
b. Main Files:
The different files,we will use are the following:
    **data/**: Folder containing the data files (CSV, JSON, etc.).  
	**src/**: The source code, with subfolders for:
        *data_processing.py: For cleaning and structuring the data.
        model_training.py: For training the prediction model.
        visualization.py: For generating charts and maps.
        web_app.py: The script responsible for generating the website.*
c. Development Pipeline

The development pipeline will be divided into several stages:
- **Data Collection**: Import and clean data from various datasets (VéloMagg, bike/pedestrian counts, OpenStreetMap).
- **Preprocessing**: Filter the data, handle missing values, and merge the different data sources.
- **Visualization of Historical Data**: Create time series charts and maps showing bike traffic from April to October 2023.
- **Modeling and Prediction**: Train a model to forecast bike traffic for the upcoming days.
- **Website Development**: Integrate visualizations and the prediction model into an interactive website.
d. Technologies and Packages Used
- **Primary Language**: Python
- **Packages**:
    **For data management and analysis**: Pandas, NumPy
    **For visualization**: Matplotlib, Seaborn, Plotly (for interactive charts), Folium or Leaflet.js (for the interactive map)
    **For modeling and prediction**: scikit-learn, Prophet (or ARIMA)
    **For the website**: Flask or Streamlit
e.The Grantt chart
We will also create a Gantt chart to illustrate the project's timeline and track its progress over time. This diagram will help visualize each phase of the project, from data collection to website development, allowing us to monitor deadlines, dependencies, and milestones clearly.