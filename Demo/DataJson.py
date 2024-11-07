LabelToName = {
    '0' : "烟", ## 感烟火灾探测器
    '1' : "温", ## 感温火灾探测器
    '2' : "消", ## 消火栓按钮？
    '3' : "强", #
    '4' : "声", # 声光报警器？
    '5' : "扬", ##
    '6' : "挡", # 电控挡烟垂壁？
    '7' : "排", ## 排风机？排烟防火阀？
    '8' : "卷", #
    '9' : "手", # 手动火灾报警按钮？
    '10' : "防", ## 防火阀
    '11' : "水", ##
    '12' : "信", #
    '13' : "门", ##
    '14' : "推", #
    '15' : "空调内机 - ",
    '16' : "空调外机",
    '17' : "常闭送风口",
    '18' : "非消防电源强切 1",
    '19' : "低压主开关柜",
    '20' : "馈线柜 - ",
    '21' : "新风室内机",
}
LabelToImg = {
    "0" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E7%83%9F.png",
    "1" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%B8%A9.png",
    "2" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%B6%88.png",
    "3" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E5%BC%BA.png",
    "4" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E5%A3%B0.png",
    "5" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%89%AC.png",
    "6" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%8C%A1.png",
    "7" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%8E%92.png",
    "8" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E5%8D%B7.png",
    "9" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%89%8B.png",
    "10" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E9%98%B2.png",
    "11" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%B0%B4.png",
    "12" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E4%BF%A1.png",
}

DescriptionToImgUrlTable = {
    "烟" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E7%83%9F.png",
    "温" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%B8%A9.png",
    "消" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%B6%88.png",
    "强" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E5%BC%BA.png",
    "声" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E5%91%8A%E8%AD%A6.png",
    "扬" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%89%AC.png",
    "挡" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%8C%A1.png",
    "排" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%8E%92.png",
    "卷" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E5%8D%B7.png",
    "手" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E7%81%AB%E7%81%BE%E6%8A%A5%E8%AD%A6%E4%B8%BB%E6%9C%BA.png",
    "防" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E9%98%B2.png",
    "水" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%B0%B4.png",
    "信" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E4%BF%A1.png",
    "门" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E9%97%A8.png",
    "推" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%8E%A8.png",
    "空调内机" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E7%A9%BA%E8%B0%83.png",
    "空调外机" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E7%A9%BA%E8%B0%83.png",
    "常闭送风口" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%96%B0%E9%A3%8E.png",
    "切" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E5%BC%BA%E5%88%87.png",
    "低压主开关柜" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E7%94%B5%E6%BA%90%E5%BC%80%E5%85%B3%E6%9F%9C.png",
    "馈" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E9%85%8D%E7%94%B5%E6%9F%9C.png",
    "新风室内机" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%96%B0%E9%A3%8E.png",
    "摄像" : "http://192.168.3.195/data-center/zjdc/upload/upload/image/%E6%91%84%E5%83%8F%E5%A4%B4.png",
}

def description_to_img(description):
    for keyword, url in DescriptionToImgUrlTable.items():
        if keyword in description:
            return url
    return ""
