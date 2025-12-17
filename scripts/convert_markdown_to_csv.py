#!/usr/bin/env python3
"""
将 hinghwa-RAG 的 Markdown 表格转换为 CSV 格式
"""
import re
import csv
import sys
from pathlib import Path

def parse_markdown_table(md_file):
    """解析 Markdown 表格"""
    print(f"正在解析: {md_file}")
    
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    entries = []
    entry_id = 1
    
    for i, line in enumerate(lines):
        # 跳过表头和分隔行
        if i < 2 or line.startswith('|---') or not line.strip():
            continue
        
        # 解析表格行
        if line.startswith('|'):
            cols = [col.strip() for col in line.split('|')[1:-1]]  # 去掉首尾空列
            
            if len(cols) >= 4:
                word = cols[0]          # 莆仙话词汇
                pinyin1 = cols[1]       # 拼音方案1
                pinyin2 = cols[2]       # 拼音方案2（音标）
                meaning = cols[3]       # 释义
                
                # 跳过空行
                if not word or not meaning:
                    continue
                
                # 从释义中提取例句
                example_pt = ""  # 莆仙话例句
                example_zh = ""  # 普通话例句
                note = ""        # 文化注释
                
                # 尝试分离例句（格式：～舅|～叔 或 汝食饭未？）
                if '|' in meaning:
                    parts = meaning.split('|')
                    note = parts[0] if parts[0] else meaning
                    if len(parts) > 1:
                        # 可能有例句
                        for part in parts[1:]:
                            if '（' in part or '(' in part:
                                # 包含解释的例句
                                example_pt = part.split('（')[0].split('(')[0].strip()
                    else:
                        note = meaning
                else:
                    note = meaning
                
                # 提取括号中的注释
                cultural_note = ""
                if '‖' in note:
                    parts = note.split('‖')
                    note = parts[0]
                    cultural_note = parts[1] if len(parts) > 1 else ""
                
                # 清理释义中的序号标记
                note = re.sub(r'^[①②③④⑤⑥⑦⑧⑨⑩]\s*', '', note)
                
                entry = {
                    'id': entry_id,
                    '莆仙话': word,
                    '拼音': pinyin1,
                    '国际音标': pinyin2,
                    '释义': note[:200] if len(note) > 200 else note,  # 限制长度
                    '例句_莆仙话': example_pt[:100] if example_pt else "",
                    '例句_普通话': example_zh[:100] if example_zh else "",
                    '文化注释': cultural_note[:100] if cultural_note else "",
                    '来源': 'hinghwa-RAG词典'
                }
                
                entries.append(entry)
                entry_id += 1
                
                # 每100条显示进度
                if entry_id % 100 == 0:
                    print(f"  已处理: {entry_id} 条")
    
    print(f"✅ 解析完成，共 {len(entries)} 条词汇")
    return entries

def save_to_csv(entries, output_file):
    """保存为 CSV 文件"""
    print(f"\n保存到: {output_file}")
    
    fieldnames = ['id', '莆仙话', '拼音', '国际音标', '释义', 
                  '例句_莆仙话', '例句_普通话', '文化注释', '来源']
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
    
    print(f"✅ CSV 文件已保存")
    
    # 显示统计
    total_size = Path(output_file).stat().st_size
    print(f"\n统计信息:")
    print(f"  词条数: {len(entries)}")
    print(f"  文件大小: {total_size / 1024:.1f} KB")

def main():
    # 输入文件
    input_file = '/home/zl/LLM/hinghwa-RAG/knowledge/defualt/简明词汇.md'
    
    # 输出文件
    output_file = '/home/zl/LLM/puxian-rag-assistant/data/knowledge/hinghwa_vocab.csv'
    
    print("=" * 60)
    print("📚 Markdown 词典转 CSV 工具")
    print("=" * 60)
    
    # 解析
    entries = parse_markdown_table(input_file)
    
    # 保存
    save_to_csv(entries, output_file)
    
    print("\n" + "=" * 60)
    print("✅ 转换完成！")
    print("=" * 60)
    print(f"\n现在可以导入知识库：")
    print(f"  cd /home/zl/LLM/puxian-rag-assistant")
    print(f"  python tests/test_knowledge.py import --file data/knowledge/hinghwa_vocab.csv")

if __name__ == "__main__":
    main()
