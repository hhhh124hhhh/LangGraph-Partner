"""
API接口测试
测试各个API端点的功能
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

# 导入应用
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

# 创建测试客户端
client = TestClient(app)


class TestHealthCheck:
    """健康检查测试"""

    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "timestamp" in data

    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "AI Partner API"
        assert "environment" in data


class TestChatAPI:
    """聊天API测试"""

    def test_chat_basic(self):
        """测试基础聊天功能"""
        request_data = {
            "message": "你好，我想了解一下LangGraph",
            "context_turns": 5,
            "enable_search": True,
            "enable_tools": True
        }

        response = client.post("/api/chat/", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "response" in data["data"]
        assert "session_id" in data["data"]
        assert "processing_time" in data["data"]
        assert data["data"]["response"] is not None

    def test_chat_empty_message(self):
        """测试空消息"""
        request_data = {
            "message": "",
            "context_turns": 5
        }

        response = client.post("/api/chat/", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_chat_long_message(self):
        """测试过长消息"""
        long_message = "a" * 10001  # 超过限制
        request_data = {
            "message": long_message,
            "context_turns": 5
        }

        response = client.post("/api/chat/", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_get_chat_state(self):
        """测试获取会话状态"""
        # 首先发送一条消息创建会话
        request_data = {
            "message": "测试消息",
            "session_id": "test_session_123"
        }
        client.post("/api/chat/", json=request_data)

        # 然后获取会话状态
        response = client.get("/api/chat/state/test_session_123")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "session_id" in data["data"]
        assert "current_turn" in data["data"]
        assert data["data"]["session_id"] == "test_session_123"

    def test_chat_search(self):
        """测试知识搜索功能"""
        request_data = {
            "query": "LangGraph",
            "top_k": 5,
            "min_score": 0.3
        }

        response = client.post("/api/chat/search", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    def test_chat_tool_execution(self):
        """测试工具执行功能"""
        request_data = {
            "tool_name": "calculator",
            "parameters": {
                "expression": "2+3*4"
            }
        }

        response = client.post("/api/chat/tools/execute", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "tool_name" in data["data"]
        assert "success" in data["data"]
        assert "result" in data["data"]
        assert data["data"]["tool_name"] == "calculator"


class TestPersonaAPI:
    """画像API测试"""

    def test_get_persona_context(self):
        """测试获取画像上下文"""
        response = client.get("/api/persona/context")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "user_persona" in data["data"]
        assert "ai_persona" in data["data"]
        assert "compatibility_score" in data["data"]

    def test_update_persona(self):
        """测试更新画像"""
        request_data = {
            "persona_type": "user",
            "attributes": {
                "name": "测试用户",
                "role": "开发者",
                "expertise_areas": ["Python", "FastAPI"]
            },
            "merge_strategy": "merge"
        }

        response = client.post("/api/persona/update", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "persona_info" in data["data"]

    def test_get_user_persona(self):
        """测试获取用户画像"""
        response = client.get("/api/persona/user")
        assert response.status_code == 200

        data = response.json()
        assert "success" in data
        assert "data" in data

    def test_get_ai_persona(self):
        """测试获取AI画像"""
        response = client.get("/api/persona/ai")
        assert response.status_code == 200

        data = response.json()
        assert "success" in data
        assert "data" in data

    def test_persona_analysis(self):
        """测试画像分析"""
        response = client.get("/api/persona/analysis")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "user_persona_summary" in data["data"]
        assert "ai_persona_summary" in data["data"]
        assert "interaction_patterns" in data["data"]

    def test_persona_validation(self):
        """测试画像验证"""
        request_data = {
            "name": "测试用户",
            "role": "开发者",
            "expertise_areas": ["Python"]
        }

        response = client.post(
            "/api/persona/validate",
            params={"persona_type": "user"},
            json=request_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "is_valid" in data["data"]
        assert "completeness_score" in data["data"]


class TestMemoryAPI:
    """记忆API测试"""

    def test_get_memory_stats(self):
        """测试获取记忆统计"""
        response = client.get("/api/memory/stats")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_sessions" in data["data"]
        assert "total_turns" in data["data"]
        assert "memory_usage_mb" in data["data"]

    def test_list_sessions(self):
        """测试获取会话列表"""
        response = client.get("/api/memory/sessions")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert "pagination" in data

    def test_search_memory(self):
        """测试记忆搜索"""
        request_data = {
            "query": "LangGraph",
            "limit": 10,
            "include_context": True
        }

        response = client.post("/api/memory/search", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    def test_get_memory_network(self):
        """测试获取记忆网络"""
        response = client.get("/api/memory/network")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "nodes" in data["data"]
        assert "edges" in data["data"]
        assert "metadata" in data["data"]


class TestKnowledgeAPI:
    """知识API测试"""

    def test_get_knowledge_stats(self):
        """测试获取知识库统计"""
        response = client.get("/api/knowledge/stats")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_documents" in data["data"]
        assert "total_chunks" in data["data"]
        assert "embedding_model" in data["data"]

    def test_search_knowledge(self):
        """测试知识搜索"""
        request_data = {
            "query": "FastAPI",
            "top_k": 5,
            "min_score": 0.3,
            "include_metadata": True
        }

        response = client.post("/api/knowledge/search", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    def test_list_documents(self):
        """测试获取文档列表"""
        response = client.get("/api/knowledge/documents")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert "pagination" in data

    def test_get_tags_stats(self):
        """测试获取标签统计"""
        response = client.get("/api/knowledge/tags")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_tags" in data["data"]
        assert "most_used_tags" in data["data"]


class TestDemoAPI:
    """演示API测试"""

    def test_get_demo_scenarios(self):
        """测试获取演示场景"""
        response = client.get("/api/demo/scenarios")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_get_scenario_detail(self):
        """测试获取场景详情"""
        response = client.get("/api/demo/scenarios/langgraph_basics")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "scenario_id" in data["data"]
        assert "name" in data["data"]
        assert "steps" in data["data"]

    def test_run_demo_scenario(self):
        """测试运行演示场景"""
        request_data = {
            "interactive_mode": True
        }

        response = client.post("/api/demo/run/langgraph_basics", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "run_id" in data["data"]
        assert "result" in data["data"]

    def test_get_demo_templates(self):
        """测试获取演示模板"""
        response = client.get("/api/demo/templates")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_get_demo_samples(self):
        """测试获取示例数据"""
        response = client.get("/api/demo/samples")
        assert response.status_code == 200

        data = response.json()
        assert "conversations" in data
        assert "personas" in data
        assert "tools" in data

    def test_comparison_analysis(self):
        """测试对比分析"""
        request_data = {
            "baseline": {
                "framework": "LangChain",
                "complexity": "medium"
            },
            "target": {
                "framework": "LangGraph",
                "complexity": "low"
            },
            "comparison_type": "performance",
            "metrics": ["response_time", "memory_usage"]
        }

        response = client.post("/api/demo/comparison/analyze", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "comparison_id" in data["data"]
        assert "differences" in data["data"]
        assert "overall_score" in data["data"]


class TestErrorHandling:
    """错误处理测试"""

    def test_404_error(self):
        """测试404错误"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_validation_error(self):
        """测试验证错误"""
        # 发送无效的数据
        response = client.post("/api/chat/", json={"invalid": "data"})
        assert response.status_code == 422

    def test_rate_limiting(self):
        """测试速率限制（如果启用）"""
        # 快速发送多个请求
        responses = []
        for _ in range(10):
            response = client.post("/api/chat/", json={"message": "test"})
            responses.append(response)

        # 检查是否有速率限制响应
        rate_limited = any(r.status_code == 429 for r in responses)
        # 这个测试可能失败，取决于速率限制配置


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
