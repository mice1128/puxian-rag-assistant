#!/bin/bash

echo "🚀 启动前端服务..."

cd "$(dirname "$0")/../frontend"

# 使用 nvm 切换到 Node.js 18
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

nvm use 18

if [ $? -ne 0 ]; then
    echo "❌ 切换到 Node.js 18 失败"
    echo "请确保已安装 nvm 和 Node.js 18"
    exit 1
fi

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
fi

# 启动开发服务器
echo "✅ 启动 Vite 开发服务器..."
npm run dev
