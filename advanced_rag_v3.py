"""
Advanced RAG v3 - 智能自适应 + 可靠性增强
核心特性:
1. QueryClassifier - 智能查询分类
2. AdaptiveRetriever - 自适应检索策略
3. AnswerValidator - 答案验证与引用
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vllm_service import get_vllm_service
import chromadb
from typing import List, Dict, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
import jieba
import re


class QueryClassifier:
    """查询分类器 - 识别查询意图"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    def classify(self, query: str) -> Dict:
        """
        分类查询类型
        
        返回:
            {
                'type': 'factual' | 'example' | 'comparison' | 'context',
                'confidence': 0.0-1.0
            }
        """
        # 先用规则快速判断
        rule_based = self._rule_based_classify(query)
        if rule_based['confidence'] > 0.9:
            return rule_based
        
        # 规则不确定时，使用 LLM 分类
        return self._llm_based_classify(query)
    
    def _rule_based_classify(self, query: str) -> Dict:
        """基于规则的快速分类"""
        query_lower = query.lower()
        
        # 事实查询 (factual): 直接询问发音、词汇
        factual_patterns = [
            r'怎么说', r'怎么读', r'怎么念', r'发音', r'读音',
            r'是什么', r'叫什么', r'怎么写'
        ]
        for pattern in factual_patterns:
            if re.search(pattern, query):
                return {'type': 'factual', 'confidence': 0.95}
        
        # 例句查询 (example): 询问用法、例句
        example_patterns = [
            r'怎么用', r'用法', r'例句', r'举例', r'造句',
            r'怎么表达', r'如何说', r'怎样说'
        ]
        for pattern in example_patterns:
            if re.search(pattern, query):
                return {'type': 'example', 'confidence': 0.95}
        
        # 对比查询 (comparison): 询问区别、对比
        comparison_patterns = [
            r'区别', r'不同', r'差异', r'对比', r'相同',
            r'和.*的关系', r'跟.*比'
        ]
        for pattern in comparison_patterns:
            if re.search(pattern, query):
                return {'type': 'comparison', 'confidence': 0.95}
        
        # 背景查询 (context): 询问原因、历史、背景
        context_patterns = [
            r'为什么', r'怎么来的', r'起源', r'历史', r'背景',
            r'由来', r'典故'
        ]
        for pattern in context_patterns:
            if re.search(pattern, query):
                return {'type': 'context', 'confidence': 0.95}
        
        # 默认为事实查询
        return {'type': 'factual', 'confidence': 0.5}
    
    def _llm_based_classify(self, query: str) -> Dict:
        """基于 LLM 的精确分类"""
        prompt = f"""请判断以下问题属于哪种类型，只返回类型名称：

类型说明：
- factual: 询问事实，如发音、词汇、定义
- example: 询问用法、例句、表达方式
- comparison: 询问区别、对比、差异
- context: 询问背景、原因、历史

问题：{query}

类型（只返回 factual/example/comparison/context 中的一个）："""

        try:
            response = self.llm_service.generate(
                prompt=prompt,
                max_tokens=10,
                temperature=0.1
            ).strip().lower()
            
            # 提取类型
            if 'factual' in response:
                return {'type': 'factual', 'confidence': 0.85}
            elif 'example' in response:
                return {'type': 'example', 'confidence': 0.85}
            elif 'comparison' in response:
                return {'type': 'comparison', 'confidence': 0.85}
            elif 'context' in response:
                return {'type': 'context', 'confidence': 0.85}
        except:
            pass
        
        # LLM 失败，返回默认
        return {'type': 'factual', 'confidence': 0.5}


class AdaptiveRetriever:
    """自适应检索器 - 根据查询类型调整策略"""
    
    # 不同查询类型的检索策略
    STRATEGIES = {
        'factual': {
            'retrieval_top_k': 10,
            'rerank_top_k': 2,
            'use_query_rewrite': False,
            'temperature': 0.3,
            'description': '高精度检索，直接给出准确答案'
        },
        'example': {
            'retrieval_top_k': 20,
            'rerank_top_k': 5,
            'use_query_rewrite': True,
            'temperature': 0.7,
            'description': '高召回检索，提供丰富例句'
        },
        'comparison': {
            'retrieval_top_k': 15,
            'rerank_top_k': 4,
            'use_query_rewrite': True,
            'temperature': 0.5,
            'description': '多角度检索，全面对比分析'
        },
        'context': {
            'retrieval_top_k': 12,
            'rerank_top_k': 3,
            'use_query_rewrite': True,
            'temperature': 0.6,
            'description': '背景检索，补充文化历史'
        }
    }
    
    @classmethod
    def get_strategy(cls, query_type: str) -> Dict:
        """获取检索策略"""
        return cls.STRATEGIES.get(query_type, cls.STRATEGIES['factual'])


