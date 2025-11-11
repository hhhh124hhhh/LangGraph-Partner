"""
画像管理系统
管理用户和 AI 的交互画像，提供个性化对话基础
"""

import os
from pathlib import Path
from typing import Dict, Optional, List
import markdown
from dataclasses import dataclass


@dataclass
class PersonaInfo:
    """画像信息数据类"""
    name: str = ""
    role: str = ""
    background: str = ""
    communication_style: str = ""
    expertise_areas: List[str] = None
    interests: List[str] = None
    working_style: str = ""
    custom_attributes: Dict = None

    def __post_init__(self):
        if self.expertise_areas is None:
            self.expertise_areas = []
        if self.interests is None:
            self.interests = []
        if self.custom_attributes is None:
            self.custom_attributes = {}


class PersonaManager:
    """画像管理器"""

    def __init__(self, config_dir: str = "./config"):
        """
        初始化画像管理器

        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.user_persona_file = self.config_dir / "user-persona.md"
        self.ai_persona_file = self.config_dir / "ai-persona.md"

        # 缓存加载的画像
        self._user_persona = None
        self._ai_persona = None

    def _parse_markdown_persona(self, file_path: Path) -> PersonaInfo:
        """
        解析 Markdown 格式的画像文件

        Args:
            file_path: 画像文件路径

        Returns:
            解析后的画像信息
        """
        if not file_path.exists():
            return PersonaInfo()

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析 Markdown 内容
        html = markdown.markdown(content)

        # 简单的文本解析（更复杂的解析可以使用专门的 markdown 解析库）
        persona = PersonaInfo()
        lines = content.split('\n')
        current_section = ""

        for line in lines:
            line = line.strip()

            # 识别章节标题
            if line.startswith('# '):
                current_section = line[2:].lower()
            elif line.startswith('- **') and ':' in line:
                # 解析键值对
                key_value = line[4:].split(':', 1)
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value = key_value[1].strip().strip('[]')

                    # 根据章节和键名设置属性
                    if current_section == "basic information":
                        if key.lower() == "name":
                            persona.name = value
                        elif key.lower() == "role":
                            persona.role = value
                        elif key.lower() == "background":
                            persona.background = value

                    elif current_section == "communication preferences":
                        if "language style" in key.lower():
                            persona.communication_style = value

                    elif current_section == "working style":
                        if "problem-solving approach" in key.lower():
                            persona.working_style = value

            elif line.startswith('  - ') and current_section:
                # 解析列表项
                item = line[4:].strip()
                if "interests" in current_section.lower() or "expertise" in current_section.lower():
                    if item and persona.interests is not None:
                        persona.interests.append(item)
                    elif item and persona.expertise_areas is not None:
                        persona.expertise_areas.append(item)

        return persona

    def get_user_persona(self, force_reload: bool = False) -> PersonaInfo:
        """
        获取用户画像

        Args:
            force_reload: 是否强制重新加载

        Returns:
            用户画像信息
        """
        if self._user_persona is None or force_reload:
            self._user_persona = self._parse_markdown_persona(self.user_persona_file)

        return self._user_persona

    def get_ai_persona(self, force_reload: bool = False) -> PersonaInfo:
        """
        获取 AI 画像

        Args:
            force_reload: 是否强制重新加载

        Returns:
            AI 画像信息
        """
        if self._ai_persona is None or force_reload:
            self._ai_persona = self._parse_markdown_persona(self.ai_persona_file)

        return self._ai_persona

    def get_persona_context(self) -> str:
        """
        获取用于对话的画像上下文

        Returns:
            格式化的画像上下文字符串
        """
        user_persona = self.get_user_persona()
        ai_persona = self.get_ai_persona()

        context_parts = []

        # 用户画像部分
        if user_persona.name or user_persona.role or user_persona.background:
            user_context = []
            if user_persona.name:
                user_context.append(f"用户姓名: {user_persona.name}")
            if user_persona.role:
                user_context.append(f"职业角色: {user_persona.role}")
            if user_persona.background:
                user_context.append(f"背景: {user_persona.background}")
            if user_persona.communication_style:
                user_context.append(f"沟通风格: {user_persona.communication_style}")

            if user_context:
                context_parts.append("## 用户画像\n" + "\n".join(user_context))

        # AI 画像部分
        if ai_persona.role or ai_persona.communication_style:
            ai_context = []
            if ai_persona.role:
                ai_context.append(f"AI 角色: {ai_persona.role}")
            if ai_persona.communication_style:
                ai_context.append(f"回应风格: {ai_persona.communication_style}")

            if ai_context:
                context_parts.append("## AI 画像\n" + "\n".join(ai_context))

        # 专长领域
        all_expertise = list(set(user_persona.expertise_areas + ai_persona.expertise_areas))
        if all_expertise:
            context_parts.append("## 专长领域\n" + ", ".join(all_expertise))

        # 兴趣领域
        if user_persona.interests:
            context_parts.append("## 用户兴趣\n" + ", ".join(user_persona.interests))

        return "\n\n".join(context_parts) if context_parts else "暂无画像信息"

    def update_user_attribute(self, key: str, value: str) -> bool:
        """
        更新用户画像属性

        Args:
            key: 属性键
            value: 属性值

        Returns:
            是否更新成功
        """
        try:
            user_persona = self.get_user_persona()
            if hasattr(user_persona, key):
                setattr(user_persona, key, value)
                self._user_persona = user_persona
                return True
            else:
                user_persona.custom_attributes[key] = value
                return True
        except Exception as e:
            print(f"更新用户画像失败: {e}")
            return False

    def update_ai_attribute(self, key: str, value: str) -> bool:
        """
        更新 AI 画像属性

        Args:
            key: 属性键
            value: 属性值

        Returns:
            是否更新成功
        """
        try:
            ai_persona = self.get_ai_persona()
            if hasattr(ai_persona, key):
                setattr(ai_persona, key, value)
                self._ai_persona = ai_persona
                return True
            else:
                ai_persona.custom_attributes[key] = value
                return True
        except Exception as e:
            print(f"更新 AI 画像失败: {e}")
            return False

    def reload_personas(self) -> bool:
        """
        重新加载所有画像文件

        Returns:
            是否重新加载成功
        """
        try:
            self._user_persona = None
            self._ai_persona = None
            return True
        except Exception as e:
            print(f"重新加载画像失败: {e}")
            return False

    def validate_persona_files(self) -> Dict[str, bool]:
        """
        验证画像文件是否存在

        Returns:
            验证结果字典
        """
        return {
            'user_persona_exists': self.user_persona_file.exists(),
            'ai_persona_exists': self.ai_persona_file.exists(),
            'config_dir_exists': self.config_dir.exists()
        }


# 全局画像管理器实例
_persona_manager = None


def get_persona_manager(config_dir: str = "./config") -> PersonaManager:
    """
    获取全局画像管理器实例

    Args:
        config_dir: 配置目录路径

    Returns:
        PersonaManager 实例
    """
    global _persona_manager
    if _persona_manager is None:
        _persona_manager = PersonaManager(config_dir)
    return _persona_manager


def get_persona_context(config_dir: str = "./config") -> str:
    """
    便捷函数：获取画像上下文

    Args:
        config_dir: 配置目录路径

    Returns:
        格式化的画像上下文
    """
    manager = get_persona_manager(config_dir)
    return manager.get_persona_context()