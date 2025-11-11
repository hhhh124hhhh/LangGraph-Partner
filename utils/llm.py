"""
LLM配置模块
统一管理大语言模型的初始化和配置
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import json

# 加载环境变量，尝试加载.env文件和.env.local文件
load_dotenv('.env')
load_dotenv('.env.local')

# 打印环境变量加载状态
print(f"环境变量加载状态:")
print(f"ZHIPU_API_KEY: {'已设置' if os.getenv('ZHIPU_API_KEY') else '未设置'}")
print(f"ZHIPU_MODEL: {'已设置 - ' + os.getenv('ZHIPU_MODEL') if os.getenv('ZHIPU_MODEL') else '未设置 (使用默认值)'}")
print(f"AI_CLAUDE_API_KEY: {'已设置' if os.getenv('AI_CLAUDE_API_KEY') else '未设置'}")
print(f"AI_CLAUDE_BASE_URL: {'已设置' if os.getenv('AI_CLAUDE_BASE_URL') else '未设置'}")
print(f"OPENAI_API_KEY: {'已设置' if os.getenv('OPENAI_API_KEY') else '未设置'}")
print(f"OPENAI_BASE_URL: {'已设置' if os.getenv('OPENAI_BASE_URL') else '未设置'}")

class CustomLLM:
    """自定义LLM类，直接使用OpenAI客户端调用API"""
    def __init__(self, model="glm-3-turbo", temperature=0.7):
        # 从环境变量获取配置
        self.api_key = os.getenv('ZHIPU_API_KEY')
        # 设置完整的API URL路径
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        # 优先从环境变量读取模型名称，否则使用传入的参数或默认值
        self.model_name = os.getenv('ZHIPU_MODEL', model)  # 从环境变量读取模型
        self.temperature = temperature
        
        print(f"创建CustomLLM实例:")
        print(f"模型: {self.model_name}")
        print(f"温度: {self.temperature}")
        print(f"API密钥: {self.api_key[:8]}..." if self.api_key else "未设置")
        print(f"基础URL: {self.base_url}")
        
        # 创建OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def invoke(self, messages):
        """调用API并处理响应"""
        try:
            print(f"CustomLLM调用中，消息数量: {len(messages)}")
            print(f"使用模型: {self.model_name}")

            # 转换消息格式为智谱AI兼容的格式
            formatted_messages = []
            for msg in messages:
                if hasattr(msg, 'content') and hasattr(msg, 'type'):
                    # LangChain message format
                    content = msg.content
                    role = "user" if msg.type == "human" else "assistant" if msg.type == "ai" else "system"
                elif isinstance(msg, dict):
                    content = msg.get("content", "")
                    role = msg.get("role", "user")
                else:
                    content = str(msg)
                    role = "user"

                formatted_messages.append({
                    "role": role,
                    "content": content
                })

            # 调用API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                temperature=self.temperature
            )
            
            # 提取响应内容
            if hasattr(response, 'choices') and response.choices:
                # 标准OpenAI格式
                content = response.choices[0].message.content
                print(f"成功提取响应内容: {content[:50]}..." if content else "无内容")
                # 返回与LangChain兼容的格式
                return {"content": content, "role": "assistant"}
            else:
                print("尝试其他格式提取内容...")
                return {"content": "API调用成功但无法提取响应内容", "role": "assistant"}
                
        except Exception as e:
            print(f"CustomLLM调用错误: {e}")
            # 提供更友好的错误信息
            error_msg = str(e)
            if "401" in error_msg:
                print("❌ 认证失败: 请检查ZHIPU_API_KEY是否正确有效")
                print("   提示: 智谱AI的API密钥格式通常为 'xxx.xxx'，包含两部分")
            elif "404" in error_msg:
                print("❌ 模型不存在: 请检查模型名称是否正确")
                print("   推荐使用免费模型: glm-3-turbo")
                print("   其他可能的模型: glm-4, glm-4-flash")
            elif "429" in error_msg and "余额不足" in error_msg:
                print("💡 提示: 请尝试使用智谱AI的免费模型 'glm-3-turbo'")
                print("   或者充值您的智谱AI账户以使用高级模型")
            # 继续抛出异常，保持原有错误处理流程
            raise

def get_llm(model="glm-4.6", temperature=0.7):
    """
    获取配置好的LLM实例

    Args:
        model: 模型名称，默认使用glm-4.6
        temperature: 温度参数，控制回答的随机性

    Returns:
        CustomLLM: 配置好的LLM实例
    """
    return CustomLLM(model=model, temperature=temperature)

# 预定义的LLM实例
chat_llm = get_llm(temperature=0.7)
reasoning_llm = get_llm(temperature=0.1)