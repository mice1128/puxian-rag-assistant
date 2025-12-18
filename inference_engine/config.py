#!/usr/bin/env python3
"""
推理引擎配置
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class InferenceConfig:
    """推理配置"""
    
    # 模型路径
    model_path: str = "/home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4"
    
    # GPU 配置
    gpu_id: int = 1  # 使用 GPU 1
    tensor_parallel_size: int = 1  # 张量并行度
    
    # 生成参数
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    
    # vLLM 特定配置
    dtype: str = "auto"  # 数据类型: auto, half, float16, bfloat16
    quantization: Optional[str] = "gptq"  # 量化方法: gptq, awq, None
    max_model_len: Optional[int] = None  # 最大序列长度
    gpu_memory_utilization: float = 0.9  # GPU 显存利用率
    
    # Transformers 特定配置
    device_map: str = "auto"  # 设备映射策略
    trust_remote_code: bool = True
    local_files_only: bool = True
    
    @classmethod
    def from_env(cls):
        """从环境变量加载配置"""
        return cls(
            model_path=os.getenv("MODEL_PATH", cls.model_path),
            gpu_id=int(os.getenv("GPU_ID", cls.gpu_id)),
            max_tokens=int(os.getenv("MAX_TOKENS", cls.max_tokens)),
            temperature=float(os.getenv("TEMPERATURE", cls.temperature)),
        )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'model_path': self.model_path,
            'gpu_id': self.gpu_id,
            'tensor_parallel_size': self.tensor_parallel_size,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'dtype': self.dtype,
            'quantization': self.quantization,
            'gpu_memory_utilization': self.gpu_memory_utilization,
        }
