#!/usr/bin/env python3
"""
知识库管理服务
"""
import os
import logging
from datetime import datetime
from ..utils.file_parser import parse_file

logger = logging.getLogger(__name__)


class KnowledgeService:
    """知识库管理服务"""
    
    def __init__(self):
        from ..config import Config
        from .rag_service import get_rag_service
        
        self.config = Config
        self.knowledge_dir = os.path.abspath(Config.KNOWLEDGE_DIR)
        self.rag_service = get_rag_service()
        
        os.makedirs(self.knowledge_dir, exist_ok=True)
        logger.info(f"知识库目录: {self.knowledge_dir}")
    
    def process_file(self, filepath):
        """处理知识库文件"""
        try:
            # 解析文件
            texts, metadatas = parse_file(filepath)
            
            if not texts:
                raise ValueError("文件中没有有效内容")
            
            # 添加到向量库
            count = self.rag_service.add_documents(texts, metadatas)
            
            return {
                'filename': os.path.basename(filepath),
                'added_count': count,
                'total_documents': self.rag_service.collection.count()
            }
            
        except Exception as e:
            logger.error(f"处理文件失败: {e}")
            raise
    
    def list_files(self):
        """列出所有知识库文件"""
        try:
            files = []
            for filename in os.listdir(self.knowledge_dir):
                filepath = os.path.join(self.knowledge_dir, filename)
                
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        'name': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'extension': os.path.splitext(filename)[1]
                    })
            
            return sorted(files, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            raise
    
    def delete_file(self, filename):
        """删除知识库文件"""
        try:
            filepath = os.path.join(self.knowledge_dir, filename)
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"文件不存在: {filename}")
            
            os.remove(filepath)
            
            return {
                'message': f'文件 {filename} 已删除'
            }
            
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            raise
    
    def rebuild_vectorstore(self):
        """重建向量库"""
        try:
            # 清空现有向量库
            self.rag_service.clear()
            
            # 重新处理所有文件
            total_count = 0
            files_processed = []
            
            for filename in os.listdir(self.knowledge_dir):
                filepath = os.path.join(self.knowledge_dir, filename)
                
                if os.path.isfile(filepath):
                    try:
                        result = self.process_file(filepath)
                        total_count += result['added_count']
                        files_processed.append(filename)
                    except Exception as e:
                        logger.warning(f"处理文件 {filename} 失败: {e}")
            
            return {
                'total_count': total_count,
                'files_processed': files_processed
            }
            
        except Exception as e:
            logger.error(f"重建向量库失败: {e}")
            raise


# 全局单例
_knowledge_service = None


def get_knowledge_service():
    """获取知识库服务单例"""
    global _knowledge_service
    if _knowledge_service is None:
        _knowledge_service = KnowledgeService()
    return _knowledge_service
