#!/usr/bin/env python3
"""
路由注册
"""
from .chat import chat_bp
from .knowledge import knowledge_bp
from .health import health_bp

__all__ = ['chat_bp', 'knowledge_bp', 'health_bp']
