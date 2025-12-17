#!/usr/bin/env python3
"""
启动脚本
"""
from app import create_app
import logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app = create_app()
    
    logger.info("🚀 启动 Flask 开发服务器...")
    logger.info("访问地址: http://127.0.0.1:5000")
    logger.info("API 文档: http://127.0.0.1:5000/health")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
