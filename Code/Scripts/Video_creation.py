#%%
import os
import time
import folium
from selenium import webdriver
from moviepy.editor import ImageSequenceClip
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import requests
import polyline
from geopy.distance import geodesic  # Pour calculer les distances géographiques

def get_route(start_coords, end_coords, covered_distance):
    """
    Obtient un itinéraire en utilisant l'API OSRM, ajusté pour la distance parcourue si elle est disponible.
    """
    # Vérifier si `covered_distance` est nul et retourner un itinéraire réaliste sans ajustement
    if covered_distance == 0:
        print(f"Distance couverte nulle pour le trajet {start_coords} -> {end_coords}. Obtention d'un itinéraire réaliste.")
    
    # URL du serveur OSRM pour un itinéraire vélo
    url = f"http://router.project-osrm.org/route/v1/bicycle/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=polyline"
    response = requests.get(url)
    
    if response.status_code == 200:
        route = response.json()
        if 'routes' in route and len(route['routes']) > 0:
            geometry = route['routes'][0]['geometry']
            route_coords = polyline.decode(geometry)
            
            # Ajustement de la route en fonction de `Covered_distance_m`, si applicable
            if covered_distance > 0:
                route_distance = sum(geodesic(route_coords[i], route_coords[i + 1]).meters for i in range(len(route_coords) - 1))
                # Ajuster seulement si la différence est significative
                if abs(route_distance - covered_distance) / covered_distance < 0.1:  # Tolérance de 10%
                    return route_coords
                else:
                    print(f"Distance ajustée pour {start_coords} -> {end_coords}")
            return route_coords  # Retourner l'itinéraire calculé, même sans ajustement pour les distances nulles
    # En cas d'erreur, retourner le segment direct comme fallback
    print(f"Impossible d'obtenir l'itinéraire pour {start_coords} -> {end_coords}. Utilisation d'un trajet direct.")
    return [start_coords, end_coords]


def interpolate_route_position(route_coords, progress, covered_distance):
    """
    Interpole la position le long de la route en fonction du progrès et de la distance couverte.
    
    Args:
        route_coords: Liste de tuples (lat, lon) définissant le trajet
        progress: Pourcentage de progression (0 à 1)
        covered_distance: Distance totale parcourue en mètres
    
    Returns:
        tuple: (latitude, longitude) de la position interpolée
    """
    if not route_coords or len(route_coords) < 2:
        return route_coords[0] if route_coords else None
        
    # Si la distance est très petite (< 10m) ou nulle, on reste au point de départ
    if covered_distance < 10:
        if progress < 0.5:
            return route_coords[0]
        else:
            return route_coords[-1]
            
    # Calculer les distances entre chaque point de la route
    segment_distances = []
    total_route_distance = 0
    for i in range(len(route_coords) - 1):
        d = geodesic(route_coords[i], route_coords[i + 1]).meters
        segment_distances.append(d)
        total_route_distance += d
    
    # Utiliser la distance réelle parcourue plutôt que la distance de l'itinéraire
    target_distance = covered_distance * progress
    
    # Si la cible est au-delà de la fin, renvoyer le dernier point
    if target_distance >= covered_distance:
        return route_coords[-1]
    
    # Trouver le segment où se trouve la position cible
    current_distance = 0
    for i in range(len(route_coords) - 1):
        if current_distance + segment_distances[i] >= target_distance:
            # Calculer la fraction précise le long de ce segment
            remaining = target_distance - current_distance
            fraction = remaining / segment_distances[i]
            
            # Interpolation linéaire entre les points
            lat1, lon1 = route_coords[i]
            lat2, lon2 = route_coords[i + 1]
            
            return (
                lat1 + fraction * (lat2 - lat1),
                lon1 + fraction * (lon2 - lon1)
            )
            
        current_distance += segment_distances[i]
    
    # Si on arrive ici, renvoyer le dernier point
    return route_coords[-1]
