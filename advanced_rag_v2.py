"""
Advanced RAG v2 - 深度优化版
包含: Query Rewrite + Document Optimization + Prompt Engineering
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vllm_service import get_vllm_service
import chromadb
from typing import List, Dict
import numpy as np
from rank_bm25 import BM25Okapi
import jieba


class QueryRewriter:
    """查询改写器 - 使用 LLM 优化查询"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    def rewrite(self, query: str, strategy: str = "expand") -> List[str]:
        """
        改写查询
        
        Args:
            query: 原始查询
            strategy: 改写策略 (expand, clarify, multi)
        
        Returns:
            改写后的查询列表
        """
        if strategy == "expand":
            # 扩展查询 - 添加同义词和相关词
            prompt = f"""请将以下问题改写为3个更详细、更具体的检索查询。
要求：
1. 保留原意，但使用更精确的词汇
2. 添加相关的同义词或近义词
3. 每个改写应从不同角度表达

原问题：{query}

请直接返回3个改写后的查询，每行一个，不要编号和解释："""

        elif strategy == "clarify":
            # 澄清查询 - 消除歧义
            prompt = f"""请将以下问题改写为更清晰、无歧义的检索查询。

原问题：{query}

改写后的查询（只返回一个）："""

        else:  # multi
            # 多角度改写
            prompt = f"""请从不同角度改写以下问题，生成3个检索查询：
1. 从定义角度
2. 从用法角度  
3. 从例句角度

原问题：{query}

请直接返回3个查询，每行一个："""
        
        response = self.llm_service.generate(
            prompt=prompt,
            max_tokens=150,
            temperature=0.3
        )
        
        # 解析返回的多个查询
        rewritten = [q.strip() for q in response.strip().split('\n') if q.strip()]
        
        # 始终包含原查询
        queries = [query] + rewritten[:3]  # 最多4个查询
        
        return queries


class EnhancedPromptBuilder:
    """增强的提示词构建器 - Few-shot + Chain-of-Thought"""
    
    def __init__(self):
        # Few-shot 示例
        self.examples = [
            {
                "query": "莆田话中'走'怎么说？",
                "context": "莆仙话: 行\n国际音标: [kiã]\n普通话: 走",
                "answer": "在莆田话中，'走'说作'行'，发音为 [kiã]。\n\n例如：\n- 我要去行街（我要去逛街）\n- 行去学堂（走去学校）\n\n这个词保留了古汉语的用法，'行'在古代就有'走'的意思。"
            }
        ]
    
    def build(self, query: str, context_docs: List[Dict]) -> str:
        """构建优化的提示词"""
        
        # 格式化上下文
        if not context_docs:
            context_text = "(没有找到相关参考资料)"
        else:
            context_parts = []
            for doc in context_docs:
                context_parts.append(
                    f"【文档 {doc['rank']}】(相关度: {doc['score']:.3f})\n{doc['content']}"
                )
            context_text = "\n\n".join(context_parts)
        
        # 构建 Few-shot + CoT 提示词
        prompt = f"""你是一个专业的莆田话（莆仙方言）专家助手。

# 你的专长
- 精通莆田话的发音、词汇、语法
- 了解莆田话与古汉语、闽南语的关系
- 能够提供准确的国际音标标注

# 回答示例
用户问: {self.examples[0]['query']}
参考资料: {self.examples[0]['context']}

你的回答: {self.examples[0]['answer']}

# 回答步骤（请按此思路回答）
1. 从参考资料中提取关键信息
2. 给出莆田话的说法和发音
3. 提供使用例句
4. 补充文化或语言学背景

# 当前任务
## 参考资料
{context_text}

## 用户问题
{query}

## 你的回答
请按照上述步骤，基于参考资料回答（如果参考资料不足，请明确说明）："""

        return prompt


