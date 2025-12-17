#!/usr/bin/env python3
"""
Flask 应用工厂
"""
from flask import Flask
from flask_cors import CORS
from .config import Config
import logging
import os


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 配置日志
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )
    
    # 启用 CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    from .routes import chat_bp, knowledge_bp, health_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(knowledge_bp, url_prefix='/api/knowledge')
    
    # 确保数据目录存在
    os.makedirs(app.config['KNOWLEDGE_DIR'], exist_ok=True)
    os.makedirs(app.config['VECTORSTORE_DIR'], exist_ok=True)
    
    logging.info("✅ 莆仙话 RAG 助手启动成功")
    
    return app
