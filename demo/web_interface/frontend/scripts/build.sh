#!/bin/bash

# AI Partner Frontend Build Script
echo "🏗️  Building AI Partner Frontend..."

# 检查Node.js是否已安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

# 检查包管理器
if command -v pnpm &> /dev/null; then
    PACKAGE_MANAGER="pnpm"
elif command -v yarn &> /dev/null; then
    PACKAGE_MANAGER="yarn"
elif command -v npm &> /dev/null; then
    PACKAGE_MANAGER="npm"
else
    echo "❌ No package manager found"
    exit 1
fi

# 确保依赖已安装
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    $PACKAGE_MANAGER install
fi

# 清理之前的构建
echo "🧹 Cleaning previous build..."
rm -rf dist

# TypeScript类型检查
echo "🔍 Running TypeScript type check..."
$PACKAGE_MANAGER run type-check

if [ $? -ne 0 ]; then
    echo "❌ TypeScript type check failed"
    exit 1
fi

# 代码检查
echo "🔍 Running linting..."
$PACKAGE_MANAGER run lint

if [ $? -ne 0 ]; then
    echo "⚠️  Linting issues found. Consider fixing them before build."
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 构建应用
echo "🏗️  Building application..."
$PACKAGE_MANAGER run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# 检查构建结果
if [ ! -d "dist" ]; then
    echo "❌ Build directory not found"
    exit 1
fi

# 显示构建统计
echo "📊 Build statistics:"
echo "   Build directory size: $(du -sh dist | cut -f1)"
echo "   Files created: $(find dist -type f | wc -l)"

# 检查关键文件
CRITICAL_FILES=("index.html" "assets/")
for file in "${CRITICAL_FILES[@]}"; do
    if [ ! -e "dist/$file" ]; then
        echo "⚠️  Critical file missing: $file"
    fi
done

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "📂 Build output: ./dist"
echo "🌐 To preview: $PACKAGE_MANAGER run preview"
echo "🚀 To deploy: Copy ./dist to your web server"