#!/bin/bash

echo "🚀 启动后端服务..."

cd "$(dirname "$0")/.."

# 激活 conda 环境
eval "$(conda shell.bash hook)"

# 检查环境是否存在
if ! conda env list | grep -q "^qwen_rag "; then
    echo "❌ 错误：qwen_rag conda 环境不存在"
    echo "请先运行：./scripts/init.sh"
    exit 1
fi

conda activate qwen_rag

if [ $? -ne 0 ]; then
    echo "❌ 激活 conda 环境失败"
    exit 1
fi

echo "✅ 已激活环境: $CONDA_DEFAULT_ENV"
echo "Python: $(which python)"
echo "Torch: $(python -c 'import torch; print(torch.__version__)' 2>/dev/null || echo '未安装')"
echo "CUDA: $(python -c 'import torch; print(torch.cuda.is_available())' 2>/dev/null || echo '未知')"

# 进入后端目录
cd backend

# 检查依赖
echo "检查依赖..."
pip list | grep -q "flask" || {
    echo "安装依赖..."
    pip install -r requirements.txt
}

# 创建 .env 文件（如果不存在）
if [ ! -f ../.env ]; then
    echo "创建 .env 配置文件..."
    cp ../.env.example ../.env
fi

# 启动服务
echo "✅ 启动 Flask 服务器..."
python run.py
