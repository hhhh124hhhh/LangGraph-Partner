"""
天气查询工具
演示如何创建自定义工具供智能体使用
"""

from typing import Dict, Any
import random
from datetime import datetime

def get_weather(city: str) -> Dict[str, Any]:
    """
    获取指定城市的天气信息
    注意：这是一个模拟工具，实际使用时需要接入真实的天气API

    Args:
        city: 城市名称

    Returns:
        包含天气信息的字典
    """
    # 模拟天气数据
    weather_conditions = ["晴天", "多云", "阴天", "小雨", "大雨", "雪"]
    temperatures = {
        "北京": random.randint(-5, 35),
        "上海": random.randint(5, 38),
        "广州": random.randint(10, 35),
        "深圳": random.randint(12, 36),
        "杭州": random.randint(3, 37),
        "成都": random.randint(8, 30),
        "武汉": random.randint(2, 36),
        "西安": random.randint(0, 35),
    }

    temperature = temperatures.get(city, random.randint(0, 30))
    condition = random.choice(weather_conditions)

    return {
        "city": city,
        "temperature": temperature,
        "condition": condition,
        "humidity": random.randint(30, 90),
        "wind_speed": random.randint(0, 20),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def format_weather_response(weather_data: Dict[str, Any]) -> str:
    """
    格式化天气信息为易读的字符串

    Args:
        weather_data: 天气数据字典

    Returns:
        格式化的天气信息字符串
    """
    return f"""
📍 城市：{weather_data['city']}
🌡️ 温度：{weather_data['temperature']}°C
☁️ 天气：{weather_data['condition']}
💧 湿度：{weather_data['humidity']}%
💨 风速：{weather_data['wind_speed']} m/s
🕒 更新时间：{weather_data['timestamp']}
    """