class AnswerValidator:
    """答案验证器 - 评估可靠性并添加引用"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    def validate(self, query: str, answer: str, retrieved_docs: List[Dict]) -> Dict:
        """
        验证答案并添加引用
        
        返回:
            {
                'answer': str,  # 带引用的答案
                'confidence': float,  # 置信度 0-1
                'citations': List[str],  # 引用来源
                'warning': str  # 警告信息（如果有）
            }
        """
        # 1. 检查是否有检索文档
        if not retrieved_docs or len(retrieved_docs) == 0:
            return {
                'answer': "抱歉，我在知识库中没有找到相关信息。建议您查阅专业的莆田话词典或咨询当地语言专家。",
                'confidence': 0.0,
                'citations': [],
                'warning': '未找到相关文档'
            }
        
        # 2. 一致性检查
        consistency_score = self._check_consistency(answer, retrieved_docs)
        
        # 3. 添加引用
        answer_with_citations, citations = self._add_citations(answer, retrieved_docs)
        
        # 4. 生成警告
        warning = None
        if consistency_score < 0.5:
            warning = '此答案置信度较低，建议仔细核对'
            answer_with_citations = f"⚠️ 注意：{warning}\n\n{answer_with_citations}"
        elif consistency_score < 0.7:
            warning = '此答案可能不完全准确'
        
        return {
            'answer': answer_with_citations,
            'confidence': consistency_score,
            'citations': citations,
            'warning': warning
        }
    
    def _check_consistency(self, answer: str, docs: List[Dict]) -> float:
        """
        检查答案与检索文档的一致性
        
        简化版本：基于关键词重叠度
        """
        # 提取答案中的关键词
        answer_tokens = set(jieba.cut(answer))
        
        # 计算与每个文档的重叠度
        overlaps = []
        for doc in docs:
            doc_tokens = set(jieba.cut(doc['content']))
            if len(doc_tokens) > 0:
                overlap = len(answer_tokens & doc_tokens) / len(doc_tokens)
                overlaps.append(overlap)
        
        # 返回平均重叠度
        if overlaps:
            return min(sum(overlaps) / len(overlaps) * 2, 1.0)  # 放大后限制在1.0
        return 0.5  # 默认中等置信度
    
    def _add_citations(self, answer: str, docs: List[Dict]) -> Tuple[str, List[str]]:
        """
        为答案添加引用标注
        
        简化版本：在答案末尾添加参考文档
        """
        citations = []
        for i, doc in enumerate(docs[:3], 1):  # 最多引用3个文档
            # 提取文档关键信息
            content = doc['content']
            citation = f"[{i}] {content[:80]}..."
            citations.append(citation)
        
        # 构建带引用的答案
        if citations:
            citation_text = "\n\n📚 参考来源：\n" + "\n".join(citations)
            return answer + citation_text, citations
        
        return answer, []


class AdvancedRAGv3:
    """Advanced RAG v3 - 智能自适应 + 可靠性增强"""
    
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
        print("初始化 Advanced RAG v3 系统")
        print("特性: 智能自适应 + 可靠性增强")
        print("=" * 60)
        
        # 1. Embedding
        print("\n[1/7] 加载 Embedding 模型...")
        self.embedding_service = EmbeddingService(model_path=embedding_model_path)
        print(f"✓ Embedding: {embedding_model_path}")
        
        # 2. ChromaDB
        print("\n[2/7] 连接向量数据库...")
        self.chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        self.collection = self.chroma_client.get_collection(name=collection_name)
        doc_count = self.collection.count()
        print(f"✓ 数据库: {collection_name} ({doc_count} 文档)")
        
        # 3. BM25
        print("\n[3/7] 构建 BM25 索引...")
        all_docs = self.collection.get(include=["documents"])
        self.all_documents = all_docs['documents']
        self.tokenized_docs = [list(jieba.cut(doc)) for doc in self.all_documents]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        print(f"✓ BM25 索引: {len(self.all_documents)} 文档")
        
        # 4. Reranker
        print("\n[4/7] 加载 Reranker...")
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
        print("\n[5/7] 连接 vLLM 服务...")
        self.llm_service = get_vllm_service(vllm_api_url)
        
        # 6. v3 新组件：智能模块
        print("\n[6/7] 初始化智能组件...")
        self.query_classifier = QueryClassifier(self.llm_service)
        self.adaptive_retriever = AdaptiveRetriever()
        self.answer_validator = AnswerValidator(self.llm_service)
        print("✓ Query Classifier, Adaptive Retriever, Answer Validator")
        
        # 7. 提示词模板
        print("\n[7/7] 加载提示词模板...")
        self.prompt_templates = self._init_prompt_templates()
        print("✓ 4 种查询类型的专用模板")
        
        print("\n" + "=" * 60)
        print("✓ Advanced RAG v3 初始化完成！")
        print("=" * 60)
    
    def _init_prompt_templates(self) -> Dict:
        """初始化不同类型的提示词模板"""
        return {
            'factual': """你是一个专业的莆田话（莆仙方言）专家助手。

