"""
AI Partner 智能体集成
封装现有的AI Partner代码，提供统一的API接口
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入现有的AI Partner模块
try:
    from agents.partner_agent import AIPartnerAgent, create_partner_agent
    from utils.persona_manager import PersonaManager
    from utils.memory_manager import MemoryManager
    from utils.vector_store import VectorStore
    from utils.llm import CustomLLM
except ImportError as e:
    logging.warning(f"无法导入AI Partner模块: {e}")
    # 这里可以创建替代的模拟实现
    AIPartnerAgent = None
    create_partner_agent = None

logger = logging.getLogger(__name__)


class AIPartnerService:
    """AI Partner 服务封装类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化AI Partner服务

        Args:
            config: 配置字典
        """
        self.config = config
        self.agent: Optional[AIPartnerAgent] = None
        self.initialized = False
        self.initialization_error: Optional[str] = None

        # 初始化各个组件
        self._initialize_components()

    def _initialize_components(self):
        """初始化AI Partner组件"""
        try:
            if not AIPartnerAgent:
                raise ImportError("AI Partner模块未正确安装")

            # 获取配置路径
            config_dir = self.config.get("config_dir", "./config")
            vector_db_path = self.config.get("vector_db_path", "./vector_db")
            memory_dir = self.config.get("memory_dir", "./memory")

            # 创建目录
            Path(config_dir).mkdir(parents=True, exist_ok=True)
            Path(vector_db_path).mkdir(parents=True, exist_ok=True)
            Path(memory_dir).mkdir(parents=True, exist_ok=True)

            # 初始化AI Partner智能体
            logger.info("正在初始化AI Partner智能体...")
            self.agent = AIPartnerAgent(
                config_dir=config_dir,
                vector_db_path=vector_db_path,
                memory_dir=memory_dir
            )

            # 验证组件状态
            self._verify_components()

            self.initialized = True
            logger.info("✅ AI Partner服务初始化成功")

        except Exception as e:
            error_msg = f"AI Partner服务初始化失败: {str(e)}"
            logger.error(error_msg)
            self.initialization_error = error_msg
            self.initialized = False

            # 创建模拟智能体作为后备
            self._create_mock_agent()

    def _verify_components(self):
        """验证组件状态"""
        try:
            if self.agent:
                session_info = self.agent.get_session_info()
                logger.info(f"会话信息: {session_info}")
        except Exception as e:
            logger.warning(f"组件验证失败: {e}")

    def _create_mock_agent(self):
        """创建模拟智能体作为后备"""
        try:
            self.mock_agent = MockAIPartner(self.config)
            logger.info("✅ 模拟智能体创建成功")
        except Exception as e:
            logger.error(f"模拟智能体创建失败: {e}")

    async def chat(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        进行AI对话

        Args:
            message: 用户消息
            session_id: 会话ID

        Returns:
            对话结果
        """
        start_time = datetime.now()

        try:
            if not self.initialized and self.initialization_error:
                # 使用模拟智能体
                if hasattr(self, 'mock_agent'):
                    return await self.mock_agent.chat(message, session_id)
                else:
                    raise Exception(f"服务未初始化: {self.initialization_error}")

            # 使用真实的AI Partner
            response = await self.agent.chat(message)
            processing_time = (datetime.now() - start_time).total_seconds()

            # 获取会话信息
            session_info = self.agent.get_session_info()

            return {
                "success": True,
                "response": response,
                "session_id": session_info.get("session_id", "unknown"),
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "agent_type": "real",
                    "session_info": session_info
                }
            }

        except Exception as e:
            logger.error(f"对话处理失败: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()

            # 尝试使用模拟智能体
            if hasattr(self, 'mock_agent'):
                try:
                    return await self.mock_agent.chat(message, session_id)
                except Exception as mock_e:
                    logger.error(f"模拟智能体也失败: {mock_e}")

            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，我暂时无法处理您的请求。请稍后再试。",
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "metadata": {"agent_type": "error"}
            }

    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        try:
            if self.initialized and self.agent:
                return self.agent.get_session_info()
            elif hasattr(self, 'mock_agent'):
                return self.mock_agent.get_session_info()
            else:
                return {"error": "服务未初始化"}
        except Exception as e:
            logger.error(f"获取会话信息失败: {e}")
            return {"error": str(e)}

    def get_persona_context(self) -> str:
        """获取画像上下文"""
        try:
            if self.initialized and self.agent:
                # 从persona_manager获取上下文
                return self.agent.persona_manager.get_persona_context()
            elif hasattr(self, 'mock_agent'):
                return self.mock_agent.get_persona_context()
            else:
                return "画像上下文不可用"
        except Exception as e:
            logger.error(f"获取画像上下文失败: {e}")
            return f"获取画像上下文失败: {str(e)}"

    def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索知识库"""
        try:
            if self.initialized and self.agent:
                results = self.agent.vector_store.search(query, top_k=top_k)
                return results
            elif hasattr(self, 'mock_agent'):
                return self.mock_agent.search_knowledge(query, top_k)
            else:
                return []
        except Exception as e:
            logger.error(f"知识搜索失败: {e}")
            return []

    async def close(self):
        """关闭服务"""
        try:
            if self.initialized and self.agent:
                await self.agent.close()
            logger.info("AI Partner服务已关闭")
        except Exception as e:
            logger.error(f"关闭AI Partner服务失败: {e}")


class MockAIPartner:
    """模拟AI Partner实现，作为后备方案"""

    def __init__(self, config: Dict[str, Any]):
        """初始化模拟智能体"""
        self.config = config
        self.conversation_history = []

    async def chat(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """模拟对话"""
        # 简单的模拟回应逻辑
        responses = [
            f"我收到了您的消息：{message}",
            f"关于'{message}'，这是一个很好的问题。",
            f"让我想想关于'{message'的相关信息...",
            f"根据我的理解，{message}涉及到技术实现方面。",
        ]

        import random
        response = random.choice(responses)

        # 添加一些模拟的技术建议
        if "LangGraph" in message:
            response += "\n\nLangGraph是一个强大的框架，特别适合构建复杂的AI智能体。您可以参考官方文档来学习更多。"

        if "代码" in message or "编程" in message:
            response += "\n\n我建议您先从基础的示例开始，逐步理解状态图的工作原理。"

        return {
            "success": True,
            "response": response,
            "session_id": session_id or "mock_session",
            "processing_time": 0.5,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "agent_type": "mock",
                "message_length": len(message)
            }
        }

    def get_session_info(self) -> Dict[str, Any]:
        """获取模拟会话信息"""
        return {
            "session_id": "mock_session",
            "agent_type": "mock",
            "status": "running",
            "capabilities": ["对话", "模拟回应"]
        }

    def get_persona_context(self) -> str:
        """获取模拟画像上下文"""
        return """
