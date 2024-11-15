import asyncio
import json

import websockets

# WebSocket 服务器基类
# 继承这个类并按项目需求重载其中的交互函数
class WebSocketServer:
    def __init__(self, host='localhost', port=4567):
        self.host = host
        self.port = port
        self.clients = set()

    # 启动 WebSocket 服务器
    async def start_server(self):
        server = await websockets.serve(self.handle_client, self.host, self.port)
        print(f"WebSocket 服务器已启动，监听端口 {self.port}")
        await server.wait_closed()

    # 处理客户端连接
    async def handle_client(self, websocket):
        print(f"客户端已连接: {websocket.remote_address}")
        self.clients.add(websocket)
        try:
            async for message in websocket:
                # print(f"收到客户端消息: {message}")
                try:
                    json_data = json.loads(message)
                except json.JSONDecodeError as e:
                    print(f"并非JSON message")
                    continue
                response = await self.process_client_message(json_data)
                if response:
                    # await websocket.send(response)
                    pass
        except websockets.exceptions.ConnectionClosed as e:
            print(f"客户端断开连接: {e}")
            self.clients.remove(websocket)
        finally:
            self.clients.remove(websocket)
            print(f"连接关闭: {websocket.remote_address}")
            self.clients.remove(websocket)

    # 处理客户端消息 (请于子类重写此方法)
    async def process_client_message(self, json_data):
        if json_data['event'] == "hello":
            return "你好，客户端！这是服务端的响应。"
        elif json_data['event'] == "time":
            return f"当前时间是: {asyncio.get_event_loop().time()}"
        elif json_data['event'] == "bye":
            return "再见，客户端！"
        else:
            return f"未知命令: {json_data['event']}"

    # 向所有连接的客户端发送消息
    async def send_to_clients(self, message):
        if self.clients:
            # print(f"向 {len(self.clients)} 个客户端发送消息: {message}")
            await asyncio.gather(*(client.send(message) for client in self.clients))
        else:
            print("没有客户端连接，无法发送消息。")

    # 等待输入 (请于子类重写此方法)
    async def handle_input(self):
        loop = asyncio.get_running_loop()
        while True:
            command = await loop.run_in_executor(None, input, "等待输入: ")

            if command == "hello":
                await self.send_to_clients("你好，客户端！")
            elif command == "time":
                await self.send_to_clients(f"当前时间是: {asyncio.get_event_loop().time()}")
            elif command == "bye":
                await self.send_to_clients("再见，期待下次再见！")
            elif command.startswith("custom "):
                custom_message = command[7:]
                await self.send_to_clients(f"自定义消息: {custom_message}")
            else:
                print("未知命令")

    # 启动服务器和命令行监听
    async def main(self):
        await asyncio.gather(self.start_server(), self.handle_input())

# 主程序入口
if __name__ == "__main__":
    server = WebSocketServer()
    asyncio.run(server.main())
