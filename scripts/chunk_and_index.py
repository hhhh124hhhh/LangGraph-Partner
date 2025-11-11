"""
智能笔记分块和索引脚本
基于 AI Agent 方法，动态分析笔记格式并生成最优分块策略
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import re

# 添加 AI partner chat 脚本路径
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "ai-partner-chat" / "scripts"))

from chunk_schema import Chunk, validate_chunk
from vector_indexer import VectorIndexer


class IntelligentNoteChunker:
    """智能笔记分块器"""

    def __init__(self):
        """初始化分块器"""
        self.chunk_strategies = {
            'date_entry': self._chunk_date_entry,
            'section_based': self._chunk_section_based,
            'paragraph_based': self._chunk_paragraph_based,
            'mixed_content': self._chunk_mixed_content
        }

    def analyze_note_format(self, content: str) -> str:
        """
        分析笔记格式，确定最适合的分块策略

        Args:
            content: 笔记内容

        Returns:
            分块策略类型
        """
        lines = content.split('\n')

        # 检测日期条目格式（如：2024-01-01, ## 2024年1月1日）
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}|^\d{4}年\d{1,2}月\d{1,2}日|^##\s*\d{4}')
        date_lines = sum(1 for line in lines if date_pattern.match(line.strip()))

        if date_lines > 1:
            return 'date_entry'

        # 检测章节标题格式（如：#, ##, ###）
        header_pattern = re.compile(r'^#+\s+')
        header_lines = sum(1 for line in lines if header_pattern.match(line.strip()))

        # 检测列表项格式
        list_pattern = re.compile(r'^\s*[-*+]\s+|^\s*\d+\.\s+')
        list_lines = sum(1 for line in lines if list_pattern.match(line.strip()))

        if header_lines > 2:
            return 'section_based'
        elif list_lines > len(lines) * 0.3:
            return 'mixed_content'
        else:
            return 'paragraph_based'

    def _chunk_date_entry(self, content: str, filepath: str) -> List[Chunk]:
        """按日期条目分块"""
        chunks = []
        lines = content.split('\n')
        current_chunk_lines = []
        chunk_id = 0

        # 日期模式
        date_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2}|\d{4}年\d{1,2}月\d{1,2}日|##\s*\d{4})')

        for line in lines:
            # 检测新的日期条目
            if date_pattern.match(line.strip()) and current_chunk_lines:
                # 保存当前块
                chunk_content = '\n'.join(current_chunk_lines).strip()
                if chunk_content:
                    chunks.append(self._create_chunk(
                        chunk_content, filepath, chunk_id, 'date_entry'
                    ))
                    chunk_id += 1
                current_chunk_lines = [line]
            else:
                current_chunk_lines.append(line)

        # 处理最后一个块
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines).strip()
            if chunk_content:
                chunks.append(self._create_chunk(
                    chunk_content, filepath, chunk_id, 'date_entry'
                ))

        return chunks

    def _chunk_section_based(self, content: str, filepath: str) -> List[Chunk]:
        """基于章节标题分块"""
        chunks = []
        lines = content.split('\n')
        current_chunk_lines = []
        chunk_id = 0
        current_title = ""

        # 章节标题模式
        header_pattern = re.compile(r'^(#+)\s+(.+)')

        for line in lines:
            header_match = header_pattern.match(line.strip())

            if header_match and current_chunk_lines:
                # 保存当前章节
                chunk_content = '\n'.join(current_chunk_lines).strip()
                if chunk_content:
                    chunks.append(self._create_chunk(
                        chunk_content, filepath, chunk_id, 'section',
                        title=current_title
                    ))
                    chunk_id += 1

                current_chunk_lines = [line]
                current_title = header_match.group(2).strip()
            else:
                current_chunk_lines.append(line)

        # 处理最后一个章节
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines).strip()
            if chunk_content:
                chunks.append(self._create_chunk(
                    chunk_content, filepath, chunk_id, 'section',
                    title=current_title
                ))

        return chunks

    def _chunk_paragraph_based(self, content: str, filepath: str) -> List[Chunk]:
        """基于段落分块"""
        chunks = []
        paragraphs = content.split('\n\n')
        chunk_id = 0

        current_chunk_paragraphs = []
        current_length = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # 如果当前块太长，创建新块
            if current_length + len(paragraph) > 800 and current_chunk_paragraphs:
                chunk_content = '\n\n'.join(current_chunk_paragraphs)
                chunks.append(self._create_chunk(
                    chunk_content, filepath, chunk_id, 'paragraph'
                ))
                chunk_id += 1

                current_chunk_paragraphs = [paragraph]
                current_length = len(paragraph)
            else:
                current_chunk_paragraphs.append(paragraph)
                current_length += len(paragraph)

        # 处理最后一个块
        if current_chunk_paragraphs:
            chunk_content = '\n\n'.join(current_chunk_paragraphs)
            chunks.append(self._create_chunk(
                chunk_content, filepath, chunk_id, 'paragraph'
            ))

        return chunks

    def _chunk_mixed_content(self, content: str, filepath: str) -> List[Chunk]:
        """混合内容分块（处理包含列表、标题等的复杂内容）"""
        chunks = []
        lines = content.split('\n')
        current_chunk_lines = []
        chunk_id = 0
        current_title = ""

        # 标题和列表模式
        header_pattern = re.compile(r'^(#+)\s+(.+)')
        list_pattern = re.compile(r'^\s*[-*+]\s+|^\s*\d+\.\s+')

        for i, line in enumerate(lines):
            line = line.strip()

            # 检测标题
            header_match = header_pattern.match(line)
            if header_match:
                # 如果有内容 accumulated，先保存
                if current_chunk_lines:
                    chunk_content = '\n'.join(current_chunk_lines).strip()
                    if chunk_content:
                        chunks.append(self._create_chunk(
                            chunk_content, filepath, chunk_id, 'mixed_content',
                            title=current_title
                        ))
                        chunk_id += 1

                current_chunk_lines = [line]
                current_title = header_match.group(2).strip()
            # 空行且当前块有内容时，可能是一个新部分的开始
            elif not line and current_chunk_lines and len(current_chunk_lines) > 3:
                # 检查下一行是否是标题或列表
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if (header_pattern.match(next_line) or
                        list_pattern.match(next_line)):
                        # 保存当前块
                        chunk_content = '\n'.join(current_chunk_lines).strip()
                        if chunk_content:
                            chunks.append(self._create_chunk(
                                chunk_content, filepath, chunk_id, 'mixed_content',
                                title=current_title
                            ))
                            chunk_id += 1
                        current_chunk_lines = []
                        current_title = ""
                        continue

            # 检查当前块是否太长
            if len('\n'.join(current_chunk_lines + [line])) > 1000:
                chunk_content = '\n'.join(current_chunk_lines).strip()
                if chunk_content:
                    chunks.append(self._create_chunk(
                        chunk_content, filepath, chunk_id, 'mixed_content',
                        title=current_title
                    ))
                    chunk_id += 1
                current_chunk_lines = [line] if line else []
            else:
                current_chunk_lines.append(line)

        # 处理最后一个块
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines).strip()
            if chunk_content:
                chunks.append(self._create_chunk(
                    chunk_content, filepath, chunk_id, 'mixed_content',
                    title=current_title
                ))

        return chunks

    def _create_chunk(
        self,
        content: str,
        filepath: str,
        chunk_id: int,
        chunk_type: str,
        title: str = None,
        date: str = None
    ) -> Chunk:
        """创建标准格式的文档块"""
        # 提取日期信息
        if not date:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{4}年\d{1,2}月\d{1,2}日)', content)
            date = date_match.group(1) if date_match else None

        metadata = {
            'filename': Path(filepath).name,
            'filepath': filepath,
            'chunk_id': chunk_id,
            'chunk_type': chunk_type,
            'title': title,
            'date': date
        }

        chunk = {
            'content': content,
            'metadata': metadata
        }

        # 验证块格式
        if not validate_chunk(chunk):
            print(f"警告：生成的块格式不正确: {metadata}")

        return chunk

    def chunk_note_file(self, filepath: str) -> List[Chunk]:
        """
        分析并分块指定的笔记文件

        Args:
            filepath: 笔记文件路径

        Returns:
            分块后的文档列表
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                print(f"警告：文件 {filepath} 为空")
                return []

            print(f"📖 分析文件: {filepath}")

            # 分析格式并选择分块策略
            strategy = self.analyze_note_format(content)
            print(f"📋 选择分块策略: {strategy}")

            # 执行分块
            chunker_func = self.chunk_strategies.get(strategy, self._chunk_paragraph_based)
            chunks = chunker_func(content, filepath)

            print(f"✅ 生成了 {len(chunks)} 个块")
            return chunks

        except Exception as e:
            print(f"❌ 分块文件 {filepath} 失败: {e}")
            return []


