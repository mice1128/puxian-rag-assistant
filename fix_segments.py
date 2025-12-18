"""
修复 segments 表
"""
import sqlite3
import os

DB_PATH = "/home/zl/LLM/chroma_db_putian/chroma.sqlite3"

def fix_segments_table():
    print("=" * 60)
    print("修复 segments 表")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查 segments 表结构
    print("\n检查 segments 表...")
    cursor.execute("PRAGMA table_info(segments)")
    columns = {col[1] for col in cursor.fetchall()}
    
    print(f"当前列: {columns}")
    
    # 添加 topic 列
    if 'topic' not in columns:
        print("\n添加 'topic' 列...")
        try:
            cursor.execute("ALTER TABLE segments ADD COLUMN topic TEXT")
            conn.commit()
            print("✓ 成功添加 topic 列")
        except sqlite3.OperationalError as e:
            print(f"⚠ 添加列失败: {e}")
    else:
        print("✓ topic 列已存在")
    
    conn.close()
    print("\n修复完成！")

def verify():
    """验证修复"""
    print("\n" + "=" * 60)
    print("验证修复")
    print("=" * 60)
    
    try:
        import chromadb
        client = chromadb.PersistentClient(path="/home/zl/LLM/chroma_db_putian")
        collection = client.get_collection(name="langchain")
        count = collection.count()
        print(f"✓ 成功！集合 'langchain' 有 {count} 个文档")
        return True
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_segments_table()
    verify()
