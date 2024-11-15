import osmnx as ox
ox.settings.use_cache=True
ox.__version__

G = ox.graph_from_place('Montpellier, France', network_type='bike')
print(f"nb edges: {G.number_of_edges()}")
print(f"nb nodes: {G.number_of_nodes()}")

fig, ax = ox.plot_graph(G)

import folium
import matplotlib
import mapclassify
map_osm = folium.Map(location=[43.610769, 3.876716])
map_osm.add_child(folium.RegularPolygonMarker(location=[43.610769, 3.876716],
                  fill_color='#132b5e', radius=5))
map_osm


import sklearn
origin = ox.geocoder.geocode('Place Eugène Bataillon, Montpellier, France')
destination = ox.geocoder.geocode('Maison du Lez, Montpellier, France')

origin_node = ox.nearest_nodes(G, origin[1], origin[0])
destination_node = ox.nearest_nodes(G, destination[1], destination[0])

print(origin)
print(destination)
route = ox.routing.shortest_path(G, origin_node, destination_node)
route_back = ox.routing.shortest_path(G, destination_node, origin_node)

fig, ax = ox.plot_graph_routes(G, [route, route_back], route_linewidth=6, route_colors=['red', 'blue'], node_size=0)

route_edges = ox.utils_graph.route_to_gdf(G, route)
route_back_edges = ox.utils_graph.route_to_gdf(G, route_back)

m = route_edges.explore(color="red", style_kwds={"weight": 5, "opacity": 0.75})
m = route_back_edges.explore(m=m, color="blue", style_kwds={"weight": 5, "opacity": 0.75})
m