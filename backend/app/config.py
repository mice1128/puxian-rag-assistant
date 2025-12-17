#!/usr/bin/env python3
"""
配置管理
"""
import os
from dotenv import load_dotenv

# 加载环境变量
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))


class Config:
    """应用配置"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    
    # 模型路径
    QWEN_MODEL_PATH = os.getenv('QWEN_MODEL_PATH', '/home/zl/LLM/Qwen2.5-7B-Instruct-GPTQ-Int4')
    EMBEDDING_MODEL_PATH = os.getenv('EMBEDDING_MODEL_PATH', '/home/zl/LLM/bge-small-zh-v1.5')
    
    # 知识库
    KNOWLEDGE_DIR = os.getenv('KNOWLEDGE_DIR', './data/knowledge')
    VECTORSTORE_DIR = os.getenv('VECTORSTORE_DIR', './data/vectorstore/chroma_db')
    DEFAULT_KNOWLEDGE_FILE = os.getenv('DEFAULT_KNOWLEDGE_FILE', './data/knowledge/putian_dialect.csv')
    
    # RAG 参数
    TOP_K = int(os.getenv('TOP_K', 3))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 512))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
    
    # 日志
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')
    
    # 支持的文件格式
    ALLOWED_EXTENSIONS = {'csv', 'pdf', 'txt', 'docx', 'md'}
