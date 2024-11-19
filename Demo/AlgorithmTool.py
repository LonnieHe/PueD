"""
This file implements some mathematical methods
Usually does not require modification of the file here
"""
import json

import cv2
import numpy as np

import DataJson
from collections import defaultdict


def quaternion_to_rotation_matrix(q):
    """
    将四元数转换为旋转矩阵。
    """
    x, y, z, w = q
    # 计算四元数旋转矩阵
    rotation_matrix = np.array([
        [1 - 2 * (y ** 2 + z ** 2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x ** 2 + z ** 2), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x ** 2 + y ** 2)]
    ])
    return rotation_matrix


def apply_transformation(points, quaternion, scale_factors):
    """
    对点应用四元数旋转和缩放变换。
    """
    # 获取旋转矩阵
    rotation_matrix = quaternion_to_rotation_matrix(quaternion)
    # print(rotation_matrix)
    # 应用缩放和旋转
    scaled_points = points * scale_factors  # 对每个坐标应用缩放

    transformed_points = scaled_points.dot(rotation_matrix.T)  # 使用旋转矩阵旋转

    return transformed_points

def remove_duplicate_vertices(vertices, triangles):
    # vertices = np.array(vertices)
    # 获取唯一顶点，并生成原始顶点到唯一顶点的索引映射
    unique_vertices, new_indices = np.unique(vertices, axis=0, return_inverse=True)

    # 更新三角形的顶点索引
    updated_triangles = np.array([new_indices[vertex] for vertex in triangles])

    return unique_vertices, updated_triangles

def sort_polygon_vertices(vertices, triangles):
    # 去除重复顶点
    vertices, triangles = remove_duplicate_vertices(vertices, triangles)
    # 构建边的计数器，统计每条边出现的次数
    edge_count = defaultdict(int)
    # 三角形数量
    num = len(triangles) / 3

    for i in range(int(num)):
        # 取出三角形的每条边
        v0 = vertices[triangles[i*3]]
        v1 = vertices[triangles[i*3+1]]
        v2 = vertices[triangles[i*3+2]]

        if abs(v0[2]) > 1 or abs(v1[2]) > 1 or abs(v2[2]) > 1:
        #   print("Z轴过远")
            continue

        edge_count[tuple(sorted((triangles[i*3], triangles[i*3 + 1])))] += 1
        edge_count[tuple(sorted((triangles[i*3 + 1], triangles[i*3 + 2])))] += 1
        edge_count[tuple(sorted((triangles[i*3 + 2], triangles[i*3])))] += 1

    # 提取轮廓边（即仅出现一次的边）
    contour_edges = [edge for edge, count in edge_count.items() if count == 1]

    # 如果没有足够的边形成多边形，直接返回
    if len(contour_edges) < 3:
        print("无法形成有效的多边形：轮廓边不足。")
        return []

    # 将轮廓边连成连续的顶点序列
    edge_dict = defaultdict(list)
    for edge in contour_edges:
        edge_dict[edge[0]].append(edge[1])
        edge_dict[edge[1]].append(edge[0])

    # 检查每个顶点是否有两个邻居（多边形的基本条件）
    for vertex, neighbors in edge_dict.items():
        if len(neighbors) != 2:
            print(f"顶点 {vertex} 的邻居数不是2，无法形成有效的多边形。")
            return []

    # 从某个顶点开始（任选一个轮廓顶点）
    start_vertex = contour_edges[0][0]
    current_vertex = start_vertex
    previous_vertex = None
    visited_edges = set()
    contour = []

    while True:
        contour.append(current_vertex)
        neighbors = edge_dict[current_vertex]

        # 找到未访问过的边
        next_vertex = neighbors[0] if neighbors[0] != previous_vertex else neighbors[1]
        edge = tuple(sorted((current_vertex, next_vertex)))

        if edge in visited_edges:
            print("出现重复边，无法形成有效的多边形。")
            return []

        visited_edges.add(edge)
        previous_vertex = current_vertex
        current_vertex = next_vertex

        if current_vertex == start_vertex:
            # 回到起点，检查是否形成有效的多边形
            if len(contour) >= 3:
                break
            else:
                print("形成的多边形不合法，顶点数不足。")
                return []
    # 根据顶点索引返回排序好的顶点坐标
    # print(contour)
    ordered_vertices = [vertices[i][:2] for i in contour]
    return np.array(ordered_vertices, dtype=np.int32)
    # return ordered_vertices

# 给出UE无序顶点构造多边形
# 无法保证角度递增，不使用
def create_polygon_from_vertices(vertices, center):
    # 计算多边形的顶点（向量形式）
    vectors = vertices - center
    # 这一步是因为UE的坐标系和CV的坐标系不同，需要翻转y轴
    vectors[:, 1] *= -1
    # 计算每个顶点的极角，cv2.phase 返回的是角度，范围 [0, 2π)
    print(vectors)
    angles = cv2.phase(vectors[:, 0].astype(np.float32), vectors[:, 1].astype(np.float32))
    angles = angles.ravel()
    print(angles)
    # 根据极角进行排序
    sorted_indices = np.argsort(angles)
    # 重新排列顶点，作为多边形的顶点
    print(sorted_indices)
    polygon = vertices[sorted_indices]
    return polygon

# 生成网格分布在多边形内部的点
def grid_points_in_polygon(polygon, step_x, step_y):
    points = []
    if len(polygon) != 0:
        # 获取多边形的外接矩形边界
        x_min, y_min, width, height = cv2.boundingRect(polygon)
        # 创建网格点
        for x in np.arange(x_min, x_min + width, step_x):
            for y in np.arange(y_min, y_min + height, step_y):
                if cv2.pointPolygonTest(polygon, np.array((x, y), dtype=np.float32), False) > 0:
                    points.append((x, y))

    return np.array(points)


# 生成网格分布在多边形内部的点
# points = grid_points_in_polygon(polygon, 10)
if __name__ == "__main__":
    parsed_data = json.loads(DataJson.FakeMessage3)
    vertices = parsed_data['payload']['Vertices']
    rotation = parsed_data['payload']['location']['Rotation']
    scale = parsed_data['payload']['location']['Scale3D']

    points = np.array([[int(point['X']), int(point['Y']), int(point['Z'])] for point in vertices])
    q = np.array([rotation['X'], rotation['Y'], rotation['Z'],rotation['W']])
    scale_factors = np.array([ scale['X'], scale['Y'], scale['Z']])
    triangles = parsed_data['payload']['Triangles']
    print(q)
    print(scale_factors)

    print(points)
    points = apply_transformation(points, q, scale_factors)
    print(points)
    # 这是以mesh的局部坐标计算
    polygon = sort_polygon_vertices(points, triangles)
    print(polygon)
    points = grid_points_in_polygon(polygon, 20, 10)
    print('new points location:')
    print(type(points))
    print(points)