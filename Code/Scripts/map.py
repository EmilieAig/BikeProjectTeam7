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


# %%
import osmnx as ox
ox.settings.use_cache=True
ox.__version__

import osmnx as ox
from shapely.geometry import Polygon

# 定义经纬度范围
polygon = Polygon([
    (3.86321, 43.68513),
    (3.80804, 43.64595),
    (3.67027, 43.53212),
    (3.8362, 43.4938),
    (3.95197, 43.56945),
    (3.94459, 43.64167),
    (3.92177, 43.68116),
    (3.86321, 43.68513)  # 闭合多边形
])

# 使用自定义多边形提取自行车网络
G = ox.graph_from_polygon(polygon, network_type='bike')


# 定义要保留的道路类型
desired_highways = {'primary', 'trunk', 'secondary', 'tertiary', 'secondary_link', 'unclassified', 'trunk_link', 'primary_link', 'cycleway', 'tertiary_link', 'living_street', 'track', 'bridleway', 'residential'}

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


# 可视化网络
print(f"nb edges: {G.number_of_edges()}")
print(f"nb nodes: {G.number_of_nodes()}")
fig, ax = ox.plot_graph(G)


# %% 将计数器的坐标和节点坐标进行匹配
import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt

# 1. 加载自行车网络图
# 2. 读取计数器数据
counter_file_path = "../Data/Data_EcoCompt_Combined/counter_coordinates.csv"
counters = pd.read_csv(counter_file_path)

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

# %% 
for u, v, data in G.edges(data=True):
    print(data.get('highway'))


# %% 导入某日数据
import pandas as pd
import os

# 文件路径设置
combined_file_path = "../Data/Data_EcoCompt_Combined/fichier_combined.csv"


# 1. 读取计数器数据和最近节点信息
combined_data = pd.read_csv(combined_file_path, delimiter=";")

# 2. 过滤出 2023-07-10 的数据
filtered_data = combined_data[combined_data['date'] == '2023-07-10']

# 3. 提取计数器基础 ID
filtered_data['counter_id'] = filtered_data['id'].str.extract(r'(MMM_EcoCompt_\w+?)_')

# 4. 将计数器与最近节点匹配
# 合并过滤数据和最近节点数据
merged_data = pd.merge(counters, filtered_data, on='counter_id', how='inner')

# 5. 汇总每个节点的计数信息
node_intensity = merged_data[['nearest_node', 'intensity']]

# 6. 保存结果
output_file_path = "../Data/Data_EcoCompt_Combined/node_intensity_20230710.csv"
node_intensity.to_csv(output_file_path, index=False)

print(f"节点的计数信息已保存到：{output_file_path}")


# %%
print(node_intensity.head())





# %% 推算未知节点的intensity
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
import os

# 文件保存路径设置
output_file_path = os.path.join("..", "Data", "Data_EcoCompt_Combined", "unknown_nodes_intensity.csv")

# 提取已知节点信息
known_nodes = node_intensity['nearest_node'].tolist()
known_coords = np.array([[G.nodes[node]['x'], G.nodes[node]['y']] for node in known_nodes])
known_intensities = node_intensity['intensity'].values

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

# 遍历未知节点，计算与最近3个已知节点的加权平均值
for coord in unknown_coords:
    # 查询最近的3个已知节点
    distances, indices = kd_tree.query(coord, k=3)
    
    # 加权计算 intensity
    weights = 1 / distances  # 权重是距离的倒数
    weighted_intensity = np.sum(weights * known_intensities[indices]) / np.sum(weights)
    unknown_intensity.append(weighted_intensity)

# 将估算值保存到未知节点中
for i, node in enumerate(unknown_nodes):
    G.nodes[node]['intensity'] = unknown_intensity[i]

# 保存结果到文件
unknown_intensity_df = pd.DataFrame({
    'node': unknown_nodes,
    'intensity': unknown_intensity
})
unknown_intensity_df.to_csv(output_file_path, index=False)
print(f"未知节点的 intensity 已保存到：{output_file_path}")






# %%
import folium
import numpy as np
import matplotlib.pyplot as plt

# 1. 将 intensity 赋值给图 G 的节点
for node in node_intensity['nearest_node']:
    G.nodes[node]['intensity'] = node_intensity.set_index('nearest_node').loc[node, 'intensity']

for i, node in enumerate(unknown_nodes):
    G.nodes[node]['intensity'] = unknown_intensity[i]

# 检查赋值结果
print("节点 intensity 已赋值")

# %%
# 2. 计算每条边的 intensity
for u, v, data in G.edges(data=True):
    node_u_intensity = G.nodes[u].get('intensity', np.nan)
    node_v_intensity = G.nodes[v].get('intensity', np.nan)
    
    # 使用 np.isnan 需要确保是标量值
    if np.isscalar(node_u_intensity) and np.isscalar(node_v_intensity) and not (np.isnan(node_u_intensity) or np.isnan(node_v_intensity)):
        data['intensity'] = (node_u_intensity + node_v_intensity) / 2
    else:
        data['intensity'] = np.nan  # 如果节点 intensity 不可用，设为 NaN

print("边 intensity 已计算")


# %% 可视化部分，预期达到示例图片的效果
# 3. 可视化图 G 的边 intensity
import folium

# 创建 folium 地图
center_coords = [43.611, 3.877]  # 替换为你的地图中心
m = folium.Map(location=center_coords, zoom_start=13)

# 定义颜色映射规则
def get_color(intensity):
    if intensity > 1500:
        return '#FE4528'
    elif intensity > 1200:
        return '#FD6121'
    elif intensity > 900:
        return '#FB9234'
    elif intensity > 600:
        return '#FFEF3A'
    elif intensity > 300:
        return '#6CD932'
    else:
        return '#23C326'

# 添加边到地图
for u, v, data in G.edges(data=True):
    intensity = data.get('intensity', None)
    highway_type = data.get('highway', 'Unknown')  # 获取道路种类

    if intensity is not None and not np.isnan(intensity):
        # 根据 intensity 设置颜色
        color = get_color(intensity)

        # 检查是否有 geometry
        if 'geometry' in data:
            # 如果有 geometry，使用实际的几何线段
            coords = [(point[1], point[0]) for point in data['geometry'].coords]  # 反转为 (lat, lon)
        else:
            # 如果没有 geometry，用节点坐标连线
            coords = [
                (G.nodes[u]['y'], G.nodes[u]['x']),
                (G.nodes[v]['y'], G.nodes[v]['x'])
            ]

        # 绘制平滑路径或线段
        folium.PolyLine(
            coords,
            color=color,
            weight=3,  # 固定宽度
            opacity=0.8,
            tooltip=folium.Tooltip(f"Road Type: {highway_type}")  # 悬停时显示道路类型
        ).add_to(m)

# 标记计数器节点
for _, row in node_intensity.iterrows():
    node = row['nearest_node']
    intensity = row['intensity']
    # 获取节点坐标
    lat, lon = G.nodes[node]['y'], G.nodes[node]['x']
    # 添加圆形标记
    folium.CircleMarker(
        location=(lat, lon),
        radius=5,  # 标记的大小
        color='#0074E0',  # 边框颜色
        fill=True,
        fill_color='#0074E0',  # 填充颜色
        fill_opacity=0.8,
        tooltip=folium.Tooltip(f"Intensity: {intensity}")  # 悬停时显示
    ).add_to(m)        

# 保存地图
output_map_path = "../Data/Data_EcoCompt_Combined/edge_intensity_map.html"
m.save(output_map_path)
print(f"地图已保存到：{output_map_path}")



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

# %%
