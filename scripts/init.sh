#!/bin/bash

echo "🛠️ 初始化项目..."

cd "$(dirname "$0")/.."

# 1. 创建 .env 文件
if [ ! -f .env ]; then
    echo "创建 .env 配置文件..."
    cp .env.example .env
    echo "✅ 请编辑 .env 文件设置模型路径"
fi

# 2. 创建数据目录
echo "创建数据目录..."
mkdir -p data/knowledge
mkdir -p data/vectorstore
mkdir -p logs

# 3. 复制默认知识库（如果存在）
if [ -f ../putian_dialect_template.csv ]; then
    echo "复制默认知识库..."
    cp ../putian_dialect_template.csv data/knowledge/
fi

# 4. 后端依赖
echo ""
echo "安装后端依赖（使用 qwen_rag 环境）..."

# 检查 conda 环境是否存在
if ! conda env list | grep -q "^qwen_rag "; then
    echo "❌ 错误：qwen_rag conda 环境不存在"
    echo "请先创建环境：conda create -n qwen_rag python=3.10"
    exit 1
fi

eval "$(conda shell.bash hook)"
conda activate qwen_rag

echo "当前 Python: $(which python)"
echo "当前环境: $CONDA_DEFAULT_ENV"

cd backend
echo "安装/更新依赖..."
pip install -r requirements.txt --upgrade

# 5. 前端依赖
echo ""
echo "安装前端依赖..."
cd ../frontend

# 使用 nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 18

npm install

echo ""
echo "✅ 初始化完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件配置模型路径"
echo "2. 运行 ./scripts/start_backend.sh 启动后端"
echo "3. 运行 ./scripts/start_frontend.sh 启动前端"
