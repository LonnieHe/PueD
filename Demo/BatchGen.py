import asyncio
import csv
import json
from collections import defaultdict

import numpy as np
import pandas as pd

import DataJson
import NameToImage
from WebServer import WebSocketServer
import AlgorithmTool

port = 4567
file_path = 'E:/DgeneProjects/futurecitydata/all_1114.csv'
grouped_data = {}
room_location = defaultdict(dict)
room_valid_points = defaultdict(lambda: np.zeros((1, 2)))


class CustomWebSocketServer(WebSocketServer):
    async def process_client_message(self, json_data):
        # delete under this 3 line if working on 5.1
        json_data = json_data.get('result')
        if not json_data:
            return

        if json_data['event'] == "SmartBuilding/GetRoomLocation":
            # room_id = json_data['payload']['room_id']
            # print(f"收到房间信息: {room_id}")
            if json_data['status'] == 0:
                room_id = json_data['payload']['room_id']
                # 每收到一个房间信息，计算并存储可用位置
                room_location[room_id] = json_data['payload']['location']['Translation']
                rotation = json_data['payload']['location']['Rotation']
                scale = json_data['payload']['location']['Scale3D']
                vertices = json_data['payload']['Vertices']
                triangles = json_data['payload']['Triangles']

                points = np.array([[point['X'], point['Y'], point['Z']] for point in vertices])
                q = np.array([rotation['X'], rotation['Y'], rotation['Z'], rotation['W']])
                scale_factors = np.array([scale['X'], scale['Y'], scale['Z']])
                # 矫正局部坐标和去重顶点
                points = AlgorithmTool.apply_transformation(points, q, scale_factors)
                # 生成多边形
                polygon = AlgorithmTool.sort_polygon_vertices(points, triangles)
                # 使用参数生成网格点
                valid_points = AlgorithmTool.grid_points_in_polygon(polygon, 120, 80)

                room_valid_points[room_id] = valid_points
            # else:
            #     print("房间不存在: ", room_id)

            return
        else:
            # 调用父类的处理逻辑
            return await super().process_client_message(json_data)

    async def handle_input(self):
        loop = asyncio.get_running_loop()
        while True:
            command = await loop.run_in_executor(None, input, "等待输入: ")

            if command == "collect":
                await self.collect_room()
            elif command == "set":
                await self.set_points(False)
            elif command == "file":
                await self.set_points(True)
            elif command == "move":
                await self.send_to_clients(json.dumps(NameToImage.ZCZ_1))
            elif command.startswith("custom "):
                custom_message = command[7:]
                await self.send_to_clients(f"自定义消息: {custom_message}")
            else:
                await super().process_client_message(command)

    async def collect_room(self):
        for room_id in grouped_data.keys():
            json_back = {
                "event": "SmartBuilding/GetRoomLocation",
                "payload": {
                    "room_id": room_id
                }
            }
            await self.send_to_clients(json.dumps(json_back))

    async def set_points(self, file):
        if file:
            csvfile =  open("./output.csv", mode='w', newline='', encoding='utf-8')
            fieldnames = ["ObjectId", "objectClass*", "名称*", "图层", "标签", "是否可见", "Transform*", "ClassProp*",
                              "ParentObjectId", "CallbackData"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

        try:
            for location_id, devices in grouped_data.items():

                if location_id not in room_location:
                    print(f"房间 {location_id} 不存在, 因此未计算可用位置。")
                    continue

                if(room_valid_points[location_id].shape[0] < len(devices)):
                    print(f"房间 {location_id} 可用位置为{room_valid_points[location_id].shape[0]}不足{len(devices)}，无法生成所有设备。")
                    continue

                selected_points = room_valid_points[location_id][np.random.choice(room_valid_points[location_id].shape[0], len(devices), replace=False)]
                np.random.shuffle(selected_points)
                # print(f"{location_id}当前房间高度: {room_location[location_id]['Z']}")
                for i, device in enumerate(devices):
                    # 设置基础位置
                    transform = {
                        "coord_type": "UE4",
                        "cad_mapkey": "",
                        "coord": {"x": room_location[location_id]['X'] + selected_points[i][0],
                                  "y": room_location[location_id]['Y'] + selected_points[i][1],
                                  "z": room_location[location_id]['Z']},
                        "rotate": {"roll": 0, "pitch": 0, "yaw": 0},
                        "scale": {"x": 1, "y": 1, "z": 1}
                    }
                    # 设置基础属性
                    classprop = {
                                        "name": device['description'],
                                        "Type": "Type1",
                                        "auto_scale": True, "image_id": "",
                                        "image_style": {"alignment": {"X": 0.5, "Y": 1}, "image_size": {"X": 33, "Y": 33},
                                                        "offset": {"X": 0, "Y": 0}, "tint": {"A": 1, "B": 1, "G": 1, "R": 1}},
                                        "image_url": DataJson.description_to_img(device['description']),
                                        "inverse_z_order": False, "point_scale": 1, "show_sphere": False,
                                        "text_content": device['description'],
                                        "text_style": {"alignment": {"X": 0, "Y": 1},
                                                       "background_color": {"A": 0.6000000238418579, "B": 0, "G": 0, "R": 0},
                                                       "font_color": {"A": 1, "B": 0.5, "G": 0.5, "R": 0.5}, "font_size": 16,
                                                       "offset": {"X": 20, "Y": 0},
                                                       "padding": {"Bottom": 0, "Left": 4, "Right": 4, "Top": 2.5}}
                    }
                    # 拼接位置tag
                    location_tags = device['location'].split('-', 2)[2].split('-', 3)
                    # 拼接设备tag
                    device_tags = device['assetno'].split('-')
                    tags = location_tags + [device_tags[2], device_tags[4]]
                    # 如果设备tag长度大于5，且第6位是A或B，则视作设备级别加入
                    if len(device_tags) > 5 and device_tags[5] in ['A', 'B']:
                        tags += [device_tags[5]]
                    # 拼接构造对应的的数据格式
                    if file:
                        csv_data = {
                            "ObjectId": device['assetno'],
                            "objectClass*": "ImageDisplay",
                            "名称*": device['description'],
                            "图层": "default",
                            "标签": ','.join(tags),
                            "是否可见": True,
                            "Transform*": json.dumps(transform),
                            "ClassProp*": json.dumps(classprop),
                            "ParentObjectId": "",
                            "CallbackData": "",
                        }
                        writer.writerow(csv_data)
                    else:
                        json_back = {
                            "event": "VirtualObject/Spawn",
                            "payload":
                                {
                                    "object_id": device['assetno'],
                                    "object_class": "ImageDisplay",
                                    "name": device['description'],
                                    "tags": tags,
                                    "visible": 'true',
                                    "transform": transform,
                                    "class_prop": classprop,
                                    "callback_data":
                                        {
                                        }
                                }
                        }
                        await self.send_to_clients(json.dumps(json_back))
        finally:
            if file:
                csvfile.close()

if __name__ == "__main__":

    df = pd.read_csv(file_path)
    grouped_data = df.groupby('location').apply(lambda x: x.to_dict(orient='records')).to_dict()
    # print(grouped_data)

    server = CustomWebSocketServer(host='localhost', port=4567)
    asyncio.run(server.main())

