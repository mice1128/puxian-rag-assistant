#!/usr/bin/env python3
"""
推理引擎抽象基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time


class BaseInferenceEngine(ABC):
    """推理引擎抽象基类"""
    
    def __init__(self, config):
        """初始化推理引擎"""
        self.config = config
        self.model = None
        self.is_loaded = False
        
    @abstractmethod
    def load_model(self):
        """加载模型"""
        pass
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成文本
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            top_p: nucleus sampling 参数
            **kwargs: 其他生成参数
            
        Returns:
            {
                'text': 生成的文本,
                'tokens': token 数量,
                'latency': 延迟(秒),
                'throughput': 吞吐量(tokens/s)
            }
        """
        pass
    
    @abstractmethod
    def batch_generate(
        self,
        prompts: List[str],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        批量生成
        
        Args:
            prompts: 输入提示词列表
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            **kwargs: 其他生成参数
            
        Returns:
            生成结果列表
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            'model_path': self.config.model_path,
            'gpu_id': self.config.gpu_id,
            'is_loaded': self.is_loaded,
            'backend': self.__class__.__name__,
        }
    
    def warmup(self, num_iterations: int = 3):
        """预热模型"""
        print(f"🔥 预热模型 ({num_iterations} 次)...")
        warmup_prompt = "你好"
        
        for i in range(num_iterations):
            self.generate(warmup_prompt, max_tokens=10)
            print(f"  预热 {i+1}/{num_iterations} 完成")
        
        print("✅ 预热完成")
    
    def benchmark(
        self,
        prompts: List[str],
        num_runs: int = 3,
        warmup: bool = True
    ) -> Dict[str, Any]:
        """
        性能基准测试
        
        Args:
            prompts: 测试提示词列表
            num_runs: 每个提示词运行次数
            warmup: 是否预热
            
        Returns:
            性能指标统计
        """
        if warmup and num_runs > 0:
            self.warmup()
        
        results = []
        
        for prompt in prompts:
            prompt_results = []
            
            for run in range(num_runs):
                result = self.generate(prompt)
                prompt_results.append(result)
            
            # 计算平均指标
            avg_latency = sum(r['latency'] for r in prompt_results) / len(prompt_results)
            avg_throughput = sum(r['throughput'] for r in prompt_results) / len(prompt_results)
            
            results.append({
                'prompt': prompt[:50] + '...' if len(prompt) > 50 else prompt,
                'avg_latency': round(avg_latency, 3),
                'avg_throughput': round(avg_throughput, 1),
                'runs': num_runs
            })
        
        # 总体统计
        overall_latency = sum(r['avg_latency'] for r in results) / len(results)
        overall_throughput = sum(r['avg_throughput'] for r in results) / len(results)
        
        return {
            'backend': self.__class__.__name__,
            'num_prompts': len(prompts),
            'num_runs': num_runs,
            'overall_avg_latency': round(overall_latency, 3),
            'overall_avg_throughput': round(overall_throughput, 1),
            'details': results
        }