#%%
def create_bike_animation(input_file, target_date=None, output_video="bike_animation.mp4", fps=30, minutes_per_second=120, sample_size=None):
    """
    Crée une animation des trajets de vélos en fonction d'une date donnée et affiche les stations sous forme de points.
    """
    # Charger les données
    df = pd.read_csv(input_file)
    
    # Convertir les colonnes de date/heure
    df['Departure_DateTime'] = pd.to_datetime(df['Departure_Date'] + ' ' + df['Departure_Time'])
    df['Return_DateTime'] = pd.to_datetime(df['Return_Date'] + ' ' + df['Return_Time'])
    
    # Filtrer les trajets par date si `target_date` est spécifié
    if target_date:
        target_date = pd.to_datetime(target_date)
        df = df[df['Departure_DateTime'].dt.date == target_date.date()]
    
    # Trier les trajets par date de départ
    df_sorted = df.sort_values(by='Departure_DateTime')
    if sample_size:
        df_sorted = df_sorted.head(sample_size)
    
    # Préparer les routes
    routes = {}
    for _, row in df_sorted.iterrows():
        start_pos = (row['Departure_latitude'], row['Departure_longitude'])
        end_pos = (row['Return_latitude'], row['Return_longitude'])
        covered_distance = row['Covered distance (m)']
        route_key = f"{start_pos}-{end_pos}"
        if route_key not in routes:
            route = get_route(start_pos, end_pos, covered_distance)
            routes[route_key] = route if route else [(start_pos[0], start_pos[1]), (end_pos[0], end_pos[1])]
            time.sleep(1)
    
    # Initialisation des paramètres de l'animation
    start_time = df_sorted['Departure_DateTime'].min()
    end_time = df_sorted['Return_DateTime'].max()
    total_minutes = int((end_time - start_time).total_seconds() / 60)
    
    total_seconds = total_minutes / minutes_per_second
    total_frames = int(total_seconds * fps)
    
    image_folder = 'map_images'
    os.makedirs(image_folder, exist_ok=True)
    image_files = []
    
    driver = webdriver.Chrome()
    
    completed_trips = []
    
    for frame in range(total_frames):
        elapsed_minutes = (frame / fps) * minutes_per_second
        current_time = start_time + timedelta(minutes=elapsed_minutes)
        
        map_montpellier = folium.Map(location=[43.6117, 3.8777], zoom_start=13)
        
        # Marquer les stations de départ et d'arrivée
        for _, row in df_sorted.iterrows():
            folium.Marker(
                location=(row['Departure_latitude'], row['Departure_longitude']),
                popup="Station de départ",
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(map_montpellier)
            
            folium.Marker(
                location=(row['Return_latitude'], row['Return_longitude']),
                popup="Station d'arrivée",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(map_montpellier)
        
        # Afficher les trajets
        for trip in completed_trips:
            folium.PolyLine(
                trip['route'],
                color="blue",
                weight=2.5,
                opacity=1
            ).add_to(map_montpellier)
        
        for _, row in df_sorted.iterrows():
            start_pos = (row['Departure_latitude'], row['Departure_longitude'])
            end_pos = (row['Return_latitude'], row['Return_longitude'])
            route_key = f"{start_pos}-{end_pos}"
            route = routes[route_key]
            covered_distance = row['Covered distance (m)']
            
            if current_time > row['Return_DateTime']:
                if not any(trip['start_pos'] == start_pos and trip['end_pos'] == end_pos for trip in completed_trips):
                    completed_trips.append({
                        'start_pos': start_pos,
                        'end_pos': end_pos,
                        'route': route
                    })
                continue
            
            if row['Departure_DateTime'] <= current_time <= row['Return_DateTime']:
                journey_duration = (row['Return_DateTime'] - row['Departure_DateTime']).total_seconds()
                elapsed_journey_time = (current_time - row['Departure_DateTime']).total_seconds()
                progress = min(1.0, max(0.0, elapsed_journey_time / journey_duration))
                
                if len(route) > 2:
                    current_index = int(progress * (len(route) - 1))
                    current_route = route[:current_index + 1]
                    current_pos = route[current_index]
                else:
                    current_pos = interpolate_route_position(route, progress, covered_distance)
                    current_route = [route[0], current_pos]
                
                folium.PolyLine(
                    current_route,
                    color="blue",
                    weight=2.5,
                    opacity=1
                ).add_to(map_montpellier)
                
                folium.CircleMarker(
                    location=current_pos,
                    radius=5,
                    color="red",
                    fill=True
                ).add_to(map_montpellier)
        
        map_filename = f"map_frame_{frame}.html"
        map_montpellier.save(map_filename)
        
        driver.get(f'file://{os.path.abspath(map_filename)}')
        time.sleep(0.1)
        
        screenshot_name = os.path.join(image_folder, f"frame_{frame:08d}.png")
        driver.save_screenshot(screenshot_name)
        image_files.append(screenshot_name)
        
        if frame % 10 == 0:
            print(f"Progression: {frame}/{total_frames} images ({(frame/total_frames*100):.1f}%)")
    
    driver.quit()
    
    print("Création de la vidéo...")
    image_files.sort()
    clip = ImageSequenceClip(image_files, fps=fps)
    clip.write_videofile(output_video, codec='libx264')
    
    print("Nettoyage des fichiers temporaires...")
    for file in image_files:
        os.remove(file)
    for file in os.listdir():
        if file.startswith("map_frame_") and file.endswith(".html"):
            os.remove(file)


import os
print(os.getcwd())  # Affiche le répertoire courant

if __name__ == "__main__":
    create_bike_animation(
        input_file='Data/VideoDatacleaned.csv',
        output_video='bike_animation_test.mp4',
        fps=60,
        minutes_per_second=30,
        sample_size=200
    )
