# %% Extraire les coordonnées des compteurs
import pandas as pd
import os
# 文件路径设置
data_folder = os.path.join("..", "Data", "Data_EcoCompt_Combined")  # 数据文件夹路径
file_path = os.path.join(data_folder, "fichier_combined.csv")  # 文件路径

# 读取 CSV 文件
df = pd.read_csv(file_path, delimiter=";")  # 使用分号作为分隔符

# 提取计数器基础 Id
df['counter_id'] = df['id'].str.extract(r'(MMM_EcoCompt_\w+?)_')  # 提取基础 Id

# 提取唯一的计数器 Id 和坐标
unique_counters = df[['counter_id', 'longitude', 'latitude']].drop_duplicates()

# 输出提取结果的前几行查看
print(unique_counters.head())

# 保存结果到新的 CSV 文件
output_folder = data_folder  # 保存到同一目录
output_path = os.path.join(output_folder, "counter_coordinates.csv")
unique_counters.to_csv(output_path, index=False)

print(f"计数器数据已提取并保存到：{output_path}")




# %% 提取网络图，选择合适的范围，并根据道路类型进行筛选，保留合适的道路密度
import osmnx as ox
ox.settings.use_cache=True
ox.__version__
import osmnx as ox
import networkx as nx
from shapely.geometry import Point

# 定义中心点和半径
center_point = (43.606, 3.877)  # (latitude, longitude)
radius = 9280  # 半径 9.28 公里，单位为米

# 1. 创建圆形多边形
center = Point(center_point[1], center_point[0])  # shapely 的坐标格式为 (lon, lat)
circle = center.buffer(radius / 111320)  # 使用大约 1° 纬度等于 111.32 公里转换

# 2. 提取圆形区域内的自行车网络
G = ox.graph_from_polygon(circle, network_type='bike')


# 定义要保留的道路类型
desired_highways = {'primary', 'trunk', 'secondary', 'tertiary', 'secondary_link', 'trunk_link', 'primary_link', 'tertiary_link', 'living_street',  'bridleway'}

# 遍历图中的边并过滤筛选
edges_to_remove = []
for u, v, key, data in G.edges(keys=True, data=True):
    highway = data.get('highway', None)
    if isinstance(highway, list):
        # 如果 highway 是列表，检查是否与 desired_highways 有交集
        if not any(h in desired_highways for h in highway):
            edges_to_remove.append((u, v, key))
    elif highway not in desired_highways:
        # 如果 highway 是单个值，直接检查是否在 desired_highways 中
        edges_to_remove.append((u, v, key))

# 删除不需要的边
G.remove_edges_from(edges_to_remove)

# 删除孤立节点
isolated_nodes = list(nx.isolates(G))  # 找到所有孤立节点
G.remove_nodes_from(isolated_nodes)  # 删除孤立节点

# 1. 找到网络的所有连通分量
connected_components = nx.connected_components(G.to_undirected())

# 2. 确定最大的连通分量
largest_cc = max(connected_components, key=len)

# 3. 创建包含最大连通分量的子图
G_largest = G.subgraph(largest_cc).copy()

# 4. 输出清理后的节点和边数量
print(f"清理后，网络包含 {G_largest.number_of_nodes()} 个节点和 {G_largest.number_of_edges()} 条边。")

# 更新原图
G = G_largest

# 可视化网络
print(f"nb edges: {G.number_of_edges()}")
print(f"nb nodes: {G.number_of_nodes()}")
fig, ax = ox.plot_graph(G)




# %% 将计数器的坐标和节点坐标进行匹配
import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt

# 1. 读取计数器数据
counter_file_path = "../Data/Data_EcoCompt_Combined/counter_coordinates.csv"
counters = pd.read_csv(counter_file_path)

# 2. 删除特定的计数器（counter_id 为 MMM_EcoCompt_X2H22104765）
counters = counters[counters['counter_id'] != 'MMM_EcoCompt_X2H22104765']

# 3. 找到最近的网络节点
counters['nearest_node'] = counters.apply(
    lambda row: ox.nearest_nodes(G, row['longitude'], row['latitude']), axis=1
)

# 4. 获取最近节点的坐标
nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
counters['node_longitude'] = counters['nearest_node'].map(nodes['x'])
counters['node_latitude'] = counters['nearest_node'].map(nodes['y'])

# 5. 可视化网络及标记节点
fig, ax = ox.plot_graph(G, show=False, close=False)

# 6. 绘制最近节点的位置（以红色标记）
nearest_positions = counters[['node_longitude', 'node_latitude']].values
ax.scatter(nearest_positions[:, 0], nearest_positions[:, 1], c='red', s=50, label='Nearest Nodes')

# 添加图例并显示
ax.legend()
plt.show()




# %% 选择想要的日期，然后匹配每个计数器节点和intensity
import pandas as pd
import os

