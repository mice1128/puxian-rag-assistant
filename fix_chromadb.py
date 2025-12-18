"""
ChromaDB 数据库修复工具
解决 'no such column: collections.topic' 错误
"""
import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = "/home/zl/LLM/chroma_db_putian/chroma.sqlite3"
BACKUP_DIR = "/home/zl/LLM/chroma_db_putian/backups"

def backup_database():
    """备份数据库"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}/chroma_backup_{timestamp}.sqlite3"
    
    print(f"备份数据库到: {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    print("✓ 备份完成")
    return backup_path

def check_schema():
    """检查数据库架构"""
    print("\n检查当前数据库架构...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查 collections 表结构
    cursor.execute("PRAGMA table_info(collections)")
    columns = cursor.fetchall()
    
    print("\ncollections 表当前列:")
    column_names = [col[1] for col in columns]
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    return column_names

def add_missing_columns():
    """添加缺失的列"""
    print("\n开始修复数据库...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查是否需要添加 topic 列
    cursor.execute("PRAGMA table_info(collections)")
    columns = {col[1] for col in cursor.fetchall()}
    
    if 'topic' not in columns:
        print("添加 'topic' 列...")
        try:
            cursor.execute("ALTER TABLE collections ADD COLUMN topic TEXT")
            conn.commit()
            print("✓ 成功添加 topic 列")
        except sqlite3.OperationalError as e:
            print(f"⚠ 添加列失败: {e}")
    else:
        print("✓ topic 列已存在")
    
    # 检查是否需要添加其他列
    if 'database_id' not in columns:
        print("添加 'database_id' 列...")
        try:
            cursor.execute("ALTER TABLE collections ADD COLUMN database_id TEXT")
            conn.commit()
            print("✓ 成功添加 database_id 列")
        except sqlite3.OperationalError as e:
            print(f"⚠ 添加列失败: {e}")
    
    conn.close()

def verify_fix():
    """验证修复结果"""
    print("\n验证修复...")
    try:
        import chromadb
        client = chromadb.PersistentClient(path="/home/zl/LLM/chroma_db_putian")
        collection = client.get_collection(name="putian_dialect")
        count = collection.count()
        print(f"✓ 数据库修复成功！")
        print(f"✓ 文档总数: {count}")
        return True
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        return False

def main():
    print("=" * 60)
    print("ChromaDB 数据库修复工具")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"✗ 数据库文件不存在: {DB_PATH}")
        return
    
    # 1. 备份
    backup_path = backup_database()
    
    # 2. 检查当前架构
    columns = check_schema()
    
    # 3. 添加缺失的列
    add_missing_columns()
    
    # 4. 验证修复
    if verify_fix():
        print("\n" + "=" * 60)
        print("✅ 数据库修复完成！")
        print("=" * 60)
        print(f"\n备份文件保存在: {backup_path}")
        print("如果遇到问题，可以从备份恢复。")
    else:
        print("\n" + "=" * 60)
        print("❌ 数据库修复失败")
        print("=" * 60)
        print(f"\n请从备份恢复: {backup_path}")
        print(f"恢复命令: cp {backup_path} {DB_PATH}")

if __name__ == "__main__":
    main()
