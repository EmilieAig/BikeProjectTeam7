# BikeProjectTeam7
This is our project for the HAX712X course for the academic year 2024-2025.
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
## Description of our project:  
1. Architecture  
The project will have the following structure:\
**Front-end (website)**:\
A website where users can browse and interact with various visualizations.
The site will feature charts and an interactive map displaying bike traffic predictions for Montpellier.\
**Back-end (data processing)**:\
Data analysis from April to October 2023, based on bike counting data, public bike-sharing trip data, and OpenStreetMap data.
A prediction model based on time series analysis (using tools like Prophet, ARIMA, or Machine Learning methods) to forecast bike traffic for the coming days.  
2. Main Files:\
The different files,we will use are the following:  
**Data**: Folder containing the data files (CSV, JSON, etc.):
- Data Bike 2023.csv \
**Scripts**: The source code, with subfolders for:
- data_processing.py: For cleaning and structuring the data.  
- model_training.py: For training the prediction model.  
- visualization maps.py: For generating charts and maps.  
- web_app.py: The script responsible for generating the website. 
- website.qmd
- website.html \
**Restitution**:It contains the files about the slides and the oral for our presentation
- Slides.qmd
- Oral.txt

3. Development Pipeline

The development pipeline will be divided into several stages:
- **Data Collection**: Import and clean data from various datasets (VéloMagg, bike/pedestrian counts, OpenStreetMap).
- **Preprocessing**: Filter the data, handle missing values, and merge the different data sources.
- **Visualization of Historical Data**: Create time series charts and maps showing bike traffic from April to October 2023.
- **Modeling and Prediction**: Train a model to forecast bike traffic for the upcoming days.
- **Website Development**: Integrate visualizations and the prediction model into an interactive website.
4. Technologies and Packages Used:
- **Primary Language**: Python
- **Packages**:  
      - **For data management and analysis**: Pandas, NumPy  
      - **For visualization**: Matplotlib, Seaborn, Plotly (for interactive charts), Folium  or Leaflet.js (for the interactive map)
      - **For modeling and prediction**: scikit-learn, Prophet (or ARIMA)  
      - **For the website and the slides**: Quarto  
5. The Gantt Diagram\
We will also create a Gantt Diagram to illustrate the project's timeline and track its progress over time. This diagram will help visualize each phase of the project, from data collection to website development, allowing us to monitor deadlines, dependencies, and milestones clearly.
6. Creation of branch:\
We have created three additional branches:Data,Visualization and Website, aside from the main branch. Gradually, we will merge our respective work into the main branch.
7. Task Distribution for the project \
To organize our work efficiently, we have established the following task distribution plan,with a weekly meeting every Wednesday from 10 a.m. to 12 p.m:

    **Planning:**
    - Emilie handled the creation of the Gantt chart detailing the various stages of the project.
    - Samira was responsible for writing the README.md file and creating the files that will be used later in the project.
    - Anne-Laure created a mock-up of the future website.
    - Qingjian designed a preliminary representation of the graphical map that we aim to achieve as the final result.

    **Data Processing and Scripts:**
    - Samira will be in charge of cleaning and structuring the data in the dataprocessing.py file.
    - Anne-Laure will train these data using a forecasting model in the modeltraining.py file.
    - Qingjian will handle the generation of charts and maps in the visualisation.py file.
    - Emilie will be responsible for developing the website script in the webapp.py file.

    **Multimedia Creation:**
    - The video representing a cycling race forecast for a specific date will be made by Samira and helping by one or two other team member.
    - The creation of the website will be carried out by Emilie and Anne-Laure.

    **Verification and Testing:**
    - Qingjian will perform an initial test to ensure that the project is on the right track.
    - Anne-Laure will be responsible for the documentation, assisted by another team member depending on the workload and task complexity.

    **Final Presentation Preparation:**\
        The presentation slides, as well as the oral preparation, will be created by the entire team. This collaborative work will be done progressively as the project advances.\
        At least one week before the project deadline, a final test will be conducted to ensure the quality of the completed project.


