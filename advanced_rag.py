"""
Advanced RAG - 混合检索 (Vector + BM25) + BGE Reranker
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vllm_service import get_vllm_service
import chromadb
from typing import List, Dict
import numpy as np


class BM25Retriever:
    """BM25 关键词检索器"""
    
    def __init__(self, documents: List[str]):
        """
        初始化 BM25
        
        Args:
            documents: 文档列表
        """
        from rank_bm25 import BM25Okapi
        import jieba
        
        # 分词
        self.tokenized_docs = [list(jieba.cut(doc)) for doc in documents]
        self.documents = documents
        self.bm25 = BM25Okapi(self.tokenized_docs)
        print(f"✓ BM25 索引构建完成，文档数: {len(documents)}")
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        BM25 检索
        
        Args:
            query: 查询文本
            top_k: 返回前 k 个结果
        
        Returns:
            检索结果列表
        """
        import jieba
        
        tokenized_query = list(jieba.cut(query))
        scores = self.bm25.get_scores(tokenized_query)
        
        # 获取 top_k 索引
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # 只返回有相关性的文档
                results.append({
                    'content': self.documents[idx],
                    'score': float(scores[idx]),
                    'rank': len(results) + 1,
                    'source': 'bm25'
                })
        
        return results


class BGEReranker:
    """BGE Reranker 重排序模型"""
    
    def __init__(self, model_path: str = "/home/zl/LLM/bge-reranker-base"):
        """
        初始化 Reranker
        
        Args:
            model_path: Reranker 模型路径
        """
        from FlagEmbedding import FlagReranker
        
        print(f"加载 BGE Reranker: {model_path}")
        self.reranker = FlagReranker(model_path, use_fp16=True, device="cuda:1")
        print("✓ Reranker 加载完成")
    
    def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict]:
        """
        重排序文档
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前 k 个结果
        
        Returns:
            重排序后的文档列表
        """
        if not documents:
            return []
        
        # 构建查询-文档对
        pairs = [[query, doc] for doc in documents]
        
        # 计算相关性分数
        scores = self.reranker.compute_score(pairs)
        
        # 如果只有一个文档，scores 是单个数值
        if not isinstance(scores, list):
            scores = [scores]
        
        # 按分数排序
        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # 返回 top_k
        results = []
        for i, (doc, score) in enumerate(doc_score_pairs[:top_k]):
            results.append({
                'content': doc,
                'score': float(score),
                'rank': i + 1,
                'source': 'reranker'
            })
        
        return results


