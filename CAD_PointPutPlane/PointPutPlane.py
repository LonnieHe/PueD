# 这里的脚本是配合蓝图PointPutPlane使用的，用于将UE输出的坐标值拼接成后端可调用的表
# 格式不同于BatchGen
# 目前只考虑视频标签的模板
import csv
import json
import math

import pandas as pd
# UE转换出的code坐标数据
ue_file_path = "E:/DgeneProjects/futurecitydata/WXY全部.csv"
# 具有视频id的资产表
id_file_path = "E:/DgeneProjects/futurecitydata/监控 id tag.csv"
# 输出的csv文件
output_file_path = "./output_video.csv"
# 输出的json文件
output_json_path = "./output_video.json"

if __name__ == "__main__":
    # 读取数据
    device_table = pd.read_csv(ue_file_path, dtype=str).fillna("")
    id_table = pd.read_csv(id_file_path, dtype=str).fillna("")

    grouped_data = id_table.groupby('图纸编号').apply(lambda x: x.to_dict(orient='records')).to_dict()
    # print(grouped_data)
    video_csvfile = open(output_file_path, mode='w', newline='', encoding='utf-8')
    video_fieldnames = ["Payload"]
    writer = csv.DictWriter(video_csvfile, fieldnames=video_fieldnames)
    writer.writeheader()
    # 按行读取数据
    payloads = []
    for index, ue_row in device_table.iterrows():
        # print(f"Row {index}: Code={row['code']}, X={row['X']}, Y={row['Y']}, Z={row['Z']}, Id={row['Id']}, Tag={row['Tag']}")
        # 查询资产表获取id和tag信息
        if ue_row['Code'] in grouped_data:
            id_record = grouped_data[ue_row['Code']]
            id_record = id_record[0]
        else:
            print(f"Code {ue_row['Code']} not found in id table")
            continue
        # print(recode)

        tags = id_record['tags'][1:-1].replace("'", '').replace(" ", '').split(',')

        if id_record['cameraIndexCode'] == "":
            tags += ['NoStream']
        else:
            tags += ['Stream']

        # tags = tags[1:-1]
        # print(tags)
        payload = {
            "object_id": id_record['设备编号'],
            "object_class": "UltraVideoTag",
            "name": ue_row['Code'],
            "layer": "default",
            "visible": True,
            "tags":tags,
            "transform": {
                "coord_type": "UE4",
                "coord": {
                    "x": ue_row['X'],
                    "y": ue_row['Y'],
                    "z": ue_row['Z']
                },
                "rotate": {
                    "roll": 0,
                    "pitch": 0,
                    "yaw": 0
                },
                "scale": {
                    "X": 1,
                    "Y": 1,
                    "Z": 1
                }
            },
            "class_prop": {
                "preset_type": "Minimalism",
                "display_name": id_record['设备编号'],
                "video_id": id_record['cameraIndexCode']
            }
        }
        payloads.append(payload)
        # csv_data = {
        #     # "ObjectId": row['Id'],
        #     # "Code": row['code'],
        #     # "Tags": row['Tag'],
        #     # "Payload": payload
        #     "Payload": json.dumps(payload, ensure_ascii=False)
        # }
        # writer.writerow(csv_data)

    video_csvfile.close()
    with open(output_json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(payloads, jsonfile, ensure_ascii=False, indent=4)

# replacements = {
#     '""[': '[',
#     '\\\"\"': '"',
#     ']""': ']',
#     '""': '"',
# }
#
# with open(output_file_path, "r+", encoding="utf-8") as csvfile:
#     content = csvfile.read()  # 读取文件内容
#     csvfile.seek(0)  # 回到文件开头
#     for old, new in replacements.items():
#         content = content.replace(old, new)  # 替换并写回
#     csvfile.write(content)
#     csvfile.truncate()  # 截断多余内容
# csvfile.close()
