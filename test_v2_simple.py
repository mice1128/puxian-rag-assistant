"""
简化测试: Advanced RAG v2 单独运行
"""
from advanced_rag_v2 import AdvancedRAGv2


def main():
    """简单测试"""
    print("初始化 Advanced RAG v2...")
    rag = AdvancedRAGv2()
    
    query = "莆田话中'吃'怎么说？"
    
    print(f"\n\n测试查询: {query}")
    print("=" * 80)
    
    result = rag.generate(
        query=query,
        use_query_rewrite=True,
        retrieval_top_k=15,
        final_top_k=3,
        verbose=True
    )
    
    print("\n\n完成！")


if __name__ == "__main__":
    main()