# 任务
准确回答用户关于莆田话发音、词汇的问题。

# 回答要求
1. 直接给出准确的答案
2. 提供国际音标标注
3. 简洁明了，不超过100字

# 参考资料
{context}

# 用户问题
{query}

# 你的回答
""",
            'example': """你是一个专业的莆田话（莆仙方言）专家助手。

# 任务
提供莆田话词汇的实用例句和用法说明。

# 回答要求
1. 给出词汇的基本含义
2. 提供3-5个实用例句
3. 每个例句包含莆田话和普通话对照

# 参考资料
{context}

# 用户问题
{query}

# 你的回答
""",
            'comparison': """你是一个专业的莆田话（莆仙方言）专家助手。

# 任务
对比分析莆田话词汇的区别、异同或关系。

# 回答要求
1. 清晰说明对比的几个方面
2. 指出主要区别和共同点
3. 提供例句说明
4. 结构化输出，使用列表或表格

# 参考资料
{context}

# 用户问题
{query}

# 你的回答
""",
            'context': """你是一个专业的莆田话（莆仙方言）专家助手。

# 任务
解释莆田话词汇的背景、由来或文化历史。

# 回答要求
1. 说明词汇的起源或由来
2. 补充文化或历史背景
3. 说明与古汉语或其他方言的关系
4. 内容丰富，200字左右

# 参考资料
{context}

# 用户问题
{query}

