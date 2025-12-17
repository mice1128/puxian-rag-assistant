#!/usr/bin/env python3
"""
Qwen 模型服务
"""
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging
import os

logger = logging.getLogger(__name__)


class QwenService:
    """Qwen 模型服务（单例）"""
    _instance = None
    
    def __new__(cls, model_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_path=None):
        if self._initialized:
            return
        
        # 转换为绝对路径
        if model_path:
            self.model_path = os.path.abspath(model_path)
        else:
            from ..config import Config
            self.model_path = os.path.abspath(Config.QWEN_MODEL_PATH)
        
        self.tokenizer = None
        self.model = None
        # 强制使用 GPU 1
        self.device = "cuda:1" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Qwen 服务已初始化（懒加载模式），设备: {self.device}")
        # 延迟加载：首次调用 generate() 时才加载模型
        self._initialized = True
    
    def load_model(self):
        """加载模型"""
        try:
            logger.info(f"正在加载 Qwen 模型: {self.model_path}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                local_files_only=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map={"":  1},
                trust_remote_code=True,
                local_files_only=True
            )
            
            logger.info("✅ Qwen 模型加载成功")
            
        except Exception as e:
            logger.error(f"❌ 加载 Qwen 模型失败: {e}")
            raise
    
    def generate(self, prompt, max_new_tokens=512, temperature=0.7):
        """生成回答"""
        # 懒加载：首次调用时加载模型
        if self.model is None:
            logger.info("首次调用，开始加载 Qwen 模型...")
            self.load_model()
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9
                )
            
            response = self.tokenizer.decode(
                outputs[0][len(inputs.input_ids[0]):],
                skip_special_tokens=True
            )
            
            return response, len(outputs[0])
            
        except Exception as e:
            logger.error(f"生成回答失败: {e}")
            raise


# 全局单例
_qwen_service = None


def get_qwen_service():
    """获取 Qwen 服务单例"""
    global _qwen_service
    if _qwen_service is None:
        _qwen_service = QwenService()
    return _qwen_service
