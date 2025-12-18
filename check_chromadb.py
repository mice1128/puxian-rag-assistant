"""
检查 ChromaDB 数据库内容
"""
import sqlite3
import chromadb

DB_PATH = "/home/zl/LLM/chroma_db_putian/chroma.sqlite3"

def check_database_directly():
    """直接通过 SQL 检查数据库"""
    print("=" * 60)
    print("直接检查数据库 (SQL)")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查所有表
    print("\n数据库中的表:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table[0]}")
    
    # 检查集合
    print("\ncollections 表内容:")
    cursor.execute("SELECT id, name, dimension FROM collections")
    collections = cursor.fetchall()
    if collections:
        for coll in collections:
            print(f"  - ID: {coll[0]}")
            print(f"    名称: {coll[1]}")
            print(f"    维度: {coll[2]}")
    else:
        print("  (空)")
    
    # 检查文档数量
    if 'embeddings' in [t[0] for t in tables]:
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        count = cursor.fetchone()[0]
        print(f"\nembeddings 表文档数: {count}")
    
    conn.close()

def check_with_chromadb():
    """使用 ChromaDB API 检查"""
    print("\n" + "=" * 60)
    print("使用 ChromaDB API 检查")
    print("=" * 60)
    
    try:
        client = chromadb.PersistentClient(path="/home/zl/LLM/chroma_db_putian")
        
        # 列出所有集合
        collections = client.list_collections()
        print(f"\n找到 {len(collections)} 个集合:")
        for coll in collections:
            print(f"  - 名称: {coll.name}")
            print(f"    ID: {coll.id}")
            print(f"    元数据: {coll.metadata}")
            try:
                count = coll.count()
                print(f"    文档数: {count}")
            except Exception as e:
                print(f"    文档数: (无法获取: {e})")
        
        if not collections:
            print("  (没有集合)")
        
    except Exception as e:
        print(f"✗ ChromaDB API 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_directly()
    check_with_chromadb()
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)
