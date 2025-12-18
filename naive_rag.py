"""
Naive RAG - 基础检索增强生成
使用 vLLM 作为推理引擎
"""
import sys
import os

# 添加项目根目录到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vllm_service import get_vllm_service
import chromadb


class NaiveRAG:
    """Naive RAG 实现 - Vector 检索 + vLLM 生成"""
    
    def __init__(
        self,
        collection_name: str = "putian_dialect",
        embedding_model_path: str = "/home/zl/LLM/bge-small-zh-v1.5",
        chroma_db_path: str = "/home/zl/LLM/chroma_db_putian",
        vllm_api_url: str = "http://127.0.0.1:8001/v1"
    ):
        """
        初始化 Naive RAG
        
        Args:
            collection_name: ChromaDB 集合名称
            embedding_model_path: Embedding 模型路径
            chroma_db_path: ChromaDB 数据库路径
            vllm_api_url: vLLM API 服务地址
        """
        print("=" * 60)
        print("初始化 Naive RAG 系统")
        print("=" * 60)
        
        # 1. 初始化 Embedding 服务
        print("\n[1/3] 加载 Embedding 模型...")
        self.embedding_service = EmbeddingService(
            model_path=embedding_model_path
        )
        print(f"✓ Embedding 模型加载完成: {embedding_model_path}")
        
        # 2. 连接 ChromaDB
        print("\n[2/3] 连接 ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        self.collection = self.chroma_client.get_collection(name=collection_name)
        print(f"✓ ChromaDB 连接成功: {collection_name}")
        print(f"  数据库路径: {chroma_db_path}")
        print(f"  文档总数: {self.collection.count()}")
        
        # 3. 初始化 vLLM 服务
        print("\n[3/3] 连接 vLLM 推理服务...")
        self.llm_service = get_vllm_service(vllm_api_url)
        
        print("\n" + "=" * 60)
        print("✓ Naive RAG 初始化完成！")
        print("=" * 60)
    
    def retrieve(self, query: str, top_k: int = 5) -> list:
        """
        向量检索
        
        Args:
            query: 用户查询
            top_k: 返回前 k 个相关文档
        
        Returns:
            检索结果列表
        """
        # 1. 生成查询向量
        query_embedding = self.embedding_service.encode(query)
        # query_embedding 形状是 (1, 512)，tolist() 后是 [[...]]
        query_emb_list = query_embedding.tolist()
        
        # 2. 向量检索
        results = self.collection.query(
            query_embeddings=query_emb_list,
            n_results=top_k
        )
        
        # 3. 格式化结果
        retrieved_docs = []
        if results and results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 0
                
                retrieved_docs.append({
                    'content': doc,
                    'metadata': metadata,
                    'score': 1 - distance,  # 转换为相似度分数
                    'rank': i + 1
                })
        
        return retrieved_docs
    
    def build_prompt(self, query: str, context_docs: list) -> str:
        """
        构建 RAG 提示词
        
        Args:
            query: 用户问题
            context_docs: 检索到的文档列表
        
        Returns:
            完整的提示词
        """
        # 拼接上下文
        context_text = "\n\n".join([
            f"[文档 {doc['rank']}]:\n{doc['content']}"
            for doc in context_docs
        ])
        
        # 构建提示词
        prompt = f"""你是一个莆田话（莆仙方言）专家助手。请根据以下参考资料回答用户的问题。

# 参考资料：
{context_text}

# 用户问题：
{query}

# 要求：
1. 基于参考资料回答，不要编造信息
2. 如果参考资料中没有相关信息，请诚实说明
3. 回答要准确、简洁、易懂
4. 如果涉及莆田话的发音或词汇，请提供详细解释

请回答："""

        return prompt
    
    def generate(self, query: str, top_k: int = 5, verbose: bool = True) -> dict:
        """
        执行完整的 RAG 流程
        
        Args:
            query: 用户查询
            top_k: 检索文档数量
            verbose: 是否打印详细信息
        
        Returns:
            包含答案和中间结果的字典
        """
        if verbose:
            print("\n" + "=" * 60)
            print(f"查询: {query}")
            print("=" * 60)
        
        # 1. 检索
        if verbose:
            print("\n[步骤 1] 向量检索...")
        retrieved_docs = self.retrieve(query, top_k)
        
        if verbose:
            print(f"✓ 检索到 {len(retrieved_docs)} 个相关文档:")
            for doc in retrieved_docs[:3]:  # 只显示前 3 个
                print(f"  - [排名 {doc['rank']}] 相似度: {doc['score']:.3f}")
                print(f"    内容预览: {doc['content'][:100]}...")
        
        # 2. 构建提示词
        if verbose:
            print("\n[步骤 2] 构建 RAG 提示词...")
        prompt = self.build_prompt(query, retrieved_docs)
        
        if verbose:
            print(f"✓ 提示词长度: {len(prompt)} 字符")
        
        # 3. 生成答案
        if verbose:
            print("\n[步骤 3] 调用 vLLM 生成答案...")
        answer = self.llm_service.generate(
            prompt=prompt,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9
        )
        
        if verbose:
            print("✓ 生成完成")
            print("\n" + "=" * 60)
            print("最终答案:")
            print("=" * 60)
            print(answer)
            print("=" * 60)
        
        return {
            'query': query,
            'answer': answer,
            'retrieved_docs': retrieved_docs,
            'prompt': prompt,
            'num_docs': len(retrieved_docs)
        }


def main():
    """测试 Naive RAG"""
    # 初始化
    rag = NaiveRAG()
    
    # 测试查询
    test_queries = [
        "莆田话中'食'怎么说？",
        "介绍一下莆田话的声调系统",
        "莆田话和普通话有什么区别？"
    ]
    
    print("\n\n" + "🔥" * 30)
    print("开始测试 Naive RAG")
    print("🔥" * 30)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*80}")
        print(f"测试 {i}/{len(test_queries)}")
        print(f"{'='*80}")
        
        result = rag.generate(query, top_k=3, verbose=True)
        
        input("\n按回车键继续下一个测试...")


if __name__ == "__main__":
    main()
