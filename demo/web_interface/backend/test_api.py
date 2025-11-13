import requests

# 测试健康检查端点
try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    print(f"健康检查端点状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
except Exception as e:
    print(f"健康检查端点测试失败: {e}")

# 测试WebSocket连接
try:
    import websocket
    ws = websocket.WebSocket()
    ws.connect('ws://localhost:8000/ws')
    print("WebSocket连接成功")
    ws.close()
except Exception as e:
    print(f"WebSocket连接测试失败: {e}")