"""
Markdown预处理工具，用于将Markdown文件处理为JSON和CSV格式
处理知识库入库前的数据准备工作
"""
import os
import re
import json
import csv
import logging
from typing import List, Dict, Tuple
import pandas as pd

def parse_markdown_to_qa(markdown_text: str) -> List[Dict[str, str]]:
    """
    将Markdown文本解析为问答对的列表
    
    Args:
        markdown_text: Markdown格式的文本内容
        
    Returns:
        包含问答对的字典列表，每个字典包含'question'和'answer'键
    """
    # 添加一个结束标记，确保最后一个部分也能被处理
    markdown_text = markdown_text.strip() + "\n# END_OF_DOCUMENT"
    
    # 正则表达式匹配标题行（# 开头的行）
    heading_pattern = re.compile(r'^(#+)\s+(.*?)$', re.MULTILINE)
    
    # 查找所有标题位置
    headings = list(heading_pattern.finditer(markdown_text))
    
    # 如果没有找到标题，则返回空列表
    if not headings or len(headings) <= 1:  # 只有END_OF_DOCUMENT不处理
        return []
    
    qa_pairs = []
    
    # 处理标题和内容
    for i in range(len(headings) - 1):  # 减1是因为最后一个是我们添加的END_OF_DOCUMENT
        current_heading = headings[i]
        next_heading = headings[i + 1]
        
        # 获取当前标题的级别和文本
        level = len(current_heading.group(1))  # #的数量表示标题级别
        heading_text = current_heading.group(2).strip()
        
        # 跳过END_OF_DOCUMENT标题
        if heading_text == "END_OF_DOCUMENT":
            continue
        
        # 获取此标题下的内容（到下一个标题之前的所有文本）
        content_start = current_heading.end()
        content_end = next_heading.start()
        content = markdown_text[content_start:content_end].strip()
        
        # 跳过没有内容的标题
        if not content:
            continue
        
        # 查找上级标题（如果存在）
        parent_titles = []
        if level > 1:
            for j in range(i-1, -1, -1):
                prev_heading = headings[j]
                prev_level = len(prev_heading.group(1))
                
                if prev_level < level:
                    parent_title = prev_heading.group(2).strip()
                    parent_titles.insert(0, parent_title)  # 插入到前面，保持层级顺序
                    
                    # 如果找到一级标题，停止查找
                    if prev_level == 1:
                        break
        
        # 构建完整问题标题
        if parent_titles:
            question = ",".join(parent_titles) + "," + heading_text
        else:
            question = heading_text
        
        # 添加问答对
        qa_pairs.append({
            "question": question,
            "answer": content
        })
    
    return qa_pairs

def save_as_json(qa_pairs: List[Dict[str, str]], output_path: str) -> str:
    """
    将问答对保存为JSON文件
    
    Args:
        qa_pairs: 包含问答对的字典列表
        output_path: 输出文件路径
        
    Returns:
        保存的文件路径
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
    
    return output_path

def save_as_csv(qa_pairs: List[Dict[str, str]], output_path: str) -> str:
    """
    将问答对保存为CSV文件
    
    Args:
        qa_pairs: 包含问答对的字典列表
        output_path: 输出文件路径
        
    Returns:
        保存的文件路径
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 使用pandas保存为CSV，确保正确处理特殊字符和换行符
    df = pd.DataFrame(qa_pairs)
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    return output_path

def process_markdown_file(file_path: str, output_dir: str, filename_base: str = None) -> Tuple[str, str]:
    """
    处理Markdown文件，将其转换为JSON和CSV格式
    
    Args:
        file_path: Markdown文件路径
        output_dir: 输出目录
        filename_base: 输出文件名基础（不含扩展名），如果为None则使用原始文件名
        
    Returns:
        元组包含(json文件路径, csv文件路径)
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 如果没有提供文件名基础，则使用原始文件名（不含扩展名）
    if not filename_base:
        filename_base = os.path.splitext(os.path.basename(file_path))[0]
    
    # 读取Markdown文件
    with open(file_path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    
    # 解析Markdown为问答对
    qa_pairs = parse_markdown_to_qa(markdown_text)
    
    # 生成输出文件路径
    json_path = os.path.join(output_dir, f"{filename_base}.json")
    csv_path = os.path.join(output_dir, f"{filename_base}.csv")
    
    # 保存为JSON和CSV
    save_as_json(qa_pairs, json_path)
    save_as_csv(qa_pairs, csv_path)
    
    return json_path, csv_path

def process_markdown_text(markdown_text: str, output_dir: str, filename_base: str) -> Tuple[str, str]:
    """
    处理Markdown文本，将其转换为JSON和CSV格式
    
    Args:
        markdown_text: Markdown文本内容
        output_dir: 输出目录
        filename_base: 输出文件名基础（不含扩展名）
        
    Returns:
        元组包含(json文件路径, csv文件路径)
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 解析Markdown为问答对
    qa_pairs = parse_markdown_to_qa(markdown_text)
    
    # 生成输出文件路径
    json_path = os.path.join(output_dir, f"{filename_base}.json")
    csv_path = os.path.join(output_dir, f"{filename_base}.csv")
    
    # 保存为JSON和CSV
    save_as_json(qa_pairs, json_path)
    save_as_csv(qa_pairs, csv_path)
    
    return json_path, csv_path 