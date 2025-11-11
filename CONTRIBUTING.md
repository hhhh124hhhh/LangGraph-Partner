# 贡献指南

感谢你考虑为LangGraph-Partner项目做出贡献！以下是一些指导原则，帮助你顺利参与到项目中来。

## 行为准则

参与本项目的所有贡献者都应遵循开放友好的社区氛围。我们希望所有贡献者都能互相尊重，共同创造一个包容的环境。

## 报告问题

如果你发现了Bug或者有新功能建议，请在GitHub上提交Issue。提交Issue时，请尽可能详细地描述问题：

- 清晰的标题
- 详细的问题描述
- 重现步骤（如适用）
- 预期行为与实际行为
- 环境信息（操作系统、Python版本等）
- 相关截图或日志（如适用）

## 贡献代码

### 准备工作

1. **Fork** 本项目到你的GitHub账号
2. **克隆** 你的Fork到本地
   ```bash
   git clone https://github.com/YOUR_USERNAME/LangGraph-Partner.git
   cd LangGraph-Partner
   ```
3. **创建** 一个新的功能分支
   ```bash
   git checkout -b feature/amazing-feature
   # 或修复分支
   git checkout -b fix/bug-description
   ```

### 开发流程

1. **安装** 开发依赖
   ```bash
   pip install -r requirements.txt
   ```

2. **编写代码**
   - 遵循项目的代码风格（PEP 8）
   - 添加适当的注释
   - 确保代码可读性

3. **编写测试**（如适用）
   - 为新功能添加单元测试
   - 确保现有测试通过

4. **运行测试**
   ```bash
   python -m pytest
   ```

5. **提交更改**
   - 使用清晰简洁的提交信息
   - 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 格式
   ```bash
   git commit -m "feat: 添加新功能描述"
   # 或修复
   git commit -m "fix: 修复问题描述"
   ```

6. **推送到远程分支**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **创建 Pull Request**
   - 从你的Fork创建一个Pull Request到主项目
   - 在PR描述中详细说明更改内容和目的
   - 引用相关的Issue（如适用）

## 代码审查流程

1. 提交PR后，项目维护者将审查你的代码
2. 可能会有一些修改建议，请积极回应
3. 一旦PR被批准，项目维护者将合并你的代码

## 开发规范

### 代码风格

- 遵循 PEP 8 规范
- 保持代码简洁、可读
- 使用类型提示（Type Hints）增强代码可读性

### 文档规范

- 为新功能和API添加文档
- 更新README.md（如需要）
- 确保文档清晰易懂

### 测试规范

- 为新功能编写测试用例
- 确保测试覆盖主要功能点
- 避免测试中的硬编码和依赖外部服务

## 版本控制

项目使用语义化版本控制（Semantic Versioning）：
- MAJOR.MINOR.PATCH
  - MAJOR：不兼容的API更改
  - MINOR：向后兼容的功能性新增
  - PATCH：向后兼容的问题修复

## 获取帮助

如果你在贡献过程中有任何问题，可以通过以下方式获取帮助：
- 在GitHub上提出问题
- 联系项目维护者

感谢你的贡献！