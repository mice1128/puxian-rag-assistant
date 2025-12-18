#!/bin/bash

MODEL_PATH="/home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4"
HOST="127.0.0.1"
PORT="8001"
GPU_ID="1"
GPU_MEMORY_UTILIZATION=0.9

echo "========================================"
echo "Starting vLLM OpenAI-Compatible API Server"
echo "========================================"
echo "Model: $MODEL_PATH"
echo "Host: $HOST"
echo "Port: $PORT"
echo "GPU: $GPU_ID"
echo "========================================"
echo ""
echo "重要提示："
echo "1. 请确保您已激活 vllm_env 环境: conda activate vllm_env"
echo "2. 服务启动后，可通过 http://${HOST}:${PORT}/v1/models 测试"
echo "3. 使用 Ctrl+C 停止服务"
echo ""

# 使用 CUDA_VISIBLE_DEVICES 指定 GPU
export CUDA_VISIBLE_DEVICES=$GPU_ID

python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_PATH" \
    --host "$HOST" \
    --port "$PORT" \
    --gpu-memory-utilization $GPU_MEMORY_UTILIZATION \
    --trust-remote-code
