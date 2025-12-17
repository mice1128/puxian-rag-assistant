#!/usr/bin/env python3
"""
RAG 服务
"""
import chromadb
from chromadb.config import Settings
import logging
import os

logger = logging.getLogger(__name__)


class RAGService:
    """RAG 服务"""
    
    def __init__(self):
        from ..config import Config
        from .qwen_service import get_qwen_service
        from .embedding_service import get_embedding_service
        
        self.config = Config
        self.qwen = get_qwen_service()
        self.embedding = get_embedding_service()
        
        # 初始化向量库
        self.vectorstore_dir = os.path.abspath(Config.VECTORSTORE_DIR)
        os.makedirs(self.vectorstore_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=self.vectorstore_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="putian_dialect",
            metadata={"description": "莆仙话知识库"}
        )
        
        logger.info(f"✅ RAG 服务初始化完成，向量库: {self.vectorstore_dir}")
    
    def add_documents(self, texts, metadatas=None):
        """添加文档到向量库（分批处理）"""
        try:
            batch_size = 500  # ChromaDB 批量大小限制
            total_added = 0
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size] if metadatas else [{}] * len(batch_texts)
                
                # 生成嵌入
                embeddings = self.embedding.encode(batch_texts)
                
                # 生成 ID
                start_id = self.collection.count()
                ids = [f"doc_{j}" for j in range(start_id, start_id + len(batch_texts))]
                
                # 添加到向量库
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    ids=ids
                )
                
                total_added += len(batch_texts)
                logger.info(f"已添加 {total_added}/{len(texts)} 条文档")
            
            logger.info(f"✅ 成功添加 {total_added} 条文档到向量库")
            return total_added
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            raise
    
    def search(self, query, k=3):
        """语义搜索"""
        try:
            # 生成查询嵌入
            query_embedding = self.embedding.encode([query])[0]
            
            # 搜索
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=k
            )
            
            # 格式化结果
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise
    
    def ask(self, question):
        """RAG 问答"""
        try:
            # 1. 检索相关文档
            docs = self.search(question, k=self.config.TOP_K)
            
            if not docs:
                return {
                    'answer': '抱歉，知识库中没有找到相关信息。',
                    'sources': [],
                    'tokens_used': 0
                }
            
            # 2. 构建提示词
            context = "\n\n".join([f"参考资料 {i+1}:\n{doc['text']}" for i, doc in enumerate(docs)])
            
            prompt = f"""你是一个莆仙话（莆仙语）专家助手。请根据以下参考资料回答用户的问题。

{context}

用户问题：{question}

请用简洁、准确的语言回答，如果参考资料中没有相关信息，请如实说明。"""
            
            # 3. 生成回答
            answer, tokens = self.qwen.generate(
                prompt,
                max_new_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE
            )
            
            return {
                'answer': answer.strip(),
                'sources': [{'text': doc['text'], 'metadata': doc['metadata']} for doc in docs],
                'tokens_used': tokens
            }
            
        except Exception as e:
            logger.error(f"问答失败: {e}")
            raise
    
    def clear(self):
        """清空向量库"""
        try:
            # 删除并重建集合
            self.client.delete_collection("putian_dialect")
            self.collection = self.client.create_collection(
                name="putian_dialect",
                metadata={"description": "莆仙话知识库"}
            )
            logger.info("向量库已清空")
            
        except Exception as e:
            logger.error(f"清空向量库失败: {e}")
            raise
    
    def get_metrics(self):
        """获取统计信息"""
        return {
            'total_documents': self.collection.count(),
            'vectorstore_path': self.vectorstore_dir
        }


# 全局单例
_rag_service = None


def get_rag_service():
    """获取 RAG 服务单例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
