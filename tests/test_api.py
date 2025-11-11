"""
简单API测试文件
用于测试LLM API连接是否正常工作
"""

import os
from dotenv import load_dotenv
import openai

# 加载环境变量
load_dotenv('.env.local')

print("开始测试API连接...")
print(f"API密钥: {os.getenv('AI_CLAUDE_API_KEY')[:8]}...")
print(f"基础URL: {os.getenv('AI_CLAUDE_BASE_URL')}")
print(f"模型名称: {os.getenv('ANTHROPIC_MODEL')}")

# 直接使用openai客户端进行测试
try:
    # 创建客户端实例
    client = openai.OpenAI(
        api_key=os.getenv('AI_CLAUDE_API_KEY'),
        base_url=os.getenv('AI_CLAUDE_BASE_URL')
    )
    
    print("\n客户端创建成功，尝试发送请求...")
    
    # 发送简单请求
    response = client.chat.completions.create(
        model=os.getenv('ANTHROPIC_MODEL', 'glm-4.6'),
        messages=[
            {"role": "user", "content": "你好，请简单介绍一下你自己。"}
        ],
        max_tokens=100
    )
    
    print(f"\n请求成功！")
    print(f"完整响应对象: {response}")
    print(f"响应类型: {type(response)}")
    print(f"响应属性: {dir(response)}")
    
    # 尝试获取回复内容（使用安全方式）
    if hasattr(response, 'choices') and response.choices:
        print(f"choices属性: {response.choices}")
        if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
            print(f"回复内容: {response.choices[0].message.content}")
        else:
            print("message或content属性不存在")
    else:
        print("choices属性不存在或为空")
    
    print("\nAPI测试完成！")
    
except Exception as e:
    print(f"\nAPI测试失败: {str(e)}")
    import traceback
    traceback.print_exc()