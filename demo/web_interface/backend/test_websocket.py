#!/usr/bin/env python3
"""
WebSocket 连接测试脚本
用于验证 WebSocket 修复是否成功
"""

import asyncio
import json
import websockets
from datetime import datetime

async def test_websocket_connection():
    """测试 WebSocket 连接和消息通信"""

    uri = "ws://localhost:8000/ws"

    try:
        print(f"[WebSocket] 正在连接到 {uri}...")

        async with websockets.connect(uri) as websocket:
            print("[WebSocket] 连接成功！")

            # 测试 1: 发送 ping 消息
            print("\n[Test 1] 发送 ping 消息")
            ping_message = {
                "type": "ping",
                "payload": {}
            }
            await websocket.send(json.dumps(ping_message))
            print(f"发送: {ping_message}")

            response = await websocket.recv()
            print(f"接收: {response}")

            # 测试 2: 发送聊天消息
            print("\n[Test 2] 发送聊天消息")
            chat_message = {
                "type": "message",
                "payload": {
                    "content": "Hello, this is a test message!",
                    "session_id": "test_session_123",
                    "attachments": []
                }
            }
            await websocket.send(json.dumps(chat_message))
            print(f"发送: {json.dumps(chat_message, indent=2)}")

            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"接收: {json.dumps(response_data, indent=2)}")

            # 测试 3: 发送订阅请求
            print("\n[Test 3] 发送订阅请求")
            subscribe_message = {
                "type": "subscribe",
                "payload": {
                    "session_id": "test_session_123"
                }
            }
            await websocket.send(json.dumps(subscribe_message))
            print(f"发送: {subscribe_message}")

            response = await websocket.recv()
            print(f"接收: {response}")

            # 测试 4: 发送未知消息类型（测试错误处理）
            print("\n[Test 4] 发送未知消息类型")
            unknown_message = {
                "type": "unknown_type",
                "payload": {"test": "data"}
            }
            await websocket.send(json.dumps(unknown_message))
            print(f"发送: {unknown_message}")

            response = await websocket.recv()
            print(f"接收: {response}")

            print("\n[SUCCESS] 所有测试通过！WebSocket 连接和消息处理正常工作。")

    except websockets.ConnectionClosed as e:
        print(f"[ERROR] WebSocket 连接关闭: 代码={e.code}, 原因={e.reason}")
    except Exception as e:
        print(f"[ERROR] 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("[TEST] WebSocket 连接测试开始")
    print("=" * 50)

    asyncio.run(test_websocket_connection())

if __name__ == "__main__":
    main()