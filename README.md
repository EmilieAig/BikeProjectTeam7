# BikeProjectTeam7
Welcome to our project for the HAX712X course for the academic year 2024-2025.
Our project is titled **BikeProjectTeam7**.\
The team members are :
- AIGOIN Emilie
- MAMANE SIDI Samira
- THOMAS Anne-Laure
- ZHU Qingjian

## Introduction:  
Our project will focus on the following question: "What is the impact of the 2023 Tour de France on bicycle usage in Montpellier, and how have cyclists' behaviors evolved before and after this major event?". The goal is to analyze whether this sporting event, which took place in July 2023, had a significant effect on cycling in the city and if there were notable changes in cycling habits.

To conduct this study, we have chosen to analyze data on bicycle usage spanning from April to October 2023. This time frame allows us to examine bike traffic before, during, and after the Tour de France, providing a comprehensive view of usage patterns around this event. The selection of this period is crucial for capturing short-term trends related to the Tour and distinguishing them from seasonal or contextual factors that might also influence cycling behavior.

Through this analysis, we aim to provide a clear and detailed understanding of how cyclists' behaviors in Montpellier have evolved in relation to this major sporting event.

By following this link, you will have access to our website, which showcases the entirety of our project:[BikeProjectTeam7](https://emilieaig.github.io/BikeProjectTeam7/)

### Project Documentation
You can view the full documentation for this project on our website.
Here is our current Gantt diagram:  
[Gantt Diagram](https://emilieaig.github.io/BikeProjectTeam7/Organization/Gantt_Diagram/Gantt_Diagram.html)  
Please follow the link below to access the details of our project:  
[README.md](https://github.com/EmilieAig/BikeProjectTeam7/blob/main/RoadMap/README.md)  
 
Here is a diagram of the architecture of our project, detailing the location of each folder and file:

```BikeProjectTeam7/
    ├── .github/workflows/
    │     └── publish.yml
    ├── Code/ 
    │     ├── Data/
    |     |     |── Data_EcoCompt/...
    |     |     |── Data_EcoCompt_Combined/
    |     |     |       ├── counter_coordinates.csv
    |     |     |       |── fichier_combined.csv
    |     |     |       |── node_intensity_20230710.csv
    |     |     |       └── unknown_nodes_intensity.csv   
    |     |     |── Data_EcoCompt_clean/...
    │     │     |── Prediction_Data/
    |     |     |        ├── ecocompteurs_coords.csv
    |     |     |        ├── predictions_bike_intensity_july_week.csv   
    |     |     |        └── predictions_long_format_july.csv
    │     │     |── Video_Data/
    |     |     |        ├── GeolocalisationStation.csv
    |     |     |        └── VideoDatacleaned.csv
    │     │     └── Readme.md
    |     ├── Result/
    |     |     |── Bike_Animation_10-07-2023.mp4
    │     │     │── Extrait_Bike_Animation.mp4   
    │     │     │── bike_traffic_prediction_map.html
    │     │     │── boxplot.svg
    │     │     │── intensity_graph.svg   
    │     │     └── real_data_map.html       
    │     └── Scripts/
    │           ├── Prediction/
    │           |       ├── cache/...    
    │           |       ├── Readme.md
    │           |       ├── code_bike_traffic_prediction.py
    │           |       ├── code_eco_coord.py
    │           |       ├── code_prediction_july.py
    │           |       └── code_prediction_long_format_july.py
    |           ├── cache/...   
    |           ├── .Rhistory
    |           ├── Animation_Bike.py
    |           ├── Readme.md    
    |           ├── Statistics.py    
    |           ├── data_treatment_EcoCompt.py
    |           ├── data_treatment_Velomag.py 
    |           ├── ecoCompt_Download_and_Combine.py      
    |           └── map.py
    ├── Organization/
    │     ├── Gantt diagram/
    │     │     ├── Gantt_Diagram_files/libs/...
    │     │     ├── Gantt Diagram.html
    │     │     └── Gantt Diagram.qmd
    │     └──── Models/
    │           ├── Mapmodel.png
    │           └── Websitemodel.png
    ├── Restitution/
    │     ├── images/...
    │     │── slides_files/libs/...
    │     │── Slides.html
    │     │── Slides.qmd   
    │     └── styles.css        
    ├── RoadMap/
    │     └── README.md
    ├── Website/
    |      ├── analyses/   
    │      |    ├── map.qmd
    │      |    ├── statistics.qmd
    │      │    └── video.qmd
    |      ├── docs/...    
    |      ├── documentation/
    │      |    ├── classes.qmd
    │      |    ├── functions.qmd
    │      │    └── packages.qmd
    |      ├── footer/
    │      |    ├── MIT_license.qmd
    │      |    ├── about_us.qmd
    │      │    └── privacy_policy.qmd
    |      ├── images/...
    |      ├── sources/   
    │      │    └── sources.qmd 
    |      ├── .gitignore 
    |      ├── Readme.md
    |      ├── _quarto.yml
    |      ├── footer.qmd
    |      ├── index.qmd
    │      └── styles.css
    ├── .gitignore
    ├── README.md
    └── requirements.txt 
```