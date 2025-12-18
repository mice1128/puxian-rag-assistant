"""
重新创建 ChromaDB 数据库
从原始 CSV 文件导入
"""
import chromadb
from backend.app.services.embedding_service import EmbeddingService
import pandas as pd
import os
from tqdm import tqdm

def recreate_database():
    print("=" * 60)
    print("重新创建 ChromaDB 数据库")
    print("=" * 60)
    
    # 配置
    CSV_FILE = "/home/zl/LLM/putian_dialect_template.csv"
    NEW_DB_PATH = "/home/zl/LLM/chroma_db_putian_new"
    OLD_DB_PATH = "/home/zl/LLM/chroma_db_putian"
    COLLECTION_NAME = "putian_dialect"
    
    # 1. 检查 CSV 文件
    print(f"\n[1/5] 检查数据文件...")
    if not os.path.exists(CSV_FILE):
        print(f"✗ 找不到数据文件: {CSV_FILE}")
        return False
    
    df = pd.read_csv(CSV_FILE)
    print(f"✓ 找到数据文件，共 {len(df)} 条记录")
    print(f"  列: {list(df.columns)}")
    
    # 2. 初始化 Embedding 模型
    print(f"\n[2/5] 加载 Embedding 模型...")
    embedding_service = EmbeddingService(
        model_path="/home/zl/LLM/bge-small-zh-v1.5"
    )
    print("✓ Embedding 模型加载完成")
    
    # 3. 创建新的数据库
    print(f"\n[3/5] 创建新数据库...")
    if os.path.exists(NEW_DB_PATH):
        import shutil
        print(f"  删除旧的临时数据库...")
        shutil.rmtree(NEW_DB_PATH)
    
    client = chromadb.PersistentClient(path=NEW_DB_PATH)
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "莆田方言知识库"}
    )
    print(f"✓ 新数据库创建成功: {NEW_DB_PATH}")
    
    # 4. 批量导入数据
    print(f"\n[4/5] 导入数据...")
    batch_size = 100
    
    for i in tqdm(range(0, len(df), batch_size), desc="导入进度"):
        batch = df.iloc[i:i+batch_size]
        
        # 准备文档和元数据
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in batch.iterrows():
            # 构建文档内容
            doc_parts = []
            for col in df.columns:
                if pd.notna(row[col]) and str(row[col]).strip():
                    doc_parts.append(f"{col}: {row[col]}")
            
            doc_text = "\n".join(doc_parts)
            documents.append(doc_text)
            
            # 元数据
            metadata = {k: str(v) for k, v in row.items() if pd.notna(v)}
            metadatas.append(metadata)
            
            # ID
            ids.append(f"doc_{idx}")
        
        # 生成 embeddings
        embeddings = embedding_service.encode(documents)
        embeddings_list = embeddings.tolist()
        
        # 添加到集合
        collection.add(
            embeddings=embeddings_list,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    print(f"✓ 导入完成！总计 {collection.count()} 个文档")
    
    # 5. 测试新数据库
    print(f"\n[5/5] 测试新数据库...")
    test_query = "莆田话中'吃'怎么说？"
    query_emb = embedding_service.encode(test_query)
    
    # query_emb 形状是 (1, 512)，tolist() 后是 [[...]]，直接传入即可
    results = collection.query(
        query_embeddings=query_emb.tolist(),
        n_results=3
    )
    
    if results['documents'] and len(results['documents'][0]) > 0:
        print(f"✓ 检索测试成功！查询: {test_query}")
        print(f"  检索到 {len(results['documents'][0])} 个结果")
        for i, doc in enumerate(results['documents'][0], 1):
            print(f"  [{i}] {doc[:100]}...")
    else:
        print("⚠ 检索测试失败，没有返回结果")
        return False
    
    # 6. 替换旧数据库
    print(f"\n" + "=" * 60)
    print("数据库创建成功！")
    print("=" * 60)
    print(f"\n新数据库位置: {NEW_DB_PATH}")
    print(f"旧数据库位置: {OLD_DB_PATH}")
    print(f"\n要替换旧数据库，请执行:")
    print(f"  mv {OLD_DB_PATH} {OLD_DB_PATH}_backup")
    print(f"  mv {NEW_DB_PATH} {OLD_DB_PATH}")
    
    return True

if __name__ == "__main__":
    success = recreate_database()
    if success:
        print("\n✅ 数据库重建成功！")
    else:
        print("\n❌ 数据库重建失败")