class AdvancedRAG:
    """Advanced RAG - 混合检索 + 重排序"""
    
    def __init__(
        self,
        collection_name: str = "langchain",
        embedding_model_path: str = "/home/zl/LLM/bge-small-zh-v1.5",
        reranker_model_path: str = "/home/zl/LLM/bge-reranker-base",
        chroma_db_path: str = "/home/zl/LLM/chroma_db_putian",
        vllm_api_url: str = "http://127.0.0.1:8001/v1"
    ):
        """初始化 Advanced RAG"""
        print("=" * 60)
        print("初始化 Advanced RAG 系统")
        print("=" * 60)
        
        # 1. Embedding 服务
        print("\n[1/5] 加载 Embedding 模型...")
        self.embedding_service = EmbeddingService(model_path=embedding_model_path)
        print(f"✓ Embedding 模型: {embedding_model_path}")
        
        # 2. ChromaDB
        print("\n[2/5] 连接 ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        self.collection = self.chroma_client.get_collection(name=collection_name)
        doc_count = self.collection.count()
        print(f"✓ 向量数据库: {collection_name} ({doc_count} 文档)")
        
        # 3. 加载所有文档用于 BM25
        print("\n[3/5] 构建 BM25 索引...")
        all_docs = self.collection.get(include=["documents"])
        self.all_documents = all_docs['documents']
        self.bm25_retriever = BM25Retriever(self.all_documents)
        
        # 4. Reranker
        print("\n[4/5] 加载 Reranker 模型...")
        self.reranker = BGEReranker(model_path=reranker_model_path)
        
        # 5. vLLM
        print("\n[5/5] 连接 vLLM 服务...")
        self.llm_service = get_vllm_service(vllm_api_url)
        
        print("\n" + "=" * 60)
        print("✓ Advanced RAG 初始化完成！")
        print("=" * 60)
    
    def vector_search(self, query: str, top_k: int = 20) -> List[Dict]:
        """向量检索"""
        query_emb = self.embedding_service.encode(query)
        # query_emb 形状是 (1, 512)，tolist() 后是 [[...]]
        query_emb_list = query_emb.tolist()
        
        results = self.collection.query(
            query_embeddings=query_emb_list,
            n_results=top_k,
            include=["documents", "distances"]
        )
        
        retrieved = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i]
                retrieved.append({
                    'content': doc,
                    'score': 1 - distance,
                    'rank': i + 1,
                    'source': 'vector'
                })
        
        return retrieved
    
    def hybrid_search(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        混合检索：Vector + BM25
        
        使用 RRF (Reciprocal Rank Fusion) 融合结果
        """
        # 1. 向量检索
        vector_results = self.vector_search(query, top_k=top_k)
        
        # 2. BM25 检索
        bm25_results = self.bm25_retriever.search(query, top_k=top_k)
        
        # 3. RRF 融合
        k = 60  # RRF 参数
        doc_scores = {}
        
        for result in vector_results:
            doc = result['content']
            rank = result['rank']
            rrf_score = 1.0 / (k + rank)
            doc_scores[doc] = doc_scores.get(doc, 0) + rrf_score
        
        for result in bm25_results:
            doc = result['content']
            rank = result['rank']
            rrf_score = 1.0 / (k + rank)
            doc_scores[doc] = doc_scores.get(doc, 0) + rrf_score
        
        # 4. 排序
        ranked_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        hybrid_results = []
        for i, (doc, score) in enumerate(ranked_docs[:top_k]):
            hybrid_results.append({
                'content': doc,
                'score': score,
                'rank': i + 1,
                'source': 'hybrid'
            })
        
        return hybrid_results
    
    def retrieve_and_rerank(self, query: str, retrieval_top_k: int = 20, final_top_k: int = 5) -> List[Dict]:
        """
        混合检索 + 重排序
        
        Args:
            query: 查询
            retrieval_top_k: 混合检索返回的文档数
            final_top_k: 重排序后保留的文档数
        """
        # 1. 混合检索
        hybrid_results = self.hybrid_search(query, top_k=retrieval_top_k)
        
        if not hybrid_results:
            return []
        
        # 2. Reranker 重排序
        docs_to_rerank = [r['content'] for r in hybrid_results]
        reranked = self.reranker.rerank(query, docs_to_rerank, top_k=final_top_k)
        
        return reranked
    
    def build_prompt(self, query: str, context_docs: List[Dict]) -> str:
        """构建提示词"""
        if not context_docs:
            context_text = "(没有找到相关参考资料)"
        else:
            context_text = "\n\n".join([
                f"[参考文档 {doc['rank']}] (相关度: {doc['score']:.3f})\n{doc['content']}"
                for doc in context_docs
            ])
        
        prompt = f"""你是一个莆田话（莆仙方言）专家助手。请根据以下参考资料回答用户的问题。

# 参考资料：
{context_text}

# 用户问题：
{query}

# 回答要求：
1. **严格基于参考资料回答**，不要编造信息
2. 如果参考资料中没有相关信息，请明确说明
3. 回答要准确、简洁、易懂
4. 如果涉及莆田话的发音或词汇，请提供详细解释

请回答："""
        
        return prompt
    
    def generate(self, query: str, retrieval_top_k: int = 20, final_top_k: int = 5, verbose: bool = True) -> Dict:
        """执行 Advanced RAG"""
        if verbose:
            print("\n" + "=" * 60)
            print(f"查询: {query}")
            print("=" * 60)
        
        # 1. 混合检索 + 重排序
        if verbose:
            print("\n[步骤 1] 混合检索 (Vector + BM25)...")
        
        retrieved_docs = self.retrieve_and_rerank(query, retrieval_top_k, final_top_k)
        
        if verbose:
            print(f"✓ 检索并重排序完成，最终保留 {len(retrieved_docs)} 个文档:")
            for doc in retrieved_docs:
                print(f"  - [排名 {doc['rank']}] 相关度: {doc['score']:.4f}")
                print(f"    内容: {doc['content'][:80]}...")
        
        # 2. 构建提示词
        if verbose:
            print("\n[步骤 2] 构建提示词...")
        prompt = self.build_prompt(query, retrieved_docs)
        
        # 3. 生成答案
        if verbose:
            print("\n[步骤 3] vLLM 生成答案...")
        answer = self.llm_service.generate(
            prompt=prompt,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9
        )
        
        if verbose:
            print("✓ 生成完成\n")
            print("=" * 60)
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
    """测试 Advanced RAG"""
    # 注意：需要先下载 bge-reranker-base 模型
    # 如果没有，会自动从 HuggingFace 下载
    
    rag = AdvancedRAG()
    
    test_queries = [
        "莆田话中'吃'怎么说？",
        "介绍一下莆田话的声调系统",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*80}")
        print(f"测试 {i}/{len(test_queries)}")
        print(f"{'='*80}")
        
        result = rag.generate(query, retrieval_top_k=20, final_top_k=3, verbose=True)
        
        if i < len(test_queries):
            input("\n按回车继续...")


if __name__ == "__main__":
    main()
