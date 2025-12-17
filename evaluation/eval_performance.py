#!/usr/bin/env python3
"""
性能评估
评估维度：推理速度、显存占用、延迟、吞吐量
"""
import sys
import os
import json
import time
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.rag_service import get_rag_service


def get_gpu_memory():
    """获取GPU显存使用情况 (MB)"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits', '--id=1'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            used, total = result.stdout.strip().split(',')
            return {'used': int(used), 'total': int(total)}
    except:
        pass
    return {'used': 0, 'total': 0}


def measure_performance(rag, question, num_runs=3):
    """测量单个问题的性能指标"""
    print(f"测试问题: {question}")
    
    # 记录初始显存
    initial_memory = get_gpu_memory()
    print(f"初始显存: {initial_memory['used']} MB")
    
    latencies = []
    tokens_per_second = []
    peak_memory = initial_memory['used']
    
    for run in range(num_runs):
        print(f"  运行 {run + 1}/{num_runs}...", end=' ')
        
        start_time = time.time()
        result = rag.ask(question)
        end_time = time.time()
        
        latency = end_time - start_time
        tokens = result.get('tokens_used', 0)
        tps = tokens / latency if latency > 0 else 0
        
        latencies.append(latency)
        tokens_per_second.append(tps)
        
        # 检查显存峰值
        current_memory = get_gpu_memory()
        peak_memory = max(peak_memory, current_memory['used'])
        
        print(f"延迟={latency:.2f}s, TPS={tps:.1f}, 显存={current_memory['used']}MB")
    
    # 计算平均值
    avg_latency = sum(latencies) / len(latencies)
    avg_tps = sum(tokens_per_second) / len(tokens_per_second)
    memory_delta = peak_memory - initial_memory['used']
    
    return {
        'avg_latency': round(avg_latency, 2),
        'min_latency': round(min(latencies), 2),
        'max_latency': round(max(latencies), 2),
        'avg_tps': round(avg_tps, 1),
        'peak_memory_mb': peak_memory,
        'memory_delta_mb': memory_delta,
        'num_runs': num_runs
    }


def run_performance_test(test_questions, num_runs=3):
    """运行性能测试"""
    print("=" * 80)
    print("性能评估测试")
    print("=" * 80)
    print()
    
    # 初始化 RAG
    print("初始化 RAG 服务...")
    rag = get_rag_service()
    print(f"✅ 知识库文档数: {rag.collection.count()}")
    print()
    
    # 预热（首次加载模型）
    print("预热模型...")
    rag.ask("测试")
    print("✅ 预热完成")
    print()
    
    results = []
    
    for i, item in enumerate(test_questions, 1):
        question = item['question']
        question_id = item.get('id', i)
        
        print(f"\n[{i}/{len(test_questions)}] 问题 #{question_id}")
        print("-" * 80)
        
        try:
            metrics = measure_performance(rag, question, num_runs)
            
            result = {
                'id': question_id,
                'question': question,
                'performance': metrics
            }
            results.append(result)
            
            print(f"\n总结:")
            print(f"  平均延迟: {metrics['avg_latency']}s")
            print(f"  平均速度: {metrics['avg_tps']} tokens/s")
            print(f"  显存峰值: {metrics['peak_memory_mb']} MB")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            results.append({
                'id': question_id,
                'question': question,
                'error': str(e)
            })
    
    # 总体统计
    print("\n" + "=" * 80)
    print("总体性能统计")
    print("=" * 80)
    
    successful = [r for r in results if 'error' not in r]
    
    if successful:
        avg_latency = sum(r['performance']['avg_latency'] for r in successful) / len(successful)
        avg_tps = sum(r['performance']['avg_tps'] for r in successful) / len(successful)
        max_memory = max(r['performance']['peak_memory_mb'] for r in successful)
        
        print(f"测试问题数: {len(test_questions)}")
        print(f"成功数: {len(successful)}")
        print(f"平均延迟: {avg_latency:.2f}s")
        print(f"平均速度: {avg_tps:.1f} tokens/s")
        print(f"显存峰值: {max_memory} MB")
        
        summary = {
            'total_tests': len(test_questions),
            'successful': len(successful),
            'avg_latency': round(avg_latency, 2),
            'avg_tps': round(avg_tps, 1),
            'peak_memory_mb': max_memory
        }
    else:
        summary = {'error': 'All tests failed'}
    
    return {'summary': summary, 'details': results}


def save_results(results, output_file=None):
    """保存评估结果"""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"results/performance_eval_{timestamp}.json"
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else 'results', exist_ok=True)
    
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'results': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存: {output_file}")


if __name__ == '__main__':
    # 测试问题
    test_questions = [
        {'id': 1, 'question': '莆仙话中祭祀怎么说？'},
        {'id': 2, 'question': '莆仙话的"厝"是什么意思？'},
        {'id': 3, 'question': '如何用莆仙话说"吃饭"？'},
    ]
    
    # 检查自定义测试文件
    test_file = 'data/test_questions.json'
    if os.path.exists(test_file):
        print(f"加载测试文件: {test_file}")
        with open(test_file, 'r', encoding='utf-8') as f:
            test_questions = json.load(f)
    
    # 运行测试（每个问题运行3次）
    results = run_performance_test(test_questions, num_runs=3)
    
    # 保存结果
    save_results(results)
