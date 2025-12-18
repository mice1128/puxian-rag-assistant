#!/bin/bash
# Advanced RAG v2 快速测试脚本

echo "======================================================================"
echo "Advanced RAG v2 - 深度优化版本"
echo "优化点: Query Rewrite + Enhanced Prompt (Few-shot + CoT)"
echo "======================================================================"

# 检查环境
echo -e "\n[1/3] 检查环境..."
if ! conda info --envs | grep -q "qwen_rag"; then
    echo "❌ 错误: qwen_rag 环境不存在"
    exit 1
fi
echo "✓ qwen_rag 环境存在"

# 检查 vLLM 服务
echo -e "\n[2/3] 检查 vLLM 服务..."
if ! curl -s http://127.0.0.1:8001/v1/models > /dev/null 2>&1; then
    echo "❌ 错误: vLLM 服务未启动 (端口 8001)"
    echo "请先启动: bash run_vllm_server.sh"
    exit 1
fi
echo "✓ vLLM 服务运行中"

# 运行测试
echo -e "\n[3/3] 运行 Advanced RAG v2 测试..."
echo "----------------------------------------------------------------------"

conda run -n qwen_rag python test_v2_simple.py

echo -e "\n======================================================================"
echo "测试完成！"
echo "======================================================================"
echo -e "\n下一步:"
echo "1. 对比测试: python test_rag_v1_v2.py"
echo "2. 查看文档: cat OPTIMIZATION_SUMMARY.md"
echo "3. 集成应用: 参考 advanced_rag_v2.py"
