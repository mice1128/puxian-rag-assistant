#!/usr/bin/env python3
"""
推理引擎性能对比测试
"""
import sys
import os
import json
import argparse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from inference_engine import TransformersEngine, VLLMEngine
from inference_engine.config import InferenceConfig


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def compare_engines(config: InferenceConfig, test_prompts: list, num_runs: int = 3):
    """对比两种推理引擎"""
    print_section("🔬 推理引擎性能对比测试")
    
    print(f"\n配置:")
    print(f"  模型: {config.model_path}")
    print(f"  GPU: {config.gpu_id}")
    print(f"  测试提示词数: {len(test_prompts)}")
    print(f"  每个提示词运行次数: {num_runs}")
    
    results = {}
    
    # 测试 Transformers 引擎
    print_section("1️⃣  Transformers 原生引擎")
    try:
        tf_engine = TransformersEngine(config)
        tf_engine.load_model()
        
        tf_results = tf_engine.benchmark(test_prompts, num_runs=num_runs, warmup=True)
        results['transformers'] = tf_results
        
        print(f"\n总体性能:")
        print(f"  平均延迟: {tf_results['overall_avg_latency']:.3f}s")
        print(f"  平均吞吐: {tf_results['overall_avg_throughput']:.1f} tokens/s")
        
    except Exception as e:
        print(f"❌ Transformers 引擎测试失败: {e}")
        results['transformers'] = {'error': str(e)}
    
    # 测试 vLLM 引擎
    print_section("2️⃣  vLLM 优化引擎")
    try:
        vllm_engine = VLLMEngine(config)
        vllm_engine.load_model()
        
        vllm_results = vllm_engine.benchmark(test_prompts, num_runs=num_runs, warmup=True)
        results['vllm'] = vllm_results
        
        print(f"\n总体性能:")
        print(f"  平均延迟: {vllm_results['overall_avg_latency']:.3f}s")
        print(f"  平均吞吐: {vllm_results['overall_avg_throughput']:.1f} tokens/s")
        
    except Exception as e:
        print(f"❌ vLLM 引擎测试失败: {e}")
        print(f"   提示: 请先安装 vLLM: pip install vllm")
        results['vllm'] = {'error': str(e)}
    
    # 性能对比
    if 'error' not in results.get('transformers', {}) and 'error' not in results.get('vllm', {}):
        print_section("📊 性能对比总结")
        
        tf_latency = results['transformers']['overall_avg_latency']
        vllm_latency = results['vllm']['overall_avg_latency']
        
        tf_throughput = results['transformers']['overall_avg_throughput']
        vllm_throughput = results['vllm']['overall_avg_throughput']
        
        latency_speedup = tf_latency / vllm_latency if vllm_latency > 0 else 0
        throughput_speedup = vllm_throughput / tf_throughput if tf_throughput > 0 else 0
        
        print(f"\n延迟对比:")
        print(f"  Transformers: {tf_latency:.3f}s")
        print(f"  vLLM:         {vllm_latency:.3f}s")
        print(f"  加速比:       {latency_speedup:.2f}x 🚀")
        
        print(f"\n吞吐量对比:")
        print(f"  Transformers: {tf_throughput:.1f} tokens/s")
        print(f"  vLLM:         {vllm_throughput:.1f} tokens/s")
        print(f"  提升比:       {throughput_speedup:.2f}x 🚀")
        
        results['comparison'] = {
            'latency_speedup': round(latency_speedup, 2),
            'throughput_speedup': round(throughput_speedup, 2),
            'vllm_faster': vllm_latency < tf_latency
        }
    
    return results


def test_batch_performance(config: InferenceConfig):
    """测试批处理性能"""
    print_section("📦 批处理性能测试")
    
    batch_sizes = [1, 4, 8, 16]
    test_prompt = "莆仙话中祭祀怎么说？请详细解释。"
    
    print(f"\n测试提示词: {test_prompt[:50]}...")
    print(f"批量大小: {batch_sizes}")
    
    results = {}
    
    # 测试 vLLM 批处理
    try:
        print("\n🚀 vLLM 批处理测试:")
        vllm_engine = VLLMEngine(config)
        vllm_engine.load_model()
        
        for batch_size in batch_sizes:
            prompts = [test_prompt] * batch_size
            
            import time
            start = time.time()
            outputs = vllm_engine.batch_generate(prompts)
            elapsed = time.time() - start
            
            total_tokens = sum(o['tokens'] for o in outputs)
            throughput = total_tokens / elapsed if elapsed > 0 else 0
            
            print(f"  Batch {batch_size:2d}: {elapsed:.3f}s, {throughput:.1f} tokens/s")
            
            results[f'vllm_batch_{batch_size}'] = {
                'batch_size': batch_size,
                'latency': round(elapsed, 3),
                'throughput': round(throughput, 1)
            }
        
    except Exception as e:
        print(f"❌ vLLM 批处理测试失败: {e}")
    
    return results


def save_results(results: dict, output_file: str = None):
    """保存测试结果"""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"inference_benchmark_{timestamp}.json"
    
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'results': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存: {output_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='推理引擎性能对比')
    parser.add_argument('--model-path', default='/home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4', help='模型路径')
    parser.add_argument('--gpu-id', type=int, default=1, help='GPU ID')
    parser.add_argument('--num-runs', type=int, default=3, help='每个测试运行次数')
    parser.add_argument('--batch-test', action='store_true', help='运行批处理测试')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    # 创建配置
    config = InferenceConfig(
        model_path=args.model_path,
        gpu_id=args.gpu_id,
        max_tokens=256,  # 测试时使用较短的 token 数
    )
    
    # 测试提示词
    test_prompts = [
        "莆仙话中祭祀怎么说？",
        "莆仙话的‘厝’是什么意思？",
        "如何用莆仙话说’吃饭’？",
        "莆仙话中表示‘漂亮’的词有哪些？",
        "莆仙话和闽南话有什么区别？",
    ]
    
    # 运行对比测试
    results = compare_engines(config, test_prompts, num_runs=args.num_runs)
    
    # 批处理测试
    if args.batch_test:
        batch_results = test_batch_performance(config)
        results['batch_performance'] = batch_results
    
    # 保存结果
    save_results(results, args.output)
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
