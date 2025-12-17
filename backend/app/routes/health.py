#!/usr/bin/env python3
"""
健康检查路由
"""
from flask import Blueprint, jsonify
import logging

health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'Puxian RAG Assistant',
        'version': '1.0.0'
    }), 200


@health_bp.route('/api/stats', methods=['GET'])
def get_stats():
    """获取系统统计"""
    from ..services.rag_service import get_rag_service
    
    try:
        rag_service = get_rag_service()
        stats = rag_service.get_metrics()
        
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
