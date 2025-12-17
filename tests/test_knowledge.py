#!/usr/bin/env python3
"""
测试知识库导入
支持多种文件格式
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from app.services.embedding_service import get_embedding_service
from app.services.rag_service import get_rag_service
from app.utils.file_parser import parse_file
import argparse

def import_file(filepath):
    """导入单个文件到知识库"""
    print(f"\n📁 导入文件: {filepath}")
    
    # 检查文件是否存在
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    # 解析文件
    print("  解析文件...")
    texts, metadatas = parse_file(filepath)
    print(f"  ✅ 解析完成，共 {len(texts)} 条记录")
    
    # 初始化服务
    print("  初始化服务...")
    embedding = get_embedding_service()
    rag = get_rag_service()
    
    # 添加到向量库
    print("  添加到向量库...")
    count = rag.add_documents(texts, metadatas)
    
    print(f"  ✅ 成功导入 {count} 条知识")
    print(f"  总计: {rag.collection.count()} 条知识\n")
    
    return True

def list_knowledge():
    """列出知识库统计"""
    print("\n📚 知识库统计")
    print("=" * 60)
    
    rag = get_rag_service()
    metrics = rag.get_metrics()
    
    print(f"  总文档数: {metrics['total_documents']}")
    print(f"  向量库路径: {metrics['vectorstore_path']}")
    print()

def search_knowledge(query, k=3):
    """搜索知识库"""
    print(f"\n🔍 搜索: {query}")
    print("=" * 60)
    
    rag = get_rag_service()
    results = rag.search(query, k=k)
    
    if not results:
        print("  未找到相关内容")
        return
    
    for i, doc in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"  文本: {doc['text'][:200]}...")
        print(f"  相似度: {1 - doc['distance']:.4f}")
        if doc['metadata']:
            print(f"  元数据: {doc['metadata']}")

def clear_knowledge():
    """清空知识库"""
    confirm = input("\n⚠️  确定要清空知识库吗？(yes/no): ").strip().lower()
    
    if confirm == 'yes':
        rag = get_rag_service()
        rag.clear()
        print("✅ 知识库已清空")
    else:
        print("❌ 取消操作")

def main():
    parser = argparse.ArgumentParser(description='知识库管理工具')
    parser.add_argument('action', choices=['import', 'list', 'search', 'clear'],
                       help='操作: import(导入), list(列表), search(搜索), clear(清空)')
    parser.add_argument('--file', '-f', help='要导入的文件路径')
    parser.add_argument('--query', '-q', help='搜索查询')
    parser.add_argument('--top-k', '-k', type=int, default=3, help='搜索返回数量')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📚 知识库管理工具")
    print("=" * 60)
    
    if args.action == 'import':
        if not args.file:
            print("❌ 错误: 请指定文件路径 --file")
            return
        import_file(args.file)
    
    elif args.action == 'list':
        list_knowledge()
    
    elif args.action == 'search':
        if not args.query:
            print("❌ 错误: 请指定搜索查询 --query")
            return
        search_knowledge(args.query, args.top_k)
    
    elif args.action == 'clear':
        clear_knowledge()

if __name__ == "__main__":
    main()
