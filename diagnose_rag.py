"""
诊断 RAG 检索问题
"""
import sys
sys.path.insert(0, '/home/zl/LLM/puxian-rag-assistant')

import chromadb
from backend.app.services.embedding_service import EmbeddingService
import numpy as np

def diagnose():
    print("=" * 60)
    print("RAG 检索诊断")
    print("=" * 60)
    
    # 1. 连接数据库
    print("\n[1] 连接 ChromaDB...")
    client = chromadb.PersistentClient(path="/home/zl/LLM/chroma_db_putian")
    
    # 列出所有集合
    collections = client.list_collections()
    print(f"✓ 找到 {len(collections)} 个集合:")
    for coll in collections:
        print(f"  - {coll.name}")
    
    if not collections:
        print("✗ 数据库中没有集合！请先运行 import_all_knowledge.py 导入数据")
        return
    
    # 使用第一个集合
    collection = collections[0]
    print(f"\n使用集合: {collection.name}, 文档数: {collection.count()}")
    
    # 2. 查看一个样本文档
    print("\n[2] 获取样本文档...")
    sample = collection.get(limit=2, include=["embeddings", "documents", "metadatas"])
    
    if sample['documents']:
        print(f"样本文档 1: {sample['documents'][0][:200]}...")
        if sample['embeddings'] and sample['embeddings'][0]:
            emb_dim = len(sample['embeddings'][0])
            print(f"样本 embedding 维度: {emb_dim}")
            print(f"样本 embedding 前5维: {sample['embeddings'][0][:5]}")
        else:
            print("⚠️ 样本文档没有 embedding！")
    
    # 3. 测试当前 embedding 模型
    print("\n[3] 测试当前 Embedding 模型...")
    emb_service = EmbeddingService(model_path="/home/zl/LLM/bge-small-zh-v1.5")
    
    test_text = "莆田话测试"
    query_emb = emb_service.encode(test_text)
    print(f"查询文本: {test_text}")
    print(f"查询 embedding 维度: {query_emb.shape}")
    print(f"查询 embedding 前5维: {query_emb[0][:5]}")
    
    # 4. 测试检索
    print("\n[4] 测试检索...")
    query = "莆田话中'吃'怎么说？"
    query_emb = emb_service.encode(query)
    
    # 转换格式
    if len(query_emb.shape) == 1:
        query_emb_list = [query_emb.tolist()]
    else:
        query_emb_list = query_emb.tolist()
    
    print(f"查询: {query}")
    print(f"查询向量格式: {type(query_emb_list)}, 长度: {len(query_emb_list)}")
    
    try:
        results = collection.query(
            query_embeddings=query_emb_list,
            n_results=5,
            include=["documents", "distances"]
        )
        
        print(f"\n检索结果:")
        print(f"  返回文档数: {len(results['documents'][0]) if results['documents'] else 0}")
        
        if results['documents'] and len(results['documents'][0]) > 0:
            for i, doc in enumerate(results['documents'][0][:3]):
                distance = results['distances'][0][i] if results['distances'] else 'N/A'
                print(f"\n  [{i+1}] 距离: {distance}")
                print(f"      内容: {doc[:150]}...")
        else:
            print("  ⚠️ 没有检索到任何文档！")
            
            # 尝试直接查询所有文档
            print("\n[5] 尝试直接peek所有文档...")
            peek = collection.peek(limit=3)
            print(f"  数据库前3个文档:")
            for i, doc in enumerate(peek['documents']):
                print(f"  [{i+1}] {doc[:100]}...")
    
    except Exception as e:
        print(f"✗ 检索失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose()
