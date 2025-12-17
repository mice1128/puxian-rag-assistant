#!/usr/bin/env python3
"""
文件解析工具
"""
import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_csv(filepath):
    """解析 CSV 文件"""
    texts = []
    metadatas = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader):
                # 组合所有列的内容
                text = " | ".join([f"{k}: {v}" for k, v in row.items() if v])
                
                texts.append(text)
                metadatas.append({
                    'source': Path(filepath).name,
                    'row': i + 1,
                    **row
                })
        
        logger.info(f"解析 CSV 文件: {len(texts)} 条记录")
        return texts, metadatas
        
    except Exception as e:
        logger.error(f"解析 CSV 失败: {e}")
        raise


def parse_txt(filepath):
    """解析 TXT 文件"""
    texts = []
    metadatas = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按段落分割
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        for i, para in enumerate(paragraphs):
            texts.append(para)
            metadatas.append({
                'source': Path(filepath).name,
                'paragraph': i + 1
            })
        
        logger.info(f"解析 TXT 文件: {len(texts)} 个段落")
        return texts, metadatas
        
    except Exception as e:
        logger.error(f"解析 TXT 失败: {e}")
        raise


def parse_md(filepath):
    """解析 Markdown 文件"""
    # 使用与 TXT 相同的逻辑
    return parse_txt(filepath)


def parse_pdf(filepath):
    """解析 PDF 文件"""
    from pdfminer.high_level import extract_text
    
    texts = []
    metadatas = []
    
    try:
        content = extract_text(filepath)
        
        # 按段落分割
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        for i, para in enumerate(paragraphs):
            texts.append(para)
            metadatas.append({
                'source': Path(filepath).name,
                'paragraph': i + 1,
                'type': 'pdf'
            })
        
        logger.info(f"解析 PDF 文件: {len(texts)} 个段落")
        return texts, metadatas
        
    except Exception as e:
        logger.error(f"解析 PDF 失败: {e}")
        raise


def parse_docx(filepath):
    """解析 DOCX 文件"""
    from docx import Document
    
    texts = []
    metadatas = []
    
    try:
        doc = Document(filepath)
        
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if text:
                texts.append(text)
                metadatas.append({
                    'source': Path(filepath).name,
                    'paragraph': i + 1,
                    'type': 'docx'
                })
        
        logger.info(f"解析 DOCX 文件: {len(texts)} 个段落")
        return texts, metadatas
        
    except Exception as e:
        logger.error(f"解析 DOCX 失败: {e}")
        raise


def parse_file(filepath):
    """根据文件类型解析文件"""
    ext = Path(filepath).suffix.lower()
    
    parsers = {
        '.csv': parse_csv,
        '.txt': parse_txt,
        '.md': parse_md,
        '.pdf': parse_pdf,
        '.docx': parse_docx
    }
    
    parser = parsers.get(ext)
    
    if not parser:
        raise ValueError(f"不支持的文件格式: {ext}")
    
    return parser(filepath)