## 用户画像
- 角色：开发者
- 背景：学习LangGraph和AI开发
- 目标：构建智能的AI系统

## AI画像
- 角色：AI助手
- 能力：提供技术指导和示例代码
- 风格：友好、专业
        """

    def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """模拟知识搜索"""
        return [
            {
                "content": f"关于'{query}'的模拟搜索结果 {i+1}",
                "metadata": {"source": "mock_database", "relevance": 0.8 - i*0.1},
                "similarity": 0.8 - i*0.1
            }
            for i in range(min(top_k, 3))
        ]


# 全局服务实例
_ai_partner_service: Optional[AIPartnerService] = None


def get_ai_partner_service(config: Optional[Dict[str, Any]] = None) -> AIPartnerService:
    """
    获取AI Partner服务实例

    Args:
        config: 配置字典

    Returns:
        AI Partner服务实例
    """
    global _ai_partner_service

    if _ai_partner_service is None:
        if config is None:
            # 使用默认配置
            config = {
                "config_dir": "./config",
                "vector_db_path": "./vector_db",
                "memory_dir": "./memory"
            }

        _ai_partner_service = AIPartnerService(config)

    return _ai_partner_service


async def initialize_ai_partner(config: Dict[str, Any]) -> bool:
    """
    初始化AI Partner服务

    Args:
        config: 配置字典

    Returns:
        是否初始化成功
    """
    try:
        service = get_ai_partner_service(config)
        return service.initialized
    except Exception as e:
        logger.error(f"初始化AI Partner失败: {e}")
        return False


def is_ai_partner_available() -> bool:
    """检查AI Partner是否可用"""
    try:
        service = get_ai_partner_service()
        return service.initialized
    except Exception:
        return False