# 文件路径设置
combined_file_path = "../Data/Data_EcoCompt_Combined/fichier_combined.csv"

def load_daily_node_intensity(dates, counters, combined_file_path):
    """
    加载多个日期的数据，并返回一个包含每日数据的字典。
    
    参数：
    - dates: list，包含需要处理的日期（格式如 "2023-07-10"）。
    - counters: DataFrame，包含计数器与最近节点的匹配数据。
    - combined_file_path: str，计数器原始数据文件路径。
    
    返回：
    - daily_data: dict，每个日期对应一个 DataFrame，格式为 {date: DataFrame}
    """
    # 1. 读取计数器原始数据
    combined_data = pd.read_csv(combined_file_path, delimiter=";")

    # 存储每日数据的字典
    daily_data = {}

    for date in dates:
        # 2. 筛选出当前日期的数据
        filtered_data = combined_data[combined_data['date'] == date].copy()

        # 3. 提取计数器基础 ID
        filtered_data['counter_id'] = filtered_data['id'].str.extract(r'(MMM_EcoCompt_\w+?)_')

        # 4. 将计数器与最近节点匹配
        merged_data = pd.merge(counters, filtered_data, on='counter_id', how='inner')

        # 5. 汇总每个节点的计数信息
        node_intensity = merged_data[['nearest_node', 'intensity']]

        # 6. 将 DataFrame 存入字典
        daily_data[date] = node_intensity
        print(f"{date} 的节点流量数据已加载完成")
    
    return daily_data

# 定义日期范围
dates_to_load = [
    "2023-07-10", "2023-07-11", "2023-07-12",
    "2023-07-13", "2023-07-14", "2023-07-15", "2023-07-16"
]

# 文件路径
combined_file_path = "../Data/Data_EcoCompt_Combined/fichier_combined.csv"

# 调用函数加载数据
daily_data = load_daily_node_intensity(dates_to_load, counters, combined_file_path)

# 检查某一天的数据
print(daily_data["2023-07-10"].head())




# %% 推算未知节点的intensity
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
import os

def estimate_unknown_intensity(daily_data, G):
    """
    使用已知节点的流量数据推算未知节点的流量，并更新图 G。
    
    参数：
    - daily_data: dict，每天的已知节点流量数据，格式为 {date: DataFrame}。
    - G: networkx 图对象，包含自行车网络结构。

    返回：
    - estimated_data: dict，推算后的每日未知节点流量，格式为 {date: DataFrame}。
    """
    from scipy.spatial import KDTree
    import numpy as np
    import pandas as pd

    # 存储推算结果的字典
    estimated_data = {}

    for date, node_data in daily_data.items():
        print(f"正在处理日期：{date}")

        # 提取已知节点信息
        known_nodes = node_data['nearest_node'].tolist()
        known_coords = np.array([[G.nodes[node]['x'], G.nodes[node]['y']] for node in known_nodes])
        known_intensities = node_data['intensity'].values

        # 获取所有节点
        all_nodes = list(G.nodes())
        all_coords = np.array([[G.nodes[node]['x'], G.nodes[node]['y']] for node in all_nodes])

        # 找到未知节点
        unknown_nodes = [node for node in all_nodes if node not in known_nodes]
        unknown_coords = np.array([[G.nodes[node]['x'], G.nodes[node]['y']] for node in unknown_nodes])

        # 构建 KD-Tree
        kd_tree = KDTree(known_coords)

        # 初始化未知节点的 intensity
        unknown_intensity = []

        # 遍历未知节点，计算与最近 3 个已知节点的加权平均值
        for coord in unknown_coords:
            distances, indices = kd_tree.query(coord, k=3)  # 最近 3 个已知节点
            weights = 1 / distances  # 权重是距离的倒数
            weighted_intensity = np.sum(weights * known_intensities[indices]) / np.sum(weights)
            unknown_intensity.append(weighted_intensity)

        # 保存推算结果到 DataFrame
        estimated_data[date] = pd.DataFrame({
            'node': unknown_nodes,
            'intensity': unknown_intensity
        })

        # 更新图 G 中的未知节点 intensity
        for i, node in enumerate(unknown_nodes):
            G.nodes[node]['intensity'] = unknown_intensity[i]

        print(f"日期 {date} 的未知节点流量推算完成")

    return estimated_data

estimated_daily_data = estimate_unknown_intensity(daily_data, G)

# 检查某一天的结果
print(estimated_daily_data["2023-07-10"])





# %% 可视化多日期的流量强度
import folium
import numpy as np

# 创建 folium 地图
center_coords = [43.607, 3.877]  # 地图中心
m = folium.Map(location=center_coords, zoom_start=13)

legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; width: 220px; height: 180px; 
    background-color: white; z-index:9999; font-size:14px;
    border:2px solid grey; border-radius:5px; padding: 10px;">
    <b>Intensity Legend</b><br>
    <i style="background:#D12315; width:15px; height:15px; display:inline-block;"></i> > 1500 (High Intensity)<br>
    <i style="background:#FE4528; width:15px; height:15px; display:inline-block;"></i> > 1200<br>
    <i style="background:#FB9234; width:15px; height:15px; display:inline-block;"></i> > 900<br>
    <i style="background:#FFEF3A; width:15px; height:15px; display:inline-block;"></i> > 600<br>
    <i style="background:#6CD932; width:15px; height:15px; display:inline-block;"></i> >= 300<br>
    <i style="background:#038C05; width:15px; height:15px; display:inline-block;"></i> < 300 (Low Intensity)<br>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# 定义颜色映射规则
def get_color(intensity):
    if intensity > 1500:
        return '#D12315'
    elif intensity > 1200:
        return '#FE4528'
    elif intensity > 900:
        return '#FB9234'
    elif intensity > 600:
        return '#FFEF3A'
    elif intensity > 300:
        return '#6CD932'
    else:
        return '#23C326'

# 为每一天的数据创建图层
for date, known_data in daily_data.items():
    print(f"正在处理日期：{date}")
    layer = folium.FeatureGroup(name=f"Data {date}")

    # 从 estimated_daily_data 获取未知节点的流量强度
    estimated_data = estimated_daily_data[date]

    # 1. 更新图 G 中的节点 intensity
    for node in G.nodes:
        if node in known_data['nearest_node'].values:
            # 使用 daily_data 中的已知节点流量
            G.nodes[node]['intensity'] = known_data.set_index('nearest_node').loc[node, 'intensity']
        elif node in estimated_data['node'].values:
            # 使用 estimated_daily_data 中的推算值
            G.nodes[node]['intensity'] = estimated_data.set_index('node').loc[node, 'intensity']
        else:
            # 对于没有数据的节点，设置为 NaN
            G.nodes[node]['intensity'] = np.nan

    # 2. 更新边的 intensity
    for u, v, data in G.edges(data=True):
        node_u_intensity = G.nodes[u].get('intensity', np.nan)
        node_v_intensity = G.nodes[v].get('intensity', np.nan)

        if np.isscalar(node_u_intensity) and np.isscalar(node_v_intensity) and not (np.isnan(node_u_intensity) or np.isnan(node_v_intensity)):
            data['intensity'] = (node_u_intensity + node_v_intensity) / 2
        else:
            data['intensity'] = np.nan  # 如果没有值则设为 NaN

    # 3. 在图层中绘制边
    for u, v, data in G.edges(data=True):
        intensity = data.get('intensity', None)
        highway_type = data.get('highway', 'Unknown')  # 获取道路种类

        if intensity is not None and not np.isnan(intensity):
            # 根据 intensity 设置颜色
            color = get_color(intensity)

            # 检查是否有 geometry, 使路径更加平滑
            if 'geometry' in data:
                coords = [(point[1], point[0]) for point in data['geometry'].coords]
            else:
                coords = [
                    (G.nodes[u]['y'], G.nodes[u]['x']),
                    (G.nodes[v]['y'], G.nodes[v]['x'])
                ]

            # 绘制路径或线段
            folium.PolyLine(
                coords,
                color=color,
                weight=4,  # 固定宽度
                opacity=0.9,
                tooltip=folium.Tooltip(f"Road Type: {highway_type}")
            ).add_to(layer)

    # 4. 在图层中标记计数器节点
    for _, row in known_data.iterrows():
        node = row['nearest_node']
        intensity = row['intensity']
        lat, lon = G.nodes[node]['y'], G.nodes[node]['x']
        folium.Marker(
        location=(lat, lon),
        icon=folium.Icon(color="blue"),  # 设置图标
        popup=folium.Popup(f"Intensity: {intensity}", max_width=200)  # 设置弹出框
    ).add_to(layer)

    # 将图层添加到地图
    layer.add_to(m)

# 添加图层控制
folium.LayerControl().add_to(m)

# 保存地图
output_map_path = "../Data/Data_EcoCompt_Combined/multi_date_intensity_map.html"
m.save(output_map_path)
print(f"多日期地图已保存到：{output_map_path}")




# %% 检查每条edges的属性是什么，以便能够了解有什么样的种类
from collections import Counter

# 提取所有边的 highway 属性
highway_types = []

for u, v, data in G.edges(data=True):
    highway = data.get('highway', None)  # 获取 highway 属性
    if highway:
        if isinstance(highway, list):  # 如果是列表，展开加入
            highway_types.extend(highway)
        else:
            highway_types.append(highway)

# 统计每种道路的数量
highway_counter = Counter(highway_types)

# 输出所有道路种类和数量
print("包含的道路种类及数量：")
for highway, count in highway_counter.items():
    print(f"{highway}: {count}")

