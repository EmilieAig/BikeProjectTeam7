# %%
import os
import pandas as pd
from datetime import timedelta
from geopy.distance import geodesic
import osmnx as ox
import matplotlib
matplotlib.use('Agg')  # Use a backend without graphical interface
import matplotlib.pyplot as plt
import seaborn as sns
import pooch
from tqdm import tqdm
from multiprocessing import Pool
from moviepy.editor import ImageSequenceClip

class BikeAnimation:
    def __init__(self, input_file, place_name="Montpellier, France", target_date=None, 
                 output_video="bike_animation.mp4", fps=30, minutes_per_second=120, 
                 sample_size=None):
        self.input_file = input_file
        self.place_name = place_name
        self.target_date = target_date
        self.output_video = output_video
        self.fps = fps
        self.minutes_per_second = minutes_per_second
        self.sample_size = sample_size

        # Load the data
        self.df = pd.read_csv(input_file)
        self.df['Departure_DateTime'] = pd.to_datetime(self.df['Departure_Date'] + ' ' + self.df['Departure_Time'])
        self.df['Return_DateTime'] = pd.to_datetime(self.df['Return_Date'] + ' ' + self.df['Return_Time'])
        
        if self.target_date:
            self.target_date = pd.to_datetime(self.target_date)
            self.df = self.df[self.df['Departure_DateTime'].dt.date == self.target_date.date()]
        
        if self.sample_size:
            self.df = self.df.head(self.sample_size)
        
        self.df_sorted = self.df.sort_values(by='Departure_DateTime')

        # Load the OSM graph
        self.G = ox.graph_from_place(self.place_name, network_type='bike')
        self.nodes = ox.graph_to_gdfs(self.G, nodes=True, edges=False)
        
        # Calculate the total duration and frames
        self.start_time = self.df_sorted['Departure_DateTime'].min()
        self.end_time = self.df_sorted['Return_DateTime'].max()
        total_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
        total_seconds = total_minutes / self.minutes_per_second
        self.total_frames = int(total_seconds * self.fps)

        # Precompute the routes
        self.df_sorted['route'] = self.df_sorted.apply(
            lambda row: self.precompute_route(row), axis=1)

        # Save the background graph image
        self.background_file = "background_graph.png"
        self.save_graph_background()

    def precompute_route(self, row):
        """Precompute the route for a departure and return."""
        start_pos = (row['Departure_latitude'], row['Departure_longitude'])
        end_pos = (row['Return_latitude'], row['Return_longitude'])

        try:
            start_node = ox.distance.nearest_nodes(self.G, X=start_pos[1], Y=start_pos[0])
            end_node = ox.distance.nearest_nodes(self.G, X=end_pos[1], Y=end_pos[0])
            return ox.shortest_path(self.G, start_node, end_node, weight='length')
        except:
            return None

    def save_graph_background(self):
        """Save a background image of the graph."""
        fig, ax = plt.subplots(figsize=(12, 12))
        ax.set_facecolor('black')
        ox.plot_graph(self.G, ax=ax, show=False, close=False, node_size=0,
                      edge_color='white', edge_linewidth=0.5)
        plt.savefig(self.background_file, bbox_inches='tight', facecolor='black')
        plt.close(fig)

    def interpolate_route_position(self, route_coords, progress):
        """Interpolate the position on the route."""
        if not route_coords or len(route_coords) < 2:
            return route_coords[0] if route_coords else None

        total_distance = sum(
            geodesic(route_coords[i], route_coords[i + 1]).meters
            for i in range(len(route_coords) - 1)
        )
        target_distance = total_distance * progress

        current_distance = 0
        for i in range(len(route_coords) - 1):
            segment_distance = geodesic(route_coords[i], route_coords[i + 1]).meters
            if current_distance + segment_distance >= target_distance:
                fraction = (target_distance - current_distance) / segment_distance
                lat1, lon1 = route_coords[i]
                lat2, lon2 = route_coords[i + 1]
                return (
                    lat1 + fraction * (lat2 - lat1),
                    lon1 + fraction * (lon2 - lon1)
                )
            current_distance += segment_distance
        return route_coords[-1]

    def generate_frame(self, frame):
        """Generate a single frame."""
        elapsed_minutes = (frame / self.fps) * self.minutes_per_second
        current_time = self.start_time + timedelta(minutes=elapsed_minutes)

        fig, ax = plt.subplots(figsize=(12, 12))
        ax.set_facecolor('black')

        # Load the background image
        background_img = plt.imread(self.background_file)
        # Get the bounds of the graph
        graph_bbox = ox.graph_to_gdfs(self.G, nodes=True, edges=False).total_bounds
        xmin, ymin, xmax, ymax = graph_bbox
        ax.imshow(background_img, extent=[xmin, xmax, ymin, ymax])

        # Add the ongoing trips
        for _, row in self.df_sorted.iterrows():
            route_coords = [(self.nodes.loc[node]['y'], self.nodes.loc[node]['x']) for node in row['route']] if row['route'] else []
            if row['Departure_DateTime'] <= current_time <= row['Return_DateTime']:
                journey_duration = (row['Return_DateTime'] - row['Departure_DateTime']).total_seconds()
                elapsed_journey_time = (current_time - row['Departure_DateTime']).total_seconds()
                progress = elapsed_journey_time / journey_duration
                current_pos = self.interpolate_route_position(route_coords, progress)

                if current_pos:
                    xs, ys = zip(*route_coords)
                    ax.plot(ys, xs, color='blue', linewidth=1.5)
                    ax.scatter(current_pos[1], current_pos[0], color='red', s=50)

        ax.text(0.05, 0.95, f"Time: {current_time.strftime('%H:%M:%S')}", color='white',
                transform=ax.transAxes, fontsize=14, verticalalignment='top')

        filename = f"map_images/frame_{frame:08d}.png"
        plt.savefig(filename, bbox_inches='tight', facecolor='black')
        plt.close(fig)
        return filename

    def create_animation(self):
        """Create the animation using multiprocessing."""
        os.makedirs("map_images", exist_ok=True)

        with Pool(processes=os.cpu_count()) as pool:
            image_files = list(tqdm(pool.imap(self.generate_frame, range(self.total_frames)), 
                                    total=self.total_frames, desc="Generating frames"))

        clip = ImageSequenceClip(image_files, fps=self.fps)
        clip.write_videofile(self.output_video, codec='libx264')

        for file in image_files:
            os.remove(file)

#%%
# Seaborn configuration
sns.set_palette("colorblind")
palette = sns.color_palette("twilight", n_colors=12)
pd.options.display.max_rows = 8

# URL and file path
url = "https://raw.githubusercontent.com/EmilieAig/BikeProjectTeam7/main/Code/Data/Video_Data/VideoDatacleaned.csv"
path_target = "./VideoDatacleaned.csv"
path, fname = os.path.split(path_target)

# Download the data
known_hash = 'db411c888c7fdbb208165ef84b854dc5a431ae8ed5d25edb3a3facebea33cba3'  # Replace with the hash if necessary
pooch.retrieve(url, path=path, fname=fname, known_hash=known_hash)
df_DataBike_raw = pd.read_csv(url, low_memory=False)

#%%
# Example of using the class
if __name__ == "__main__":
    animation = BikeAnimation(
        input_file=url,  # Replace with your CSV file
        place_name="Montpellier, France",
        target_date="2023-07-10",
        output_video="bike_animation_video1.mp4",
        fps=30,
        minutes_per_second=30  # 1 real minute = 1 second in the video
    )
    animation.create_animation()
