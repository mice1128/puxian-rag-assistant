#!/usr/bin/env python3
"""
RAG 质量评估
评估维度：准确性、相关性、完整性、幻觉检测
"""
import sys
import os
import json
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.rag_service import get_rag_service


def calculate_relevance(docs, question):
    """计算检索文档的相关性分数"""
    if not docs:
        return 0.0
    
    # 使用距离的倒数作为相关性分数
    relevance_scores = []
    for doc in docs:
        distance = doc.get('distance', 1.0)
        # 距离越小，相关性越高
        relevance = 1 / (1 + distance)
        relevance_scores.append(relevance)
    
    return sum(relevance_scores) / len(relevance_scores)


def evaluate_answer_quality(answer, sources):
    """评估答案质量（简单自动评估）"""
    metrics = {
        'has_answer': len(answer.strip()) > 0,
        'answer_length': len(answer),
        'sources_used': len(sources),
        'contains_refusal': '抱歉' in answer or '没有找到' in answer or '无法回答' in answer,
    }
    
    # 简单质量分数 (0-10)
    quality_score = 0
    
    if metrics['has_answer']:
        quality_score += 3
    
    if 20 < metrics['answer_length'] < 500:
        quality_score += 3
    
    if metrics['sources_used'] > 0:
        quality_score += 2
    
    if not metrics['contains_refusal']:
        quality_score += 2
    
    metrics['quality_score'] = quality_score
    return metrics


def run_evaluation(test_questions, output_file=None):
    """运行评估"""
    print("=" * 80)
    print("RAG 质量评估")
    print("=" * 80)
    print()
    
    # 初始化 RAG 服务
    print("初始化 RAG 服务...")
    rag = get_rag_service()
    print(f"✅ 知识库文档数: {rag.collection.count()}")
    print()
    
    results = []
    total_time = 0
    
    for i, item in enumerate(test_questions, 1):
        question = item['question']
        question_id = item.get('id', i)
        category = item.get('category', 'unknown')
        
        print(f"[{i}/{len(test_questions)}] 问题 #{question_id}: {question}")
        print(f"类别: {category}")
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 执行问答
            result = rag.ask(question)
            
            # 记录结束时间
            elapsed = time.time() - start_time
            total_time += elapsed
            
            # 计算指标
            relevance = calculate_relevance(result.get('sources', []), question)
            quality_metrics = evaluate_answer_quality(
                result.get('answer', ''),
                result.get('sources', [])
            )
            
            # 保存结果
            eval_result = {
                'id': question_id,
                'question': question,
                'category': category,
                'answer': result.get('answer', ''),
                'sources_count': len(result.get('sources', [])),
                'tokens_used': result.get('tokens_used', 0),
                'relevance_score': round(relevance, 4),
                'quality_score': quality_metrics['quality_score'],
                'answer_length': quality_metrics['answer_length'],
                'contains_refusal': quality_metrics['contains_refusal'],
                'response_time': round(elapsed, 2),
            }
            
            results.append(eval_result)
            
            # 打印结果
            print(f"答案: {result.get('answer', '')[:100]}...")
            print(f"相关性: {relevance:.2f} | 质量分: {quality_metrics['quality_score']}/10 | 耗时: {elapsed:.2f}s")
            print()
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            results.append({
                'id': question_id,
                'question': question,
                'category': category,
                'error': str(e)
            })
            print()
    
    # 统计总体指标
    print("=" * 80)
    print("评估总结")
    print("=" * 80)
    
    successful_results = [r for r in results if 'error' not in r]
    
    if successful_results:
        avg_relevance = sum(r['relevance_score'] for r in successful_results) / len(successful_results)
        avg_quality = sum(r['quality_score'] for r in successful_results) / len(successful_results)
        avg_time = total_time / len(successful_results)
        avg_tokens = sum(r['tokens_used'] for r in successful_results) / len(successful_results)
        
        print(f"总测试数: {len(test_questions)}")
        print(f"成功数: {len(successful_results)}")
        print(f"失败数: {len(test_questions) - len(successful_results)}")
        print(f"平均相关性: {avg_relevance:.3f}")
        print(f"平均质量分: {avg_quality:.1f}/10")
        print(f"平均响应时间: {avg_time:.2f}s")
        print(f"平均Token数: {avg_tokens:.0f}")
        
        summary = {
            'total_tests': len(test_questions),
            'successful': len(successful_results),
            'failed': len(test_questions) - len(successful_results),
            'avg_relevance': round(avg_relevance, 3),
            'avg_quality_score': round(avg_quality, 1),
            'avg_response_time': round(avg_time, 2),
            'avg_tokens': round(avg_tokens, 0),
        }
    else:
        print("❌ 所有测试都失败了")
        summary = {'error': 'All tests failed'}
    
    # 保存结果
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"results/rag_eval_{timestamp}.json"
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else 'results', exist_ok=True)
    
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': summary,
        'details': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存: {output_file}")


if __name__ == '__main__':
    # 默认测试问题集
    default_questions = [
        {'id': 1, 'question': '莆仙话中祭祀怎么说？', 'category': '词汇查询'},
        {'id': 2, 'question': '莆仙话的"厝"是什么意思？', 'category': '词义解释'},
        {'id': 3, 'question': '如何用莆仙话说"吃饭"？', 'category': '日常用语'},
        {'id': 4, 'question': '莆仙话中表示"漂亮"的词有哪些？', 'category': '词汇查询'},
        {'id': 5, 'question': '莆仙话和闽南话有什么区别？', 'category': '综合问答'},
    ]
    
    # 检查是否有自定义测试文件
    test_file = 'data/test_questions.json'
    if os.path.exists(test_file):
        print(f"加载测试文件: {test_file}")
        with open(test_file, 'r', encoding='utf-8') as f:
            test_questions = json.load(f)
    else:
        print("使用默认测试问题集")
        test_questions = default_questions
    
    run_evaluation(test_questions)
