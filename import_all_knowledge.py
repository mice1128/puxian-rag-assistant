"""
导入所有知识库文件到 ChromaDB
支持多个CSV文件，自动处理不同格式
"""
import chromadb
from backend.app.services.embedding_service import EmbeddingService
import pandas as pd
import os
from tqdm import tqdm

def analyze_csv_files(data_dir):
    """分析CSV文件"""
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print("=" * 60)
    print("发现的CSV文件:")
    print("=" * 60)
    
    file_info = []
    for csv_file in csv_files:
        path = os.path.join(data_dir, csv_file)
        try:
            df = pd.read_csv(path)
            info = {
                'filename': csv_file,
                'path': path,
                'rows': len(df),
                'columns': list(df.columns)
            }
            file_info.append(info)
            
            print(f"\n文件: {csv_file}")
            print(f"  行数: {len(df)}")
            print(f"  列数: {len(df.columns)}")
            print(f"  列名: {', '.join(df.columns)}")
            
        except Exception as e:
            print(f"\n✗ 读取失败: {csv_file} - {e}")
    
    return file_info

def format_document(row, source_file):
    """
    格式化文档内容
    根据不同的数据源使用不同的格式
    """
    doc_parts = []
    
    # 添加来源标记
    doc_parts.append(f"[来源: {source_file}]")
    
    # 遍历所有列
    for col, value in row.items():
        if pd.notna(value) and str(value).strip():
            # 特殊处理某些重要字段
            if col in ['莆仙话', 'hinghwa', '词条']:
                doc_parts.insert(1, f"【{col}】{value}")
            else:
                doc_parts.append(f"{col}: {value}")
    
    return "\n".join(doc_parts)

def import_all_csvs(
    data_dir="/home/zl/LLM/puxian-rag-assistant/data/knowledge",
    db_path="/home/zl/LLM/chroma_db_putian_new",
    collection_name="putian_dialect"
):
    """导入所有CSV文件"""
    
    print("=" * 60)
    print("导入所有知识库文件到 ChromaDB")
    print("=" * 60)
    
    # 1. 分析CSV文件
    print(f"\n[1/5] 扫描数据目录: {data_dir}")
    file_info = analyze_csv_files(data_dir)
    
    if not file_info:
        print("✗ 没有找到CSV文件")
        return False
    
    total_rows = sum(f['rows'] for f in file_info)
    print(f"\n总计: {len(file_info)} 个文件, {total_rows} 条记录")
    
    # 2. 初始化 Embedding 模型
    print(f"\n[2/5] 加载 Embedding 模型...")
    embedding_service = EmbeddingService(
        model_path="/home/zl/LLM/bge-small-zh-v1.5"
    )
    print("✓ Embedding 模型加载完成")
    
    # 3. 创建数据库
    print(f"\n[3/5] 创建数据库...")
    if os.path.exists(db_path):
        import shutil
        print(f"  删除旧数据库: {db_path}")
        shutil.rmtree(db_path)
    
    client = chromadb.PersistentClient(path=db_path)
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "莆田方言知识库（完整版）"}
    )
    print(f"✓ 数据库创建: {db_path}")
    
    # 4. 逐个文件导入
    print(f"\n[4/5] 导入数据...")
    batch_size = 50
    doc_id_counter = 0
    
    for file_info_item in file_info:
        print(f"\n导入文件: {file_info_item['filename']}")
        df = pd.read_csv(file_info_item['path'])
        
        for i in tqdm(range(0, len(df), batch_size), desc=f"  {file_info_item['filename']}"):
            batch = df.iloc[i:i+batch_size]
            
            documents = []
            metadatas = []
            ids = []
            
            for idx, row in batch.iterrows():
                # 格式化文档
                doc_text = format_document(row, file_info_item['filename'])
                documents.append(doc_text)
                
                # 元数据
                metadata = {
                    'source_file': file_info_item['filename'],
                    'row_id': str(idx)
                }
                # 添加所有非空字段到元数据
                for col, val in row.items():
                    if pd.notna(val):
                        # 限制元数据值长度
                        val_str = str(val)
                        if len(val_str) > 500:
                            val_str = val_str[:500] + "..."
                        metadata[col] = val_str
                
                metadatas.append(metadata)
                
                # ID
                ids.append(f"doc_{doc_id_counter}")
                doc_id_counter += 1
            
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
        
        print(f"  ✓ {file_info_item['filename']}: {len(df)} 条记录导入完成")
    
    final_count = collection.count()
    print(f"\n✓ 所有文件导入完成！数据库总计: {final_count} 个文档")
    
    # 5. 测试检索
    print(f"\n[5/5] 测试检索功能...")
    test_queries = [
        "莆田话中'吃'怎么说？",
        "食",
        "方言"
    ]
    
    for query in test_queries:
        query_emb = embedding_service.encode(query)
        results = collection.query(
            query_embeddings=query_emb.tolist(),
            n_results=3
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            print(f"\n查询: '{query}'")
            print(f"  ✓ 检索到 {len(results['documents'][0])} 个结果")
            for i, doc in enumerate(results['documents'][0][:1], 1):
                print(f"  [{i}] {doc[:150]}...")
        else:
            print(f"\n查询: '{query}' - ⚠ 无结果")
    
    # 6. 提供替换指令
    print("\n" + "=" * 60)
    print("✅ 数据库创建成功！")
    print("=" * 60)
    print(f"\n新数据库位置: {db_path}")
    print(f"文档总数: {final_count}")
    print(f"\n要替换旧数据库，执行:")
    print(f"  mv /home/zl/LLM/chroma_db_putian /home/zl/LLM/chroma_db_putian_backup_$(date +%Y%m%d)")
    print(f"  mv {db_path} /home/zl/LLM/chroma_db_putian")
    
    return True

if __name__ == "__main__":
    success = import_all_csvs()
    if success:
        print("\n✅ 完成！")
    else:
        print("\n❌ 失败")
