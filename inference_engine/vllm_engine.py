#!/usr/bin/env python3
"""
vLLM 推理引擎
高性能推理优化：PagedAttention, Continuous Batching, 优化 CUDA kernels
"""
import time
from typing import List, Dict, Any, Optional
import logging

from .base_engine import BaseInferenceEngine
from .config import InferenceConfig

logger = logging.getLogger(__name__)


class VLLMEngine(BaseInferenceEngine):
    """vLLM 推理引擎"""
    
    def __init__(self, config: InferenceConfig):
        super().__init__(config)
        self.llm = None
        self.sampling_params = None
    
    def load_model(self):
        """加载模型"""
        if self.is_loaded:
            logger.info("模型已加载，跳过")
            return
        
        logger.info(f"🚀 加载 vLLM 模型: {self.config.model_path}")
        start_time = time.time()
        
        try:
            from vllm import LLM, SamplingParams
            
            # 创建 vLLM 实例
            self.llm = LLM(
                model=self.config.model_path,
                tensor_parallel_size=self.config.tensor_parallel_size,
                dtype=self.config.dtype,
                quantization=self.config.quantization,
                max_model_len=self.config.max_model_len,
                gpu_memory_utilization=self.config.gpu_memory_utilization,
                trust_remote_code=True,
            )
            
            # 设置默认采样参数
            self.sampling_params = SamplingParams(
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                max_tokens=self.config.max_tokens,
            )
            
            self.is_loaded = True
            elapsed = time.time() - start_time
            
            logger.info(f"✅ vLLM 模型加载成功 (耗时: {elapsed:.2f}s)")
            logger.info(f"   GPU: {self.config.gpu_id}")
            logger.info(f"   张量并行: {self.config.tensor_parallel_size}")
            logger.info(f"   量化方法: {self.config.quantization}")
            logger.info(f"   显存利用率: {self.config.gpu_memory_utilization}")
            
        except ImportError:
            logger.error("❌ vLLM 未安装，请运行: pip install vllm")
            raise
        except Exception as e:
            logger.error(f"❌ vLLM 模型加载失败: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成文本"""
        if not self.is_loaded:
            self.load_model()
        
        from vllm import SamplingParams
        
        # 创建采样参数
        sampling_params = SamplingParams(
            temperature=temperature or self.config.temperature,
            top_p=top_p or self.config.top_p,
            top_k=self.config.top_k,
            max_tokens=max_tokens or self.config.max_tokens,
            **kwargs
        )
        
        start_time = time.time()
        
        # 生成
        outputs = self.llm.generate([prompt], sampling_params)
        output = outputs[0]
        
        # 提取结果
        generated_text = output.outputs[0].text
        num_tokens = len(output.outputs[0].token_ids)
        
        # 计算指标
        latency = time.time() - start_time
        throughput = num_tokens / latency if latency > 0 else 0
        
        return {
            'text': generated_text,
            'tokens': num_tokens,
            'latency': round(latency, 3),
            'throughput': round(throughput, 1)
        }
    
    def batch_generate(
        self,
        prompts: List[str],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """批量生成（vLLM 的核心优势：高效批处理）"""
        if not self.is_loaded:
            self.load_model()
        
        from vllm import SamplingParams
        
        # 创建采样参数
        sampling_params = SamplingParams(
            temperature=temperature or self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            max_tokens=max_tokens or self.config.max_tokens,
            **kwargs
        )
        
        start_time = time.time()
        
        # 批量生成（vLLM 会自动优化）
        outputs = self.llm.generate(prompts, sampling_params)
        
        total_latency = time.time() - start_time
        
        # 处理结果
        results = []
        for output in outputs:
            generated_text = output.outputs[0].text
            num_tokens = len(output.outputs[0].token_ids)
            
            results.append({
                'text': generated_text,
                'tokens': num_tokens,
                'latency': round(total_latency / len(prompts), 3),  # 平均延迟
                'throughput': round(num_tokens / (total_latency / len(prompts)), 1)
            })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        info = super().get_model_info()
        info.update({
            'vllm_version': self._get_vllm_version(),
            'tensor_parallel_size': self.config.tensor_parallel_size,
            'quantization': self.config.quantization,
            'gpu_memory_utilization': self.config.gpu_memory_utilization,
        })
        return info
    
    def _get_vllm_version(self) -> str:
        """获取 vLLM 版本"""
        try:
            import vllm
            return vllm.__version__
        except:
            return "unknown"
