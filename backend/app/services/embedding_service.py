#!/usr/bin/env python3
"""
嵌入模型服务
"""
from sentence_transformers import SentenceTransformer
import logging
import os

logger = logging.getLogger(__name__)


class EmbeddingService:
    """嵌入模型服务（单例）"""
    _instance = None
    
    def __new__(cls, model_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_path=None):
        if self._initialized:
            return
        
        # 转换为绝对路径
        if model_path:
            self.model_path = os.path.abspath(model_path)
        else:
            from ..config import Config
            self.model_path = os.path.abspath(Config.EMBEDDING_MODEL_PATH)
        
        self.model = None
        logger.info("嵌入模型服务已初始化（懒加载模式）")
        # 延迟加载：首次调用 encode() 时才加载模型
        self._initialized = True
    
    def load_model(self):
        """加载模型"""
        try:
            logger.info(f"正在加载嵌入模型: {self.model_path}")
            
            # 强制使用 GPU 1
            self.model = SentenceTransformer(self.model_path, device="cuda:1")
            
            logger.info("✅ 嵌入模型加载成功")
            
        except Exception as e:
            logger.error(f"❌ 加载嵌入模型失败: {e}")
            raise
    
    def encode(self, texts):
        """文本编码"""
        # 懒加载：首次调用时加载模型
        if self.model is None:
            logger.info("首次调用，开始加载嵌入模型...")
            self.load_model()
        
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"文本编码失败: {e}")
            raise


# 全局单例
_embedding_service = None


def get_embedding_service():
    """获取嵌入服务单例"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
