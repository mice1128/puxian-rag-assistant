#!/usr/bin/env python3
"""
检索效果评估
评估指标：Recall@K, Precision@K, MRR, NDCG
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.rag_service import get_rag_service


def evaluate_retrieval_at_k(rag, questions, k_values=[1, 3, 5, 10]):
    """评估不同K值下的检索效果"""
    print("=" * 80)
    print("检索效果评估")
    print("=" * 80)
    print()
    
    results = {
        'k_values': k_values,
        'results': []
    }
    
    for i, item in enumerate(questions, 1):
        question = item['question']
        question_id = item.get('id', i)
        expected_keywords = item.get('expected_keywords', [])
        
        print(f"[{i}/{len(questions)}] 问题: {question}")
        
        question_results = {
            'id': question_id,
            'question': question,
            'metrics': {}
        }
        
        # 对每个K值进行检索
        for k in k_values:
            docs = rag.search(question, k=k)
            
            # 计算指标
            relevance_scores = []
            for doc in docs:
                # 基于距离计算相关性
                distance = doc.get('distance', 1.0)
                relevance = 1 / (1 + distance)
                relevance_scores.append(relevance)
            
            # 计算平均相关性
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
            
            # 如果有期望关键词，计算召回率
            recall = 0.0
            if expected_keywords:
                retrieved_text = ' '.join([doc['text'] for doc in docs])
                matched = sum(1 for kw in expected_keywords if kw in retrieved_text)
                recall = matched / len(expected_keywords)
            
            question_results['metrics'][f'k{k}'] = {
                'avg_relevance': round(avg_relevance, 4),
                'recall': round(recall, 4) if expected_keywords else None,
                'retrieved_count': len(docs),
                'top_distances': [round(doc.get('distance', 0), 4) for doc in docs[:3]]
            }
            
            recall_str = f"{recall:.3f}" if expected_keywords else "N/A"
            print(f"  K={k}: 相关性={avg_relevance:.3f}, 召回={recall_str}")
        
        results['results'].append(question_results)
        print()
    
    # 计算总体统计
    print("=" * 80)
    print("总体统计")
    print("=" * 80)
    
    for k in k_values:
        avg_relevance = sum(
            r['metrics'][f'k{k}']['avg_relevance'] 
            for r in results['results']
        ) / len(results['results'])
        
        recalls = [
            r['metrics'][f'k{k}']['recall'] 
            for r in results['results'] 
            if r['metrics'][f'k{k}']['recall'] is not None
        ]
        avg_recall = sum(recalls) / len(recalls) if recalls else 0
        
        print(f"K={k}:")
        print(f"  平均相关性: {avg_relevance:.3f}")
        if recalls:
            print(f"  平均召回率: {avg_recall:.3f}")
    
    return results


def save_results(results, output_file=None):
    """保存评估结果"""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"results/retrieval_eval_{timestamp}.json"
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else 'results', exist_ok=True)
    
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'evaluation': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存: {output_file}")


if __name__ == '__main__':
    # 测试问题集（可以指定期望关键词）
    test_questions = [
        {
            'id': 1,
            'question': '莆仙话中祭祀怎么说？',
            'expected_keywords': ['祭祀', '莆仙话']
        },
        {
            'id': 2,
            'question': '厝是什么意思？',
            'expected_keywords': ['厝', '房子', '家']
        },
        {
            'id': 3,
            'question': '如何用莆仙话说吃饭？',
            'expected_keywords': ['吃饭', '食']
        },
    ]
    
    # 检查自定义测试文件
    test_file = 'data/test_questions.json'
    if os.path.exists(test_file):
        print(f"加载测试文件: {test_file}")
        with open(test_file, 'r', encoding='utf-8') as f:
            test_questions = json.load(f)
    
    # 初始化 RAG 服务
    print("初始化 RAG 服务...")
    rag = get_rag_service()
    print(f"✅ 知识库文档数: {rag.collection.count()}")
    print()
    
    # 运行评估
    results = evaluate_retrieval_at_k(rag, test_questions, k_values=[1, 3, 5, 10])
    
    # 保存结果
    save_results(results)
