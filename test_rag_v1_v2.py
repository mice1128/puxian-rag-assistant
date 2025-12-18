"""
对比测试: Advanced RAG v1 vs v2
"""
from advanced_rag import AdvancedRAG
from advanced_rag_v2 import AdvancedRAGv2
import time


def test_comparison():
    """对比测试"""
    print("\n" + "=" * 80)
    print("Advanced RAG v1 vs v2 对比测试")
    print("=" * 80)
    
    # 初始化
    print("\n初始化 v1...")
    rag_v1 = AdvancedRAG()
    
    print("\n初始化 v2...")
    rag_v2 = AdvancedRAGv2()
    
    # 测试查询
    test_queries = [
        "莆田话中'吃'怎么说？",
        "莆田话的'去'怎么发音",
    ]
    
    for query in test_queries:
        print("\n\n" + "=" * 80)
        print(f"测试查询: {query}")
        print("=" * 80)
        
        # v1 测试
        print("\n" + "-" * 80)
        print("【Advanced RAG v1】基础版本")
        print("-" * 80)
        start_time = time.time()
        result_v1 = rag_v1.generate(
            query=query,
            retrieval_top_k=15,
            final_top_k=3,
            verbose=False
        )
        v1_time = time.time() - start_time
        
        print(f"\n✓ 检索到 {result_v1['num_docs']} 个文档")
        print(f"✓ 生成时间: {v1_time:.2f}s")
        print("\n答案:")
        print(result_v1['answer'])
        
        # v2 测试
        print("\n" + "-" * 80)
        print("【Advanced RAG v2】深度优化版")
        print("优化点: Query Rewrite + Enhanced Prompt (Few-shot + CoT)")
        print("-" * 80)
        start_time = time.time()
        result_v2 = rag_v2.generate(
            query=query,
            use_query_rewrite=True,
            retrieval_top_k=15,
            final_top_k=3,
            verbose=False
        )
        v2_time = time.time() - start_time
        
        print(f"\n✓ 查询改写: {len(result_v2['rewritten_queries'])} 个变体")
        for i, q in enumerate(result_v2['rewritten_queries']):
            print(f"  {i+1}. {q}")
        print(f"✓ 检索到 {result_v2['num_docs']} 个文档")
        print(f"✓ 生成时间: {v2_time:.2f}s")
        print("\n答案:")
        print(result_v2['answer'])
        
        # 对比
        print("\n" + "-" * 80)
        print("对比总结")
        print("-" * 80)
        print(f"v1 时间: {v1_time:.2f}s | v2 时间: {v2_time:.2f}s (慢 {v2_time - v1_time:.2f}s)")
        print(f"v1 答案长度: {len(result_v1['answer'])} 字 | v2 答案长度: {len(result_v2['answer'])} 字")
        
        input("\n按回车继续下一个测试...")
    
    print("\n\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    print("\nv2 相比 v1 的改进:")
    print("1. ✓ Query Rewrite - 多查询变体提升召回率")
    print("2. ✓ Enhanced Prompt - Few-shot 示例 + CoT 思维链")
    print("3. ✓ 更结构化的输出格式")
    print("\n预期效果:")
    print("- 答案更准确、更详细")
    print("- 提供使用例句")
    print("- 补充文化背景")


if __name__ == "__main__":
    test_comparison()
