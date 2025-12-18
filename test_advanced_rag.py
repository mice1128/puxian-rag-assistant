"""
Advanced RAG 测试脚本
混合检索 (Vector + BM25) + BGE Reranker
"""
import sys
sys.path.insert(0, '/home/zl/LLM/puxian-rag-assistant')

def main():
    print("=" * 80)
    print("🚀 Advanced RAG 测试")
    print("=" * 80)
    print("\n特性:")
    print("  ✓ 混合检索: Vector Search + BM25")
    print("  ✓ RRF 融合算法")
    print("  ✓ BGE Reranker 重排序")
    print("=" * 80)
    
    # 初始化
    print("\n[初始化] 加载 Advanced RAG...")
    from advanced_rag import AdvancedRAG
    rag = AdvancedRAG()
    
    # 测试查询
    test_queries = [
        "莆田话中'吃'怎么说？",
        "食的发音是什么？",
        "介绍一下莆田话的声调",
    ]
    
    print("\n" + "=" * 80)
    print("开始测试")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*80}")
        print(f"查询 {i}/{len(test_queries)}: {query}")
        print(f"{'='*80}")
        
        result = rag.generate(
            query=query,
            retrieval_top_k=20,  # 混合检索召回 20 条
            final_top_k=3,       # 重排序后保留 3 条
            verbose=True
        )
        
        # 显示统计
        print(f"\n📊 统计:")
        print(f"  - 检索文档数: {result['num_docs']}")
        print(f"  - 答案长度: {len(result['answer'])} 字符")
        
        if i < len(test_queries):
            input("\n按回车继续下一个查询...")
    
    print("\n\n" + "="*80)
    print("✅ 测试完成！")
    print("="*80)

if __name__ == "__main__":
    main()
