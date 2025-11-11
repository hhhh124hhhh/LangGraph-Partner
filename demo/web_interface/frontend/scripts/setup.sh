#!/bin/bash

# AI Partner Frontend Setup Script
echo "🚀 Setting up AI Partner Frontend..."

# 检查Node.js是否已安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# 检查Node.js版本
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# 检查包管理器
if command -v pnpm &> /dev/null; then
    PACKAGE_MANAGER="pnpm"
    echo "✅ Using pnpm"
elif command -v yarn &> /dev/null; then
    PACKAGE_MANAGER="yarn"
    echo "✅ Using yarn"
elif command -v npm &> /dev/null; then
    PACKAGE_MANAGER="npm"
    echo "✅ Using npm"
else
    echo "❌ No package manager found. Please install npm, yarn, or pnpm."
    exit 1
fi

# 安装依赖
echo "📦 Installing dependencies..."
$PACKAGE_MANAGER install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# 创建环境配置文件
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your configuration"
fi

# 检查TypeScript编译
echo "🔍 Checking TypeScript compilation..."
$PACKAGE_MANAGER run type-check

if [ $? -ne 0 ]; then
    echo "❌ TypeScript compilation failed"
    exit 1
fi

# 运行代码检查
echo "🔍 Running code linting..."
$PACKAGE_MANAGER run lint

if [ $? -ne 0 ]; then
    echo "⚠️  Linting found issues, but setup continues"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Update .env file with your configuration"
echo "   2. Start the development server: $PACKAGE_MANAGER run dev"
echo "   3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For more information, see README.md"