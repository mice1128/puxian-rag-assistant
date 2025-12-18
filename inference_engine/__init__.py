#!/usr/bin/env python3
"""
推理引擎模块
支持多种推理后端：Transformers, vLLM
"""

__version__ = "1.0.0"

from .base_engine import BaseInferenceEngine
from .transformers_engine import TransformersEngine
from .vllm_engine import VLLMEngine

__all__ = [
    'BaseInferenceEngine',
    'TransformersEngine',
    'VLLMEngine',
]
