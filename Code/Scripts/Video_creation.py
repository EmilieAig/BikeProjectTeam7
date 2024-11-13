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

def get_route(start_coords, end_coords):
    """
    Obtient l'itinéraire entre deux points en utilisant l'API OSRM.
    """
    # Utilisation du serveur public OSRM pour le vélo
    url = f"http://router.project-osrm.org/route/v1/bicycle/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=polyline"
    response = requests.get(url)
    if response.status_code == 200:
        route = response.json()
        if 'routes' in route and len(route['routes']) > 0:
            # Décode la géométrie de la route (format polyline)
            geometry = route['routes'][0]['geometry']
            route_coords = polyline.decode(geometry)
            return route_coords
    return None

def interpolate_route_position(route_coords, progress):
    """
    Interpole la position le long d'une route en fonction de la progression.
    """
    if not route_coords:
        return None
    
    # Calculer la distance totale de la route
    total_distance = 0
    distances = []
    for i in range(len(route_coords) - 1):
        lat1, lon1 = route_coords[i]
        lat2, lon2 = route_coords[i + 1]
        d = ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5
        total_distance += d
        distances.append(d)
    
    # Trouver le point correspondant à la progression
    target_distance = total_distance * progress
    current_distance = 0
    for i in range(len(route_coords) - 1):
        if current_distance + distances[i] >= target_distance:
            # Interpolation linéaire dans ce segment
            remaining = target_distance - current_distance
            fraction = remaining / distances[i]
            lat1, lon1 = route_coords[i]
            lat2, lon2 = route_coords[i + 1]
            return (
                lat1 + fraction * (lat2 - lat1),
                lon1 + fraction * (lon2 - lon1)
            )
        current_distance += distances[i]
    return route_coords[-1]

def create_bike_animation(input_file, output_video="bike_animation.mp4", fps=30, minutes_per_second=120, sample_size=None):
    """
    Crée une animation des trajets de vélos en utilisant les vraies routes.
    """
    # Charger et préparer les données
    df = pd.read_csv(input_file)
    df['Departure_DateTime'] = pd.to_datetime(df['Departure_Date'] + ' ' + df['Departure_Time'])
    df['Return_DateTime'] = pd.to_datetime(df['Return_Date'] + ' ' + df['Return_Time'])
    
    # Trier les données et prendre un échantillon
    df_sorted = df.sort_values(by='Departure_DateTime')
    if sample_size:
        df_sorted = df_sorted.head(sample_size)
        print(f"Utilisation d'un échantillon de {sample_size} trajets")
    
    # Précalculer tous les itinéraires
    print("Calcul des itinéraires...")
    routes = {}
    for _, row in df_sorted.iterrows():
        start_pos = (row['Departure latitude'], row['Departure longitude'])
        end_pos = (row['Return latitude'], row['Return longitude'])
        route_key = f"{start_pos}-{end_pos}"
        if route_key not in routes:
            route = get_route(start_pos, end_pos)
            routes[route_key] = route if route else [(start_pos[0], start_pos[1]), (end_pos[0], end_pos[1])]
            time.sleep(1)  # Pause pour respecter les limites de l'API
    
    # Calculer la période totale
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
    
    # Générer chaque image
    for frame in range(total_frames):
        elapsed_minutes = (frame / fps) * minutes_per_second
        current_time = start_time + timedelta(minutes=elapsed_minutes)
        
        map_montpellier = folium.Map(location=[43.6117, 3.8777], zoom_start=13)
        
        # Dessiner les trajets terminés
        for trip in completed_trips:
            folium.PolyLine(
                trip['route'],
                color="blue",
                weight=2.5,
                opacity=1
            ).add_to(map_montpellier)
        
        # Traiter chaque trajet actif
        for _, row in df_sorted.iterrows():
            start_pos = (row['Departure latitude'], row['Departure longitude'])
            end_pos = (row['Return latitude'], row['Return longitude'])
            route_key = f"{start_pos}-{end_pos}"
            route = routes[route_key]
            
            # Si le trajet est terminé
            if current_time > row['Return_DateTime']:
                if not any(trip['start_pos'] == start_pos and trip['end_pos'] == end_pos for trip in completed_trips):
                    completed_trips.append({
                        'start_pos': start_pos,
                        'end_pos': end_pos,
                        'route': route
                    })
                continue
            
            # Si le trajet est en cours
            if row['Departure_DateTime'] <= current_time <= row['Return_DateTime']:
                journey_duration = (row['Return_DateTime'] - row['Departure_DateTime']).total_seconds()
                elapsed_journey_time = (current_time - row['Departure_DateTime']).total_seconds()
                progress = min(1.0, max(0.0, elapsed_journey_time / journey_duration))
                
                # Trouver la position actuelle sur la route
                if len(route) > 2:
                    # Dessiner la partie parcourue de l'itinéraire
                    current_index = int(progress * (len(route) - 1))
                    current_route = route[:current_index + 1]
                    current_pos = route[current_index]
                else:
                    # Fallback sur l'interpolation linéaire si pas de route détaillée
                    current_pos = interpolate_route_position(route, progress)
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

if __name__ == "__main__":
    create_bike_animation(
        input_file='cleaned_data.csv',
        output_video='bike_animation_test.mp4',
        fps=20,
        minutes_per_second=120,
        sample_size=10  # Test avec seulement 10 trajets
    )
