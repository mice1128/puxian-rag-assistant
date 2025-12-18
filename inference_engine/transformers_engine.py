#!/usr/bin/env python3
"""
Transformers 原生推理引擎
"""
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Any, Optional
import logging

from .base_engine import BaseInferenceEngine
from .config import InferenceConfig

logger = logging.getLogger(__name__)


class TransformersEngine(BaseInferenceEngine):
    """Transformers 原生推理引擎"""
    
    def __init__(self, config: InferenceConfig):
        super().__init__(config)
        self.tokenizer = None
        self.device = f"cuda:{config.gpu_id}" if torch.cuda.is_available() else "cpu"
    
    def load_model(self):
        """加载模型"""
        if self.is_loaded:
            logger.info("模型已加载，跳过")
            return
        
        logger.info(f"🚀 加载 Transformers 模型: {self.config.model_path}")
        start_time = time.time()
        
        try:
            # 加载 tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=self.config.trust_remote_code,
                local_files_only=self.config.local_files_only
            )
            
            # 加载模型，强制使用指定 GPU
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                device_map={"": self.config.gpu_id},  # 强制使用指定 GPU
                trust_remote_code=self.config.trust_remote_code,
                local_files_only=self.config.local_files_only
            )
            
            self.is_loaded = True
            elapsed = time.time() - start_time
            
            logger.info(f"✅ 模型加载成功 (耗时: {elapsed:.2f}s)")
            logger.info(f"   设备: {self.device}")
            logger.info(f"   参数量: {sum(p.numel() for p in self.model.parameters()) / 1e9:.2f}B")
            
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
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
        
        # 使用配置默认值
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature
        top_p = top_p or self.config.top_p
        
        start_time = time.time()
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        input_length = inputs.input_ids.shape[1]
        
        # 生成
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=self.config.top_k,
                do_sample=True,
                **kwargs
            )
        
        # 解码
        generated_tokens = outputs[0][input_length:]
        text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        # 计算指标
        latency = time.time() - start_time
        num_tokens = len(generated_tokens)
        throughput = num_tokens / latency if latency > 0 else 0
        
        return {
            'text': text,
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
        """批量生成（原生 Transformers 批处理效率较低）"""
        if not self.is_loaded:
            self.load_model()
        
        results = []
        
        # 串行处理（Transformers 批处理对 GPTQ 模型支持不佳）
        for prompt in prompts:
            result = self.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            results.append(result)
        
        return results
