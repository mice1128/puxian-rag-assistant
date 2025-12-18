"""
快速测试 Naive RAG - 单个查询
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from naive_rag import NaiveRAG

# 初始化 RAG
print("初始化 Naive RAG...")
rag = NaiveRAG()

# 单个测试查询
query = "莆田话中'食'怎么说？"
print(f"\n查询: {query}\n")

# 执行 RAG
result = rag.generate(query, top_k=3, verbose=True)

print("\n✅ 测试完成！")