def main():
    """主函数：分块并索引所有笔记"""
    print("🚀 开始智能笔记分块和索引...")

    # 初始化
    chunker = IntelligentNoteChunker()
    indexer = VectorIndexer(db_path="./vector_db")
    indexer.initialize_db()

    # 查找所有笔记文件
    notes_dir = Path("./notes")
    if not notes_dir.exists():
        print("❌ 笔记目录不存在，请先创建 ./notes 目录并添加 markdown 文件")
        return

    # 获取所有 markdown 文件
    note_files = list(notes_dir.glob("**/*.md"))
    if not note_files:
        print("❌ 未找到 markdown 文件，请在 ./notes 目录中添加 .md 文件")
        return

    print(f"📁 找到 {len(note_files)} 个笔记文件")

    # 处理所有文件
    all_chunks = []
    for note_file in note_files:
        chunks = chunker.chunk_note_file(str(note_file))
        all_chunks.extend(chunks)

    if not all_chunks:
        print("❌ 没有生成任何有效的块")
        return

    print(f"📦 总共生成了 {len(all_chunks)} 个块")

    # 索引块
    print("🔍 开始向量索引...")
    try:
        indexer.index_chunks(all_chunks)
        print("✅ 索引完成！")
    except Exception as e:
        print(f"❌ 索引失败: {e}")
        return

    # 显示统计信息
    try:
        stats = indexer.get_stats()
        print(f"\n📊 数据库统计:")
        print(f"   总块数: {stats['total_chunks']}")
        print(f"   集合名: {stats['collection_name']}")
        print(f"   数据库路径: {stats['db_path']}")
    except Exception as e:
        print(f"⚠️ 无法获取统计信息: {e}")

    print("\n🎉 笔记分块和索引完成！")
    print("现在可以使用 AI Partner Chat 进行个性化对话了。")


if __name__ == "__main__":
    main()