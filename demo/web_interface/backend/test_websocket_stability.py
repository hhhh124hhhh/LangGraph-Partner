import asyncio
import websockets
import json
import time

async def test_websocket_stability():
    """测试WebSocket连接稳定性，验证心跳机制"""
    print("[STABILITY TEST] WebSocket 长时间连接测试开始")
    print("=" * 60)
    
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"[STABILITY TEST] 连接成功，开始测试心跳机制...")
            
            # 记录开始时间
            start_time = time.time()
            
            # 发送初始ping消息
            ping_msg = {"type": "ping", "payload": {}}
            await websocket.send(json.dumps(ping_msg))
            print(f"[STABILITY TEST] 发送初始ping: {ping_msg}")
            
            # 接收响应
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"[STABILITY TEST] 初始ping响应: {response_data}")
            
            # 测试1：保持连接2分钟，观察心跳
            test_duration = 120  # 120秒
            print(f"[STABILITY TEST] 开始 {test_duration} 秒连接保持测试...")
            
            # 定期发送ping
            for i in range(1, test_duration // 10 + 1):
                await asyncio.sleep(10)
                elapsed = time.time() - start_time
                
                # 发送ping
                ping_msg = {"type": "ping", "payload": {"timestamp": elapsed}}
                await websocket.send(json.dumps(ping_msg))
                print(f"[STABILITY TEST] 第 {i} 次ping (已运行 {elapsed:.1f} 秒)")
                
                # 接收pong
                try:
                    # 设置较短的超时，避免等待太久
                    pong_response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    pong_data = json.loads(pong_response)
                    print(f"[STABILITY TEST] 收到pong: {pong_data}")
                except asyncio.TimeoutError:
                    print(f"[STABILITY TEST] ERROR: pong响应超时")
                    return False
            
            # 发送正常消息测试
            await asyncio.sleep(1)
            print(f"[STABILITY TEST] 测试正常消息发送...")
            
            chat_msg = {
                "type": "message",
                "payload": {
                    "content": "长时间连接测试结束消息",
                    "session_id": "stability_test_session",
                    "attachments": []
                }
            }
            await websocket.send(json.dumps(chat_msg))
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                response_data = json.loads(response)
                print(f"[STABILITY TEST] 消息响应: {response_data}")
            except asyncio.TimeoutError:
                print(f"[STABILITY TEST] ERROR: 消息响应超时")
                return False
            
            # 测试结束
            total_time = time.time() - start_time
            print(f"[STABILITY TEST] 测试完成！连接保持时间: {total_time:.1f} 秒")
            print(f"[STABILITY TEST] ✅ WebSocket连接稳定，心跳机制正常工作")
            return True
            
    except Exception as e:
        print(f"[STABILITY TEST] ERROR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket_stability())
    if success:
        print("\n" + "=" * 60)
        print("[STABILITY TEST] 所有稳定性测试通过！")
        exit(0)
    else:
        print("\n" + "=" * 60)
        print("[STABILITY TEST] 稳定性测试失败！")
        exit(1)