# 你的回答
"""
        }
    
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
                    'rank': i + 1
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
                    'rank': len(results) + 1
                })
        
        return results
    
    def hybrid_search(self, query: str, top_k: int = 20) -> List[Dict]:
        """混合检索 + RRF"""
        # Vector + BM25
        vector_results = self.vector_search(query, top_k=top_k)
        bm25_results = self.bm25_search(query, top_k=top_k)
        
        # RRF 融合
        all_docs = {}
        k = 60
        
        for result in vector_results:
            doc = result['content']
            if doc not in all_docs:
                all_docs[doc] = 0
            all_docs[doc] += 1.0 / (k + result['rank'])
        
        for result in bm25_results:
            doc = result['content']
            if doc not in all_docs:
                all_docs[doc] = 0
            all_docs[doc] += 1.0 / (k + result['rank'])
        
        # 排序
        ranked = sorted(all_docs.items(), key=lambda x: x[1], reverse=True)
        
        return [{
            'content': doc,
            'score': score,
            'rank': i + 1
        } for i, (doc, score) in enumerate(ranked[:top_k])]
    
    def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict]:
        """重排序"""
        if not documents:
            return []
        
        if self.reranker is None:
            return [{
                'content': doc,
                'score': 1.0 - (i * 0.1),
                'rank': i + 1
            } for i, doc in enumerate(documents[:top_k])]
        
        pairs = [[query, doc] for doc in documents]
        scores = self.reranker.compute_score(pairs)
        
        if not isinstance(scores, list):
            scores = [scores]
        
        # 安全的 float 转换
        def safe_float(score):
            if hasattr(score, 'flatten'):
                flat = score.flatten()
                return float(flat[0]) if len(flat) > 0 else 0.0
            elif hasattr(score, 'item'):
                try:
                    return float(score.item())
                except (ValueError, TypeError):
                    return float(score[0]) if hasattr(score, '__getitem__') else 0.0
            elif hasattr(score, '__float__'):
                return float(score)
            elif isinstance(score, (list, tuple)) and len(score) > 0:
                return float(score[0])
            else:
                return float(score)
        
        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: safe_float(x[1]), reverse=True)
        
        return [{
            'content': doc,
            'score': safe_float(score),
            'rank': i + 1
        } for i, (doc, score) in enumerate(doc_score_pairs[:top_k])]
    
    def generate(
        self,
        query: str,
        verbose: bool = True
    ) -> Dict:
        """执行完整的 Advanced RAG v3 流程"""
        if verbose:
            print("\n" + "=" * 60)
            print(f"查询: {query}")
            print("=" * 60)
        
        # 1. 查询分类
        if verbose:
            print("\n[步骤 1] 智能查询分类...")
        
        classification = self.query_classifier.classify(query)
        query_type = classification['type']
        confidence = classification['confidence']
        
        if verbose:
            print(f"✓ 查询类型: {query_type} (置信度: {confidence:.2f})")
            print(f"  说明: {self.adaptive_retriever.get_strategy(query_type)['description']}")
        
        # 2. 获取自适应策略
        if verbose:
            print(f"\n[步骤 2] 自适应检索策略...")
        
        strategy = self.adaptive_retriever.get_strategy(query_type)
        
        if verbose:
            print(f"✓ 策略配置:")
            print(f"  - 召回文档数: {strategy['retrieval_top_k']}")
            print(f"  - 重排序保留: {strategy['rerank_top_k']}")
            print(f"  - 查询改写: {'开启' if strategy['use_query_rewrite'] else '关闭'}")
            print(f"  - 生成温度: {strategy['temperature']}")
        
        # 3. 混合检索
        if verbose:
            print(f"\n[步骤 3] 混合检索 (Vector + BM25)...")
        
        hybrid_results = self.hybrid_search(query, top_k=strategy['retrieval_top_k'])
        
        if verbose:
            print(f"✓ 召回 {len(hybrid_results)} 个候选文档")
        
        # 4. Reranker
        if verbose:
            print(f"\n[步骤 4] Reranker 重排序...")
        
        docs_to_rerank = [r['content'] for r in hybrid_results]
        reranked = self.rerank(query, docs_to_rerank, top_k=strategy['rerank_top_k'])
        
        if verbose:
            print(f"✓ 保留 Top-{len(reranked)} 文档")
        
        # 5. 构建提示词
        if verbose:
            print(f"\n[步骤 5] 构建专用提示词 ({query_type})...")
        
        context = "\n\n".join([
            f"【文档 {doc['rank']}】\n{doc['content']}"
            for doc in reranked
        ])
        
        template = self.prompt_templates[query_type]
        prompt = template.format(context=context, query=query)
        
        if verbose:
            print(f"✓ 使用 {query_type} 类型专用模板")
        
        # 6. vLLM 生成
        if verbose:
            print("\n[步骤 6] vLLM 生成答案...")
        
        answer = self.llm_service.generate(
            prompt=prompt,
            max_tokens=512,
            temperature=strategy['temperature']
        )
        
        if verbose:
            print("✓ 生成完成")
        
        # 7. 答案验证
        if verbose:
            print("\n[步骤 7] 答案验证与引用...")
        
        validation = self.answer_validator.validate(query, answer, reranked)
        
        if verbose:
            print(f"✓ 置信度: {validation['confidence']:.2f}")
            print(f"✓ 引用数: {len(validation['citations'])}")
            if validation['warning']:
                print(f"⚠ 警告: {validation['warning']}")
        
        # 8. 输出最终答案
        if verbose:
            print("\n" + "=" * 60)
            print("最终答案:")
            print("=" * 60)
            print(validation['answer'])
            print("=" * 60)
        
        return {
            'query': query,
            'query_type': query_type,
            'classification_confidence': confidence,
            'strategy': strategy,
            'answer': validation['answer'],
            'raw_answer': answer,
            'confidence': validation['confidence'],
            'citations': validation['citations'],
            'warning': validation['warning'],
            'retrieved_docs': reranked,
            'num_docs': len(reranked)
        }


def main():
    """测试 Advanced RAG v3"""
    rag = AdvancedRAGv3()
    
    test_queries = [
        "莆田话中'吃'怎么说？",  # factual
        "食字怎么用？",  # example
        "食和吃有什么区别？",  # comparison
        "为什么莆田话叫'食'而不是'吃'？",  # context
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*80}")
        print(f"测试 {i}/{len(test_queries)}")
        print(f"{'='*80}")
        
        result = rag.generate(query=query, verbose=True)
        
        if i < len(test_queries):
            input("\n按回车继续...")


if __name__ == "__main__":
    main()
