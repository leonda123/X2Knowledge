#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Docling转换测试脚本

该脚本用于测试Docling的文档转换功能，包括:
1. PDF转HTML
2. XML转HTML
3. PDF转Markdown
4. XML转Markdown
5. PDF转JSON

可以独立运行，不依赖于主应用。

使用方法:
python test_docling_conversion.py [测试文件路径]

如果不提供测试文件路径，将使用默认的测试文件。
"""

import os
import sys
import argparse
import logging
import json
import traceback
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("docling_test")

def test_docling_availability():
    """
    测试Docling库是否可用
    
    检查是否安装了Docling库，并尝试导入它。
    同时检查是否有CUDA支持用于GPU加速。
    
    @returns {bool} 如果Docling库可用，返回True；否则返回False
    """
    try:
        import docling
        logger.info("✅ Docling库已安装")
        
        # 检查是否有CUDA支持
        import torch
        has_cuda = torch.cuda.is_available()
        if has_cuda:
            logger.info("✅ 检测到CUDA支持，将使用GPU加速")
        else:
            logger.info("ℹ️ 未检测到CUDA支持，将使用CPU模式")
        
        return True
    except ImportError as e:
        logger.error(f"❌ 无法导入Docling库: {str(e)}")
        logger.error("请确保已安装Docling库: pip install docling")
        return False

def get_converter():
    """
    获取Docling转换器
    
    创建一个DocumentConverter实例用于文档转换。
    
    @returns {DocumentConverter|None} 如果成功，返回DocumentConverter实例；失败则返回None
    """
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        logger.info("✅ 成功创建Docling转换器")
        return converter
    except Exception as e:
        logger.error(f"❌ 创建Docling转换器失败: {str(e)}")
        return None

def convert_to_html(file_path, output_dir):
    """
    使用Docling将文件转换为HTML格式
    
    @param {str} file_path - 要转换的文件路径
    @param {str} output_dir - 输出目录路径
    @returns {bool} 转换成功返回True，失败返回False
    """
    try:
        logger.info(f"开始将文件转换为HTML: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"❌ 文件不存在: {file_path}")
            return False
        
        # 获取文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        supported_formats = ['.pdf', '.docx', '.xlsx', '.pptx', '.csv', 
                            '.html', '.xhtml', '.png', '.jpg', '.jpeg', 
                            '.tiff', '.bmp', '.md', '.xml']
        
        if file_ext not in supported_formats:
            logger.error(f"❌ 不支持的文件格式: {file_ext}")
            return False
        
        # 获取转换器
        converter = get_converter()
        if not converter:
            return False
        
        # 使用Docling处理文件
        file_name = os.path.basename(file_path)
        
        # 将文件转换为HTML
        logger.info("开始转换文件...")
        result = converter.convert(file_path)
        html_content = result.document.export_to_html()
        
        # 保存转换结果
        output_file = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_docling.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ HTML转换成功，已保存到: {output_file}")
        return True
    except Exception as e:
        logger.error(f"❌ HTML转换失败: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def convert_to_markdown(file_path, output_dir):
    """
    使用Docling将文件转换为Markdown格式
    
    @param {str} file_path - 要转换的文件路径
    @param {str} output_dir - 输出目录路径
    @returns {bool} 转换成功返回True，失败返回False
    """
    try:
        logger.info(f"开始将文件转换为Markdown: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"❌ 文件不存在: {file_path}")
            return False
        
        # 获取文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        supported_formats = ['.pdf', '.docx', '.xlsx', '.pptx', '.csv', 
                            '.html', '.xhtml', '.png', '.jpg', '.jpeg', 
                            '.tiff', '.bmp', '.md', '.xml']
        
        if file_ext not in supported_formats:
            logger.error(f"❌ 不支持的文件格式: {file_ext}")
            return False
        
        # 获取转换器
        converter = get_converter()
        if not converter:
            return False
        
        # 使用Docling处理文件
        file_name = os.path.basename(file_path)
        
        # 将文件转换为Markdown
        logger.info("开始转换文件...")
        result = converter.convert(file_path)
        markdown_content = result.document.export_to_markdown()
        
        # 保存转换结果
        output_file = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_docling.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"✅ Markdown转换成功，已保存到: {output_file}")
        return True
    except Exception as e:
        logger.error(f"❌ Markdown转换失败: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def convert_to_json(file_path, output_dir):
    """
    使用Docling将文件转换为JSON格式
    
    @param {str} file_path - 要转换的文件路径
    @param {str} output_dir - 输出目录路径
    @returns {bool} 转换成功返回True，失败返回False
    """
    try:
        logger.info(f"开始将文件转换为JSON: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"❌ 文件不存在: {file_path}")
            return False
        
        # 获取文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        supported_formats = ['.pdf', '.docx', '.xlsx', '.pptx', '.csv', 
                            '.html', '.xhtml', '.png', '.jpg', '.jpeg', 
                            '.tiff', '.bmp', '.md', '.xml']
        
        if file_ext not in supported_formats:
            logger.error(f"❌ 不支持的文件格式: {file_ext}")
            return False
        
        # 获取转换器
        converter = get_converter()
        if not converter:
            return False
        
        # 使用Docling处理文件
        file_name = os.path.basename(file_path)
        
        # 将文件转换为JSON
        logger.info("开始转换文件...")
        result = converter.convert(file_path)
        json_content = result.document.to_dict()
        
        # 保存转换结果
        output_file = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_docling.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ JSON转换成功，已保存到: {output_file}")
        return True
    except Exception as e:
        logger.error(f"❌ JSON转换失败: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def run_all_tests(file_path):
    """
    运行所有转换测试
    
    对指定文件运行所有转换测试（HTML、Markdown和JSON）
    
    @param {str} file_path - 要测试的文件路径
    @returns {bool} 如果所有测试都成功则返回True，否则返回False
    """
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"测试文件: {file_path}")
    logger.info(f"输出目录: {output_dir}")
    
    # 测试转换功能
    html_result = convert_to_html(file_path, output_dir)
    md_result = convert_to_markdown(file_path, output_dir)
    json_result = convert_to_json(file_path, output_dir)
    
    # 输出测试结果摘要
    logger.info("\n测试结果摘要:")
    logger.info(f"HTML转换: {'成功' if html_result else '失败'}")
    logger.info(f"Markdown转换: {'成功' if md_result else '失败'}")
    logger.info(f"JSON转换: {'成功' if json_result else '失败'}")
    
    if html_result and md_result and json_result:
        logger.info("✅ 所有测试均已通过!")
        return True
    else:
        logger.error("❌ 部分测试失败，请检查日志了解详情。")
        return False

def find_test_file(file_type=None):
    """
    查找测试文件
    
    在预设目录中查找指定类型的测试文件
    
    @param {str} file_type - 要查找的文件类型 ('pdf', 'xml', 'all')
    @returns {str|None} 如果找到，返回文件的完整路径；否则返回None
    """
    extensions = {
        'pdf': ['.pdf'],
        'xml': ['.xml'],
        'all': ['.pdf', '.xml', '.docx', '.xlsx', '.pptx', '.html']
    }
    
    # 如果未指定类型，默认查找PDF文件
    if not file_type or file_type not in extensions:
        file_type = 'pdf'
    
    # 查找当前目录及上级目录下的测试文件
    search_dirs = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_samples"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    ]
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for ext in extensions[file_type]:
                for file in os.listdir(search_dir):
                    if file.lower().endswith(ext):
                        return os.path.join(search_dir, file)
    
    return None

def main():
    """
    主函数
    
    解析命令行参数并执行测试流程
    """
    parser = argparse.ArgumentParser(description='Docling文档转换测试')
    parser.add_argument('file_path', nargs='?', help='测试文件路径')
    parser.add_argument('--type', choices=['pdf', 'xml', 'all'], default='pdf', help='测试文件类型')
    args = parser.parse_args()
    
    # 测试Docling是否可用
    if not test_docling_availability():
        sys.exit(1)
    
    # 确定测试文件
    file_path = args.file_path
    if not file_path:
        file_path = find_test_file(args.type)
        if not file_path:
            logger.error(f"❌ 未找到可用的{args.type}测试文件，请手动指定测试文件路径。")
            sys.exit(1)
    
    # 运行测试
    success = run_all_tests(file_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 