#!/usr/bin/env python3
"""
批量测试脚本
支持多参数组合实验
"""
import sys
import os
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.rag_service import get_rag_service
from app.config import Config


def run_batch_test(test_file, param_configs, output_dir='results/batch_tests'):
    """运行批量测试"""
    print("=" * 80)
    print("批量测试")
    print("=" * 80)
    print()
    
    # 加载测试问题
    with open(test_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    print(f"加载测试问题: {len(questions)} 个")
    print(f"参数配置数: {len(param_configs)}")
    print()
    
    all_results = []
    
    for config_idx, config in enumerate(param_configs, 1):
        print(f"\n{'=' * 80}")
        print(f"配置 [{config_idx}/{len(param_configs)}]: {config}")
        print("=" * 80)
        
        # 更新配置
        if 'top_k' in config:
            Config.TOP_K = config['top_k']
        if 'temperature' in config:
            Config.TEMPERATURE = config['temperature']
        if 'max_tokens' in config:
            Config.MAX_TOKENS = config['max_tokens']
        
        # 初始化 RAG（使用新配置）
        rag = get_rag_service()
        
        config_results = {
            'config': config,
            'questions': []
        }
        
        for q_idx, item in enumerate(questions, 1):
            question = item['question']
            print(f"  [{q_idx}/{len(questions)}] {question[:50]}...")
            
            try:
                result = rag.ask(question)
                
                config_results['questions'].append({
                    'id': item.get('id', q_idx),
                    'question': question,
                    'answer': result.get('answer', ''),
                    'tokens_used': result.get('tokens_used', 0),
                    'sources_count': len(result.get('sources', []))
                })
                
                print(f"    ✅ 完成 (tokens: {result.get('tokens_used', 0)})")
                
            except Exception as e:
                print(f"    ❌ 错误: {e}")
                config_results['questions'].append({
                    'id': item.get('id', q_idx),
                    'question': question,
                    'error': str(e)
                })
        
        all_results.append(config_results)
    
    # 保存结果
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'batch_test_{timestamp}.json')
    
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'test_file': test_file,
        'num_questions': len(questions),
        'num_configs': len(param_configs),
        'results': all_results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存: {output_file}")
    
    # 打印总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    for i, config_result in enumerate(all_results, 1):
        successful = sum(1 for q in config_result['questions'] if 'error' not in q)
        print(f"配置 {i}: {config_result['config']}")
        print(f"  成功: {successful}/{len(questions)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量测试脚本')
    parser.add_argument('--test-file', default='data/test_questions.json', help='测试问题文件')
    parser.add_argument('--output-dir', default='results/batch_tests', help='输出目录')
    
    args = parser.parse_args()
    
    # 定义参数组合
    param_configs = [
        {'top_k': 3, 'temperature': 0.7, 'max_tokens': 512},
        {'top_k': 5, 'temperature': 0.7, 'max_tokens': 512},
        {'top_k': 3, 'temperature': 0.5, 'max_tokens': 512},
        {'top_k': 3, 'temperature': 1.0, 'max_tokens': 512},
        {'top_k': 3, 'temperature': 0.7, 'max_tokens': 256},
    ]
    
    run_batch_test(args.test_file, param_configs, args.output_dir)
