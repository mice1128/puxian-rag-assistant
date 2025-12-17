#!/usr/bin/env python3
"""
对话路由
"""
from flask import Blueprint, request, jsonify
import logging

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """RAG 对话接口"""
    from ..services.rag_service import get_rag_service
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'status': 'error',
                'message': '问题不能为空'
            }), 400
        
        # 获取 RAG 服务
        rag_service = get_rag_service()
        
        # 生成回答
        result = rag_service.ask(question)
        
        return jsonify({
            'status': 'success',
            'data': {
                'answer': result['answer'],
                'sources': result.get('sources', []),
                'tokens_used': result.get('tokens_used', 0)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"对话失败: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@chat_bp.route('/chat/stream', methods=['POST'])
def chat_stream():
    """流式对话接口（预留）"""
    return jsonify({
        'status': 'error',
        'message': '流式对话暂未实现'
    }), 501
