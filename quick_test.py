#!/usr/bin/env python3
"""
快速测试 Naive RAG（非交互模式）
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, '/home/zl/LLM/puxian-rag-assistant')

def test_vllm():
    """测试 vLLM 连接"""
    print("="*60)
    print("测试 1: vLLM API 连接")
    print("="*60)
    from backend.app.services.vllm_service import get_vllm_service
    
    vllm = get_vllm_service('http://127.0.0.1:8001/v1')
    
    # 简单测试
    response = vllm.generate('你好，用一句话介绍自己。', max_tokens=30, temperature=0.7)
    print(f"vLLM 回复: {response}\n")
    return True

def test_embedding():
    """测试 Embedding"""
    print("="*60)
    print("测试 2: Embedding 服务")
    print("="*60)
    from backend.app.services.embedding_service import EmbeddingService
    
    emb_service = EmbeddingService(
        model_path="/home/zl/LLM/bge-small-zh-v1.5"
    )
    
    # 测试编码
    text = "莆田话测试"
    embedding = emb_service.encode(text)
    print(f"文本: {text}")
    print(f"Embedding 维度: {embedding.shape}")
    print(f"Embedding 前5维: {embedding[0][:5]}\n")
    return True

def test_chromadb():
    """测试 ChromaDB"""
    print("="*60)
    print("测试 3: ChromaDB 连接")
    print("="*60)
    import chromadb
    
    client = chromadb.PersistentClient(path="/home/zl/LLM/chroma_db_putian")
    collection = client.get_collection(name="putian_dialect")
    
    count = collection.count()
    print(f"数据库文档总数: {count}\n")
    return True

def test_naive_rag():
    """测试完整 Naive RAG"""
    print("="*60)
    print("测试 4: 完整 Naive RAG 流程")
    print("="*60)
    
    from naive_rag import NaiveRAG
    
    # 初始化
    rag = NaiveRAG()
    
    # 执行查询
    query = "莆田话中'吃'怎么说？"
    result = rag.generate(query, top_k=3, verbose=False)
    
    print(f"\n查询: {query}")
    print(f"检索到文档数: {result['num_docs']}")
    print(f"\n答案:\n{result['answer']}\n")
    
    return True

if __name__ == "__main__":
    try:
        # 按顺序执行测试
        tests = [
            ("vLLM API", test_vllm),
            ("Embedding", test_embedding),
            ("ChromaDB", test_chromadb),
            ("Naive RAG", test_naive_rag)
        ]
        
        for name, test_func in tests:
            try:
                test_func()
                print(f"✅ {name} 测试通过\n")
            except Exception as e:
                print(f"❌ {name} 测试失败: {e}\n")
                import traceback
                traceback.print_exc()
                break
        
        print("\n" + "="*60)
        print("所有测试完成！")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
