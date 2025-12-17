#!/usr/bin/env python3
"""
测试 RAG 问答
命令行交互式问答
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from app.services.rag_service import get_rag_service
import torch

def main():
    print("=" * 60)
    print("💬 莆仙话 RAG 问答测试")
    print("=" * 60)
    
    # 检查设备
    print(f"\n设备信息:")
    print(f"  CUDA 可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU 名称: {torch.cuda.get_device_name(0)}")
    
    # 初始化 RAG 服务
    print("\n初始化 RAG 服务...")
    rag = get_rag_service()
    
    # 显示知识库信息
    metrics = rag.get_metrics()
    print(f"  知识库文档数: {metrics['total_documents']}")
    print(f"  向量库路径: {metrics['vectorstore_path']}")
    
    if metrics['total_documents'] == 0:
        print("\n⚠️  知识库为空！")
        print("请先导入知识库：")
        print("  python tests/test_knowledge.py import --file data/knowledge/putian_dialect.csv")
        return
    
    print("\n✅ RAG 服务就绪！")
    print("\n说明：")
    print("  - 输入问题进行 RAG 问答")
    print("  - 输入 'exit' 或 'quit' 退出")
    print("  - 首次问答会加载模型，请耐心等待")
    
    print("\n" + "=" * 60)
    print("开始问答")
    print("=" * 60)
    
    while True:
        try:
            # 获取用户输入
            question = input("\n问题: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n再见！")
                break
            
            # RAG 问答
            print("\n正在思考...\n")
            result = rag.ask(question)
            
            # 显示回答
            print("回答:")
            print("-" * 60)
            print(result['answer'])
            print("-" * 60)
            
            # 显示参考来源
            if result['sources']:
                print(f"\n📚 参考来源 ({len(result['sources'])} 条):")
                for i, source in enumerate(result['sources'], 1):
                    print(f"\n  [{i}] {source['text'][:150]}...")
                    if source['metadata']:
                        print(f"      元数据: {source['metadata']}")
            
            print(f"\n💡 使用 Token: {result['tokens_used']}")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
