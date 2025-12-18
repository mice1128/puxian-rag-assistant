#!/usr/bin/env python3
"""
仅使用 vLLM 的推理测试脚本
- 单轮生成测试
- 可选批处理测试
- 结果输出到控制台
"""
import os
import sys
import argparse
import time
from datetime import datetime

# 添加项目根路径，便于导入 inference_engine 包
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from inference_engine import VLLMEngine
from inference_engine.config import InferenceConfig


def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def run_single_tests(engine: VLLMEngine, prompts, num_runs: int):
    print_section("🎯 单轮生成测试 (vLLM)")
    results = []
    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] {prompt[:60]}...")
        run_latencies = []
        run_tokens = []
        for r in range(num_runs):
            start = time.time()
            out = engine.generate(prompt)
            latency = time.time() - start
            run_latencies.append(latency)
            run_tokens.append(out['tokens'])
            print(f"  Run {r+1}: {latency:.3f}s, tokens={out['tokens']}, throughput={out['throughput']} tok/s")
        avg_latency = sum(run_latencies) / len(run_latencies)
        avg_tokens = sum(run_tokens) / len(run_tokens)
        results.append({
            'prompt': prompt,
            'avg_latency': round(avg_latency, 3),
            'avg_tokens': round(avg_tokens, 1),
            'throughput': round(avg_tokens / avg_latency, 1) if avg_latency > 0 else 0,
        })
    print("\n✅ 单轮生成完成")
    return results


def run_batch_tests(engine: VLLMEngine, prompt: str, batch_sizes):
    print_section("📦 批处理测试 (vLLM)")
    results = []
    for bs in batch_sizes:
        prompts = [prompt] * bs
        start = time.time()
        outputs = engine.batch_generate(prompts)
        elapsed = time.time() - start
        total_tokens = sum(o['tokens'] for o in outputs)
        throughput = total_tokens / elapsed if elapsed > 0 else 0
        print(f"Batch {bs:2d}: {elapsed:.3f}s, throughput={throughput:.1f} tok/s")
        results.append({
            'batch_size': bs,
            'latency': round(elapsed, 3),
            'throughput': round(throughput, 1),
        })
    print("\n✅ 批处理测试完成")
    return results


def main():
    parser = argparse.ArgumentParser(description="vLLM 推理测试（仅 vLLM）")
    parser.add_argument('--model-path', default='/home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4', help='模型路径')
    parser.add_argument('--gpu-id', type=int, default=1, help='GPU ID')
    parser.add_argument('--num-runs', type=int, default=2, help='每个提示词的运行次数')
    parser.add_argument('--batch-test', action='store_true', help='是否运行批处理测试')
    parser.add_argument('--max-tokens', type=int, default=256, help='生成最大 token 数')
    parser.add_argument('--temperature', type=float, default=0.7, help='生成温度')
    parser.add_argument('--top-p', type=float, default=0.9, help='top_p 设置')
    parser.add_argument('--output', help='结果保存到 JSON（可选）')
    args = parser.parse_args()

    # 配置
    config = InferenceConfig(
        model_path=args.model_path,
        gpu_id=args.gpu_id,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
    )

    # 测试提示词
    test_prompts = [
        "莆仙话中祭祀怎么说？",
        "莆仙话的‘厝’是什么意思？",
        "如何用莆仙话说‘吃饭’？",
        "莆仙话中表示‘漂亮’的词有哪些？",
    ]

    # 初始化引擎
    print_section("🚀 加载 vLLM 模型")
    engine = VLLMEngine(config)
    engine.load_model()
    print("模型信息:", engine.get_model_info())

    # 单轮测试
    single_results = run_single_tests(engine, test_prompts, num_runs=args.num_runs)

    # 批处理测试（可选）
    batch_results = None
    if args.batch_test:
        batch_results = run_batch_tests(engine, test_prompts[0], batch_sizes=[1, 4, 8, 16])

    # 可选保存结果
    if args.output:
        import json
        from datetime import datetime
        payload = {
            'timestamp': datetime.now().isoformat(),
            'single': single_results,
            'batch': batch_results,
            'config': config.to_dict(),
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 结果已保存到: {args.output}")

    print("\n" + "=" * 80)
    print("测试完成 (vLLM only)")
    print("=" * 80)


if __name__ == '__main__':
    main()
