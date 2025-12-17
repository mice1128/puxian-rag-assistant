#!/usr/bin/env python3
"""
评估结果分析与可视化
"""
import os
import json
import argparse
from datetime import datetime
from collections import defaultdict


def load_results(result_dir):
    """加载所有评估结果"""
    results = {
        'rag_quality': [],
        'retrieval': [],
        'performance': [],
        'batch_tests': []
    }
    
    for filename in os.listdir(result_dir):
        filepath = os.path.join(result_dir, filename)
        
        if not filename.endswith('.json'):
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'rag_eval' in filename:
            results['rag_quality'].append(data)
        elif 'retrieval_eval' in filename:
            results['retrieval'].append(data)
        elif 'performance_eval' in filename:
            results['performance'].append(data)
        elif 'batch_test' in filename:
            results['batch_tests'].append(data)
    
    return results


def analyze_rag_quality(data_list):
    """分析RAG质量评估结果"""
    if not data_list:
        return None
    
    print("\n" + "=" * 80)
    print("RAG 质量分析")
    print("=" * 80)
    
    for data in data_list:
        timestamp = data.get('timestamp', 'unknown')
        summary = data.get('summary', {})
        
        print(f"\n时间: {timestamp}")
        print(f"总测试数: {summary.get('total_tests', 0)}")
        print(f"成功数: {summary.get('successful', 0)}")
        print(f"平均相关性: {summary.get('avg_relevance', 0):.3f}")
        print(f"平均质量分: {summary.get('avg_quality_score', 0):.1f}/10")
        print(f"平均响应时间: {summary.get('avg_response_time', 0):.2f}s")
    
    return data_list


def analyze_retrieval(data_list):
    """分析检索效果评估结果"""
    if not data_list:
        return None
    
    print("\n" + "=" * 80)
    print("检索效果分析")
    print("=" * 80)
    
    for data in data_list:
        timestamp = data.get('timestamp', 'unknown')
        evaluation = data.get('evaluation', {})
        
        print(f"\n时间: {timestamp}")
        print(f"K值: {evaluation.get('k_values', [])}")
        
        # 计算不同K值的平均指标
        if 'results' in evaluation:
            for k in evaluation.get('k_values', []):
                relevances = []
                recalls = []
                
                for result in evaluation['results']:
                    metrics = result.get('metrics', {}).get(f'k{k}', {})
                    relevances.append(metrics.get('avg_relevance', 0))
                    if metrics.get('recall') is not None:
                        recalls.append(metrics.get('recall', 0))
                
                avg_rel = sum(relevances) / len(relevances) if relevances else 0
                avg_rec = sum(recalls) / len(recalls) if recalls else 0
                
                print(f"  K={k}: 相关性={avg_rel:.3f}, 召回率={avg_rec:.3f}")
    
    return data_list


def analyze_performance(data_list):
    """分析性能评估结果"""
    if not data_list:
        return None
    
    print("\n" + "=" * 80)
    print("性能分析")
    print("=" * 80)
    
    for data in data_list:
        timestamp = data.get('timestamp', 'unknown')
        summary = data.get('results', {}).get('summary', {})
        
        print(f"\n时间: {timestamp}")
        print(f"平均延迟: {summary.get('avg_latency', 0):.2f}s")
        print(f"平均速度: {summary.get('avg_tps', 0):.1f} tokens/s")
        print(f"显存峰值: {summary.get('peak_memory_mb', 0)} MB")
    
    return data_list


def analyze_batch_tests(data_list):
    """分析批量测试结果"""
    if not data_list:
        return None
    
    print("\n" + "=" * 80)
    print("批量测试分析")
    print("=" * 80)
    
    for data in data_list:
        timestamp = data.get('timestamp', 'unknown')
        num_configs = data.get('num_configs', 0)
        num_questions = data.get('num_questions', 0)
        
        print(f"\n时间: {timestamp}")
        print(f"配置数: {num_configs}")
        print(f"问题数: {num_questions}")
        
        for i, config_result in enumerate(data.get('results', []), 1):
            config = config_result.get('config', {})
            questions = config_result.get('questions', [])
            successful = sum(1 for q in questions if 'error' not in q)
            
            print(f"\n  配置 {i}: {config}")
            print(f"    成功率: {successful}/{len(questions)}")
    
    return data_list


def generate_report(results, output_file):
    """生成评估报告"""
    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'rag_quality_tests': len(results['rag_quality']),
            'retrieval_tests': len(results['retrieval']),
            'performance_tests': len(results['performance']),
            'batch_tests': len(results['batch_tests'])
        },
        'recommendations': []
    }
    
    # 添加建议
    if results['rag_quality']:
        latest = results['rag_quality'][-1]
        avg_quality = latest.get('summary', {}).get('avg_quality_score', 0)
        
        if avg_quality < 6:
            report['recommendations'].append(
                "RAG质量分数较低，建议增加检索文档数(TOP_K)或优化知识库内容"
            )
    
    if results['performance']:
        latest = results['performance'][-1]
        avg_tps = latest.get('results', {}).get('summary', {}).get('avg_tps', 0)
        
        if avg_tps < 10:
            report['recommendations'].append(
                "推理速度较慢，建议检查GPU利用率或考虑更小的模型"
            )
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: {output_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='分析评估结果')
    parser.add_argument('--result-dir', default='results', help='结果目录')
    parser.add_argument('--output', default='results/analysis_report.json', help='输出报告')
    
    args = parser.parse_args()
    
    # 加载结果
    print(f"加载结果目录: {args.result_dir}")
    results = load_results(args.result_dir)
    
    # 分析各项指标
    analyze_rag_quality(results['rag_quality'])
    analyze_retrieval(results['retrieval'])
    analyze_performance(results['performance'])
    analyze_batch_tests(results['batch_tests'])
    
    # 生成报告
    generate_report(results, args.output)
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)
