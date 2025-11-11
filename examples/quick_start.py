"""
AI Partner Chat 快速启动指南
一键启动完整的 AI Partner 系统
"""

import asyncio
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
print("📄 加载环境变量...")
load_dotenv(os.path.join(project_root, '.env'))
load_dotenv(os.path.join(project_root, '.env.local'))

print(f"环境变量加载状态:")
print(f"ZHIPU_API_KEY: {'已设置' if os.getenv('ZHIPU_API_KEY') else '未设置'}")

def check_environment():
    """检查环境配置"""
    print("🔧 环境检查")
    print("-" * 30)

    # 检查 API 密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if api_key:
        print("✅ ZHIPU_API_KEY 已设置")
    else:
        print("❌ ZHIPU_API_KEY 未设置")
        print("请设置环境变量: export ZHIPU_API_KEY=your_api_key")
        return False

    # 检查 Python 包
    required_packages = [
        "langgraph", "langchain", "langchain_openai",
        "chromadb", "sentence_transformers", "numpy"
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n请安装缺失的包: pip install {' '.join(missing_packages)}")
        return False

    return True


async def setup_initial_data():
    """设置初始数据"""
    print("\n📦 初始数据设置")
    print("-" * 30)

    # 检查目录结构
    required_dirs = ["config", "notes", "vector_db", "memory"]
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"📁 创建 {dir_name}/ 目录")
            dir_path.mkdir(exist_ok=True)

    # 检查配置文件
    config_files = ["config/user-persona.md", "config/ai-persona.md"]
    for config_file in config_files:
        file_path = Path(config_file)
        if file_path.exists():
            print(f"✅ {config_file} 存在")
        else:
            print(f"❌ {config_file} 不存在")
            return False

    # 检查笔记文件
    notes_dir = Path("notes")
    note_files = list(notes_dir.glob("*.md")) if notes_dir.exists() else []

    if note_files:
        print(f"✅ 找到 {len(note_files)} 个笔记文件")
        for note_file in note_files[:3]:  # 显示前3个
            print(f"   📄 {note_file.name}")
        if len(note_files) > 3:
            print(f"   ... 还有 {len(note_files) - 3} 个文件")
    else:
        print("⚠️  没有找到笔记文件")
        print("提示: 在 notes/ 目录中添加 .md 文件以启用知识检索功能")

    return True


async def initialize_vector_store():
    """初始化向量存储"""
    print("\n🔍 向量存储初始化")
    print("-" * 30)

    try:
        from utils.vector_store import VectorStore

        # 尝试连接向量存储
        vector_store = VectorStore()
        stats = vector_store.get_stats()

        if stats['total_chunks'] > 0:
            print(f"✅ 向量存储已就绪，包含 {stats['total_chunks']} 个文档块")
            return True
        else:
            print("📦 向量存储为空，开始索引笔记...")

            # 运行分块和索引
            try:
                from scripts.chunk_and_index import main as index_main
                index_main()
                print("✅ 笔记索引完成")
                return True
            except Exception as e:
                print(f"❌ 索引失败: {e}")
                return False

    except Exception as e:
        print(f"❌ 向量存储初始化失败: {e}")
        return False


async def test_ai_partner():
    """测试 AI Partner 功能"""
    print("\n🤖 AI Partner 功能测试")
    print("-" * 30)

    try:
        from agents.partner_agent import create_partner_agent

        print("🔧 创建 AI Partner 智能体...")
        agent = await create_partner_agent()

        print("✅ 智能体创建成功")

        # 获取会话信息
        session_info = agent.get_session_info()
        print(f"📊 会话ID: {session_info['session_id'][:8]}...")
        print(f"📊 画像文件: {session_info['persona_validation']}")

        # 测试简单对话
        print("\n💬 测试对话功能...")
        test_message = "你好！请简单介绍一下你的功能。"

        response = await agent.chat(test_message)
        print(f"👤 用户: {test_message}")
        print(f"🤖 AI: {response[:100]}{'...' if len(response) > 100 else ''}")

        # 关闭智能体
        await agent.close()
        print("✅ 功能测试通过")
        return True

    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_next_steps():
    """显示后续步骤"""
    print("\n🎯 后续步骤")
    print("-" * 30)

    print("1. 📝 添加你的笔记:")
    print("   在 notes/ 目录中添加 .md 文件，内容会被自动索引")

    print("\n2. 🎨 自定义画像:")
    print("   编辑 config/user-persona.md 和 config/ai-persona.md 来自定义交互体验")

    print("\n3. 🚀 运行完整演示:")
    print("   python examples/partner_chat_demo.py     # 完整功能演示")
    print("   python examples/memory_demo.py           # 记忆功能演示")
    print("   python examples/multi_session_demo.py    # 多会话演示")

    print("\n4. 🔧 集成到你的应用:")
    print("   参考 examples/ 目录中的示例代码")
    print("   查看 agents/partner_agent.py 了解核心实现")

    print("\n5. 📚 深入学习:")
    print("   阅读 utils/ 目录了解各组件实现")
    print("   查看 .claude/ai-partner-chat/SKILL.md 了解技术原理")


async def main():
    """主函数"""
    print("🚀 AI Partner Chat 快速启动")
    print("=" * 50)

    # 1. 环境检查
    if not check_environment():
        print("\n❌ 环境检查失败，请解决上述问题后重试")
        return

    # 2. 初始数据设置
    if not await setup_initial_data():
        print("\n❌ 初始数据设置失败，请检查配置文件")
        return

    # 3. 向量存储初始化
    if not await initialize_vector_store():
        print("\n❌ 向量存储初始化失败")
        return

    # 4. 功能测试
    if not await test_ai_partner():
        print("\n❌ 功能测试失败")
        return

    # 成功
    print("\n🎉 AI Partner Chat 系统启动成功！")
    print("✅ 所有组件都已就绪，可以开始使用了")

    # 显示后续步骤
    show_next_steps()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 用户取消，启动中断")
    except Exception as e:
        print(f"\n❌ 启动过程中出现未预期的错误: {e}")
        import traceback
        traceback.print_exc()