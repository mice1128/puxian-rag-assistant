"""
测试 Advanced RAG vs Naive RAG
"""
import sys
sys.path.insert(0, '/home/zl/LLM/puxian-rag-assistant')

def main():
    print("=" * 80)
    print("Advanced RAG vs Naive RAG 对比测试")
    print("=" * 80)

    # 测试查询
    test_queries = [
        "莆田话中'吃'怎么说？",
        "食",
    ]

    print("\n[准备] 初始化 Naive RAG...")
    from naive_rag import NaiveRAG
    naive_rag = NaiveRAG()

    print("\n[准备] 初始化 Advanced RAG...")
    from advanced_rag import AdvancedRAG
    advanced_rag = AdvancedRAG()

    print("\n" + "=" * 80)
    print("开始对比测试")
    print("=" * 80)

    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'#'*80}")
        print(f"测试 {i}/{len(test_queries)}: {query}")
        print(f"{'#'*80}")
        
        # Naive RAG
        print("\n" + "─"*80)
        print("🔵 Naive RAG (纯向量检索)")
        print("─"*80)
        naive_result = naive_rag.generate(query, top_k=3, verbose=True)
        
        # Advanced RAG  
        print("\n" + "─"*80)
        print("🟢 Advanced RAG (混合检索 + 重排序)")
        print("─"*80)
        advanced_result = advanced_rag.generate(
            query, 
            retrieval_top_k=10,  # 混合检索取 10 条
            final_top_k=3,       # 重排序后保留 3 条
            verbose=True
        )
        
        # 对比总结
        print("\n" + "="*80)
        print("📊 对比总结")
        print("="*80)
        print(f"\nNaive RAG:")
        print(f"  - 检索文档数: {naive_result['num_docs']}")
        print(f"  - 答案长度: {len(naive_result['answer'])} 字符")
        
        print(f"\nAdvanced RAG:")
        print(f"  - 检索文档数: {advanced_result['num_docs']}")
        print(f"  - 答案长度: {len(advanced_result['answer'])} 字符")
        
        if i < len(test_queries):
            input("\n按回车继续下一个测试...")

    print("\n\n" + "="*80)
    print("✅ 所有测试完成！")
    print("="*80)

if __name__ == "__main__":
    main()
