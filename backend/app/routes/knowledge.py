#!/usr/bin/env python3
"""
知识库管理路由
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import logging
import os

knowledge_bp = Blueprint('knowledge', __name__)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """检查文件扩展名"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@knowledge_bp.route('/upload', methods=['POST'])
def upload_file():
    """上传知识库文件"""
    from ..services.knowledge_service import get_knowledge_service
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '没有上传文件'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': '文件名为空'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': f'不支持的文件格式，仅支持: {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['KNOWLEDGE_DIR'], filename)
        file.save(filepath)
        
        # 处理文件并更新向量库
        knowledge_service = get_knowledge_service()
        result = knowledge_service.process_file(filepath)
        
        return jsonify({
            'status': 'success',
            'message': f'文件上传成功，已添加 {result["added_count"]} 条知识',
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"文件上传失败: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@knowledge_bp.route('/list', methods=['GET'])
def list_files():
    """列出所有知识库文件"""
    from ..services.knowledge_service import get_knowledge_service
    
    try:
        knowledge_service = get_knowledge_service()
        files = knowledge_service.list_files()
        
        return jsonify({
            'status': 'success',
            'data': files
        }), 200
        
    except Exception as e:
        logger.error(f"获取文件列表失败: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@knowledge_bp.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """删除知识库文件"""
    from ..services.knowledge_service import get_knowledge_service
    
    try:
        knowledge_service = get_knowledge_service()
        result = knowledge_service.delete_file(filename)
        
        return jsonify({
            'status': 'success',
            'message': result['message']
        }), 200
        
    except Exception as e:
        logger.error(f"删除文件失败: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@knowledge_bp.route('/rebuild', methods=['POST'])
def rebuild_vectorstore():
    """重建向量库"""
    from ..services.knowledge_service import get_knowledge_service
    
    try:
        knowledge_service = get_knowledge_service()
        result = knowledge_service.rebuild_vectorstore()
        
        return jsonify({
            'status': 'success',
            'message': f'向量库重建成功，共 {result["total_count"]} 条知识',
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"重建向量库失败: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
