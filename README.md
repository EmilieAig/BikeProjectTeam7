# BikeProjectTeam7
This is our project of the UE HAX712X for the year 2024-2025.
Le nom du projet : BikeProjectTeam7

The members of the group are :
- AIGOIN Emilie
- MAMANE SIDI Samira
- THOMAS Anne-Laure
- ZHU Qingjian


2. Description du projet minimum viable (MVP)

Le projet vise à analyser le trafic cycliste à Montpellier à partir de différents jeux de données et à fournir des visualisations interactives via un site web. Voici les composants à inclure dans la description du projet :

a. Architecture

Le projet aura une structure avec :

	•	Front-end (site web) :
	•	Un site web où l’utilisateur pourra naviguer et interagir avec les différentes visualisations.
	•	Le site comportera des graphiques et une carte interactive avec des prédictions du trafic de vélos pour Montpellier.
	•	Tu pourras utiliser un framework de développement web tel que Flask ou Streamlit pour afficher les résultats de manière interactive.
	•	Back-end (traitement des données) :
	•	Analyse des données provenant des fichiers de comptage des vélos, des trajets des vélos en libre-service et des données d’OpenStreetMap.
	•	Un modèle de prédiction basé sur des séries temporelles (par exemple avec des outils comme Prophet, ARIMA, ou des méthodes de Machine Learning) pour prévoir le trafic des vélos pour les jours suivants.

b. Fichiers principaux

	•	data/ : Dossier contenant les fichiers de données (CSV, JSON, etc.).
	•	src/ : Le code source, avec des sous-dossiers pour :
	•	data_processing.py : Pour nettoyer et structurer les données.
	•	model_training.py : Pour entraîner le modèle de prédiction.
	•	visualization.py : Pour générer les graphiques et cartes.
	•	web_app.py : Pour le script qui génère le site web (par exemple avec Flask ou Streamlit).
	•	templates/ : Contenant les templates HTML si tu utilises un framework web comme Flask.
	•	static/ : Pour les fichiers CSS et JavaScript (si nécessaire).

c. Pipeline de développement

Le pipeline de développement pourrait être divisé en plusieurs étapes :

	1.	Collecte des données : Importer et nettoyer les données des différents jeux de données (VéloMagg, comptages vélo/piéton, OpenStreetMap).
	2.	Pré-traitement : Filtrer les données, gérer les valeurs manquantes, et fusionner les différentes sources de données.
	3.	Visualisation des données historiques : Créer des graphiques de séries temporelles, et des cartes montrant le trafic des vélos sur des périodes comme le dernier mois, la dernière année, ou plusieurs années.
	4.	Modélisation et prédiction : Entraîner un modèle pour prévoir le trafic de vélos pour les jours à venir.
	5.	Développement du site web : Intégrer les visualisations et le modèle de prédiction dans un site web interactif.

d. Technologies et packages utilisés

	•	Langage principal : Python
	•	Packages :
	•	Pour la gestion et l’analyse des données : Pandas, NumPy
	•	Pour la visualisation : Matplotlib, Seaborn, Plotly (pour des graphiques interactifs), Folium ou Leaflet.js (pour la carte interactive)
	•	Pour la modélisation et la prédiction : scikit-learn, Prophet (ou ARIMA), TensorFlow (si tu utilises des réseaux de neurones)
	•	Pour le site web : Flask ou Streamlit
	•	Pour l’API OSM : osmnx ou GeoPandas pour manipuler les données géospatiales.

3. Illustrations des résultats attendus

Tu devras inclure des images pour donner une idée des résultats que tu souhaites obtenir. Voici quelques exemples d’illustrations que tu peux créer :

	•	Séries temporelles : Un graphique qui montre l’évolution du nombre de trajets en vélo au cours du dernier mois, de la dernière année, ou sur toutes les années disponibles.
	•	Carte interactive : Une carte de Montpellier colorée en fonction de l’intensité du trafic des vélos, avec une prévision pour le jour suivant (par exemple, avec un code couleur rouge pour un trafic élevé, jaune pour un trafic modéré, vert pour un trafic faible).
	•	Ces images peuvent être des croquis simples faits à la main ou générés rapidement via des outils comme Excel ou Google Charts.

4. Branches Git

Il est recommandé de créer au moins deux branches sur Git pour faciliter le développement parallèle :

	•	main : Contient la version stable du projet, utilisable par tout le monde.
	•	dev : Une branche pour développer et tester les nouvelles fonctionnalités sans affecter la version stable.

Tu peux également ajouter des branches supplémentaires pour des sous-parties spécifiques du projet, par exemple :

	•	data_preprocessing : Pour travailler sur le nettoyage et la préparation des données.
	•	model_training : Pour travailler sur la partie modélisation et prédiction du trafic.