class AdvancedRAGv2:
    """Advanced RAG v2 - 深度优化版"""
    
    def __init__(
        self,
        collection_name: str = "putian_dialect",
        embedding_model_path: str = "/home/zl/LLM/bge-small-zh-v1.5",
        reranker_model_path: str = "BAAI/bge-reranker-base",
        chroma_db_path: str = "/home/zl/LLM/chroma_db_putian",
        vllm_api_url: str = "http://127.0.0.1:8001/v1"
    ):
        """初始化"""
        print("=" * 60)
        print("初始化 Advanced RAG v2 系统")
        print("=" * 60)
        
        # 1. Embedding
        print("\n[1/6] 加载 Embedding 模型...")
        self.embedding_service = EmbeddingService(model_path=embedding_model_path)
        print(f"✓ Embedding: {embedding_model_path}")
        
        # 2. ChromaDB
        print("\n[2/6] 连接向量数据库...")
        self.chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        self.collection = self.chroma_client.get_collection(name=collection_name)
        doc_count = self.collection.count()
        print(f"✓ 数据库: {collection_name} ({doc_count} 文档)")
        
        # 3. BM25
        print("\n[3/6] 构建 BM25 索引...")
        all_docs = self.collection.get(include=["documents"])
        self.all_documents = all_docs['documents']
        self.tokenized_docs = [list(jieba.cut(doc)) for doc in self.all_documents]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        print(f"✓ BM25 索引: {len(self.all_documents)} 文档")
        
        # 4. Reranker
        print("\n[4/6] 加载 Reranker...")
        from FlagEmbedding import FlagReranker
        local_path = "/home/zl/LLM/bge-reranker-base"
        model_path = local_path if os.path.exists(local_path) else reranker_model_path
        try:
            self.reranker = FlagReranker(model_path, use_fp16=True, device="cuda:1", num_workers=0)
            print("✓ Reranker 加载完成")
        except:
            print("⚠ Reranker 不可用，将使用简化方案")
            self.reranker = None
        
        # 5. vLLM
        print("\n[5/6] 连接 vLLM 服务...")
        self.llm_service = get_vllm_service(vllm_api_url)
        
        # 6. 增强组件
        print("\n[6/6] 初始化增强组件...")
        self.query_rewriter = QueryRewriter(self.llm_service)
        self.prompt_builder = EnhancedPromptBuilder()
        print("✓ Query Rewriter & Enhanced Prompt")
        
        print("\n" + "=" * 60)
        print("✓ Advanced RAG v2 初始化完成！")
        print("=" * 60)
    
    def vector_search(self, query: str, top_k: int = 20) -> List[Dict]:
        """向量检索"""
        query_emb = self.embedding_service.encode(query)
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
    
    def bm25_search(self, query: str, top_k: int = 20) -> List[Dict]:
        """BM25 检索"""
        tokenized_query = list(jieba.cut(query))
        scores = self.bm25.get_scores(tokenized_query)
        
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    'content': self.all_documents[idx],
                    'score': float(scores[idx]),
                    'rank': len(results) + 1,
                    'source': 'bm25'
                })
        
        return results
    
    def hybrid_search(self, queries: List[str], top_k: int = 20) -> List[Dict]:
        """
        多查询混合检索
        
        Args:
            queries: 多个查询（原始 + 改写）
            top_k: 每个查询返回的文档数
        """
        all_docs = {}
        
        for query in queries:
            # 向量检索
            vector_results = self.vector_search(query, top_k=top_k)
            for result in vector_results:
                doc = result['content']
                if doc not in all_docs:
                    all_docs[doc] = {'vector_score': 0, 'bm25_score': 0}
                all_docs[doc]['vector_score'] = max(all_docs[doc]['vector_score'], result['score'])
            
            # BM25 检索
            bm25_results = self.bm25_search(query, top_k=top_k)
            for result in bm25_results:
                doc = result['content']
                if doc not in all_docs:
                    all_docs[doc] = {'vector_score': 0, 'bm25_score': 0}
                all_docs[doc]['bm25_score'] = max(all_docs[doc]['bm25_score'], result['score'])
        
        # RRF 融合
        k = 60
        doc_scores = {}
        for doc, scores in all_docs.items():
            # 归一化并融合
            rrf_score = 0
            if scores['vector_score'] > 0:
                rrf_score += 1.0 / (k + 1)  # 向量结果的 rank
            if scores['bm25_score'] > 0:
                rrf_score += 1.0 / (k + 1)  # BM25 结果的 rank
            doc_scores[doc] = rrf_score
        
        # 排序
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
    
    def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict]:
        """重排序"""
        if not documents:
            return []
        
        if self.reranker is None:
            return [{
                'content': doc,
                'score': 1.0 - (i * 0.1),
                'rank': i + 1,
                'source': 'fallback'
            } for i, doc in enumerate(documents[:top_k])]
        
        pairs = [[query, doc] for doc in documents]
        scores = self.reranker.compute_score(pairs)
        
        if not isinstance(scores, list):
            scores = [scores]
        
        # 辅助函数：安全地转换 score 为 float
        def safe_float(score):
            # 处理 numpy 数组
            if hasattr(score, 'flatten'):
                flat = score.flatten()
                return float(flat[0]) if len(flat) > 0 else 0.0
            elif hasattr(score, 'item'):
                try:
                    return float(score.item())
                except (ValueError, TypeError):
                    # 如果 item() 失败，尝试直接索引
                    return float(score[0]) if hasattr(score, '__getitem__') else 0.0
            elif hasattr(score, '__float__'):
                return float(score)
            elif isinstance(score, (list, tuple)) and len(score) > 0:
                return float(score[0])
            else:
                return float(score)
        
        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: safe_float(x[1]), reverse=True)
        
        results = []
        for i, (doc, score) in enumerate(doc_score_pairs[:top_k]):
            score_val = safe_float(score)
            
            results.append({
                'content': doc,
                'score': score_val,
                'rank': i + 1,
                'source': 'reranker'
            })
        
        return results
    
    def generate(
        self,
        query: str,
        use_query_rewrite: bool = True,
        retrieval_top_k: int = 20,
        final_top_k: int = 3,
        verbose: bool = True
    ) -> Dict:
        """执行完整的 Advanced RAG v2 流程"""
        if verbose:
            print("\n" + "=" * 60)
            print(f"查询: {query}")
            print("=" * 60)
        
        # 1. Query Rewrite
        if use_query_rewrite:
            if verbose:
                print("\n[步骤 1] Query Rewrite...")
            queries = self.query_rewriter.rewrite(query, strategy="expand")
            if verbose:
                print(f"✓ 生成 {len(queries)} 个查询变体:")
                for i, q in enumerate(queries):
                    print(f"  {i+1}. {q}")
        else:
            queries = [query]
        
        # 2. 混合检索
        if verbose:
            print(f"\n[步骤 2] 混合检索 (Vector + BM25, {len(queries)} 查询)...")
        
        hybrid_results = self.hybrid_search(queries, top_k=retrieval_top_k)
        
        if verbose:
            print(f"✓ 混合检索完成，召回 {len(hybrid_results)} 个候选文档")
        
        # 3. Reranker
        if verbose:
            print(f"\n[步骤 3] Reranker 重排序...")
        
        docs_to_rerank = [r['content'] for r in hybrid_results]
        reranked = self.rerank(query, docs_to_rerank, top_k=final_top_k)
        
        if verbose:
            print(f"✓ 重排序完成，保留 Top-{len(reranked)} 文档:")
            for doc in reranked:
                print(f"  - [排名 {doc['rank']}] 相关度: {doc['score']:.4f}")
                print(f"    {doc['content'][:80]}...")
        
        # 4. 构建增强提示词
        if verbose:
            print("\n[步骤 4] 构建增强提示词 (Few-shot + CoT)...")
        
        prompt = self.prompt_builder.build(query, reranked)
        
        if verbose:
            print(f"✓ 提示词构建完成，长度: {len(prompt)} 字符")
        
        # 5. vLLM 生成
        if verbose:
            print("\n[步骤 5] vLLM 生成答案...")
        
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
            'rewritten_queries': queries,
            'answer': answer,
            'retrieved_docs': reranked,
            'prompt': prompt,
            'num_docs': len(reranked)
        }


def main():
    """测试 Advanced RAG v2"""
    rag = AdvancedRAGv2()
    
    test_queries = [
        "莆田话中'吃'怎么说？",
        "食的发音",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*80}")
        print(f"测试 {i}/{len(test_queries)}")
        print(f"{'='*80}")
        
        result = rag.generate(
            query=query,
            use_query_rewrite=True,
            retrieval_top_k=15,
            final_top_k=3,
            verbose=True
        )
        
        if i < len(test_queries):
            input("\n按回车继续...")


if __name__ == "__main__":
    main()
