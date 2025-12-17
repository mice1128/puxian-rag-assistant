#!/usr/bin/env python3
"""
测试 Qwen 模型对话
直接命令行交互测试
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from app.services.qwen_service import get_qwen_service
import torch

def main():
    print("=" * 60)
    print("🤖 Qwen 模型对话测试")
    print("=" * 60)
    
    # 检查 CUDA
    print(f"\n设备信息:")
    print(f"  CUDA 可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU 数量: {torch.cuda.device_count()}")
        print(f"  当前 GPU: {torch.cuda.current_device()}")
        print(f"  GPU 名称: {torch.cuda.get_device_name(0)}")
    
    # 初始化服务
    print("\n初始化 Qwen 服务...")
    qwen = get_qwen_service()
    print(f"  模型路径: {qwen.model_path}")
    print(f"  设备: {qwen.device}")
    
    # 加载模型
    print("\n加载模型（首次较慢，请稍候）...")
    qwen.load_model()
    print("✅ 模型加载完成！\n")
    
    print("=" * 60)
    print("开始对话（输入 'exit' 或 'quit' 退出）")
    print("=" * 60)
    
    while True:
        try:
            # 获取用户输入
            question = input("\n你: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n再见！")
                break
            
            # 生成回答
            print("\n助手: ", end="", flush=True)
            
            response, tokens = qwen.generate(
                question,
                max_new_tokens=512,
                temperature=0.7
            )
            
            print(response)
            print(f"\n[Token 数: {tokens}]")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")

if __name__ == "__main__":
    main()
