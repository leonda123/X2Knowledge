"""
Web表单处理路由，处理网页上的表单提交
"""
from flask import Blueprint, request, jsonify, current_app
import os
import traceback
import time
import json
from datetime import datetime
import re
from flasgger import swag_from

from app import logger, app
from app.utils.converters import (
    convert_docx, 
    convert_xlsx, 
    convert_pptx, 
    convert_pdf, 
    convert_txt, 
    convert_md,
    convert_to_markdown
)
from app.utils.converter_factory import converter_factory
from app.utils.common import cleanup_temp_file
from app.utils.md_processor import process_markdown_file, process_markdown_text, parse_markdown_to_qa, save_as_json, save_as_csv

# 创建Web表单处理蓝图
bp = Blueprint('web', __name__)

# 转换为文本
@bp.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        logger.warning("没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"接收到文件: {filename}, 类型: {file_ext}")
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"文件大小: {file_size / 1024:.2f} KB")
        
        # 根据文件类型调用相应的转换函数
        if file_ext in ['.doc', '.docx']:
            logger.info(f"开始转换Word文档: {filename}")
            text = convert_docx(file_path)
        elif file_ext in ['.xls', '.xlsx']:
            logger.info(f"开始转换Excel文件: {filename}")
            text = convert_xlsx(file_path)
        elif file_ext in ['.ppt', '.pptx']:
            logger.info(f"开始转换PowerPoint文件: {filename}")
            text = convert_pptx(file_path)
        elif file_ext == '.pdf':
            logger.info(f"开始转换PDF文件: {filename}")
            text = convert_pdf(file_path)
        elif file_ext == '.txt':
            logger.info(f"开始读取文本文件: {filename}")
            text = convert_txt(file_path)
        elif file_ext == '.md':
            logger.info(f"开始转换Markdown文件: {filename}")
            text = convert_md(file_path)
        elif file_ext in ['.mp3', '.wav']:
            logger.info(f"开始转换音频文件: {filename}")
            text = "音频文件支持Markdown格式导出，请使用转MD功能"
        else:
            logger.warning(f"不支持的文件格式: {file_ext}")
            cleanup_temp_file(file_path)  # 删除不支持的文件
            return jsonify({'error': f'不支持的文件格式: {file_ext}'}), 400
        
        # 记录转换结果
        text_length = len(text)
        logger.info(f"文件转换成功, 文本长度: {text_length} 字符")
        
        # 删除临时文件
        cleanup_temp_file(file_path)
        
        return jsonify({'text': text})

    except Exception as e:
        # 详细记录异常信息
        error_msg = str(e)
        logger.error(f"转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        cleanup_temp_file(file_path)
            
        return jsonify({
            'error': f'转换失败: {error_msg}', 
            'details': traceback.format_exc()
        }), 500

# 转换为Markdown
@bp.route('/convert-to-md', methods=['POST'])
def convert_md_route():
    if 'file' not in request.files:
        logger.warning("没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"接收到文件(转MD): {filename}, 类型: {file_ext}")
    
    # 检查文件扩展名
    supported_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.md', '.mp3', '.wav']
    if file_ext not in supported_extensions:
        logger.warning(f"不支持的文件格式: {file_ext}")
        return jsonify({'error': f'不支持的文件格式: {file_ext}'}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"文件保存成功(转MD): {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"文件大小(转MD): {file_size / 1024:.2f} KB")
        
        # 使用MarkItDown转换为Markdown
        logger.info(f"开始将文件转换为Markdown: {filename}")
        markdown_text = convert_to_markdown(file_path)
        
        # 记录转换结果
        text_length = len(markdown_text)
        logger.info(f"文件转换为Markdown成功, 文本长度: {text_length} 字符")
        
        # 删除临时文件
        cleanup_temp_file(file_path, "转MD：")
        
        return jsonify({'text': markdown_text})

    except Exception as e:
        # 详细记录异常信息
        error_msg = str(e)
        logger.error(f"转换为Markdown失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        cleanup_temp_file(file_path, "转MD：")
            
        return jsonify({
            'error': f'转换为Markdown失败: {error_msg}', 
            'details': traceback.format_exc()
        }), 500
# 入库预处理：将Markdown处理为JSON和CSV格式
@bp.route('/preprocess-for-storage', methods=['POST'])
@swag_from('../../swagger_docs/preprocess_for_storage.yml')
def preprocess_for_storage():
    """
    将Markdown文件或文本处理为JSON和CSV格式，用于知识库入库前的数据准备
    
    详细描述见swagger_docs/preprocess_for_storage.yml
    """
    try:
        # 检查是否提供了文件或文本内容
        if 'file' not in request.files and 'text' not in request.form:
            logger.warning("没有提供Markdown文件或文本内容")
            return jsonify({'error': '请提供Markdown文件或文本内容'}), 400
        
        # 设置输出目录，如果未提供则使用默认目录
        output_dir = request.form.get('output_dir', current_app.config.get('STORAGE_FOLDER', 'storage'))
        
        # 获取输出格式
        output_format = request.form.get('format', 'both').lower()
        if output_format not in ['json', 'csv', 'both']:
            logger.warning(f"不支持的输出格式: {output_format}")
            return jsonify({'error': '输出格式必须是json、csv或both'}), 400
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 处理文件上传方式
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = file.filename
            
            # 检查是否为Markdown文件
            if not filename.lower().endswith('.md'):
                logger.warning(f"不支持的文件格式: {filename}")
                return jsonify({'error': '仅支持Markdown(.md)文件格式'}), 400
            
            # 保存上传的文件
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            logger.info(f"文件保存成功: {file_path}")
            
            # 设置输出文件名（不含扩展名）
            output_filename = request.form.get('filename', os.path.splitext(filename)[0])
            
            # 读取Markdown文件
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_text = f.read()
            
            # 解析Markdown为问答对
            qa_pairs = parse_markdown_to_qa(markdown_text)
            
            # 删除临时文件
            cleanup_temp_file(file_path)
            
        # 处理文本内容方式
        else:
            text = request.form.get('text', '')
            if not text:
                logger.warning("提供的Markdown文本内容为空")
                return jsonify({'error': 'Markdown文本内容不能为空'}), 400
            
            # 设置输出文件名（不含扩展名）
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = request.form.get('filename', f"markdown_{timestamp}")
            
            # 解析Markdown为问答对
            qa_pairs = parse_markdown_to_qa(text)
        
        # 根据输出格式保存文件
        result = {}
        
        # 生成输出文件路径
        json_path = os.path.join(output_dir, f"{output_filename}.json")
        csv_path = os.path.join(output_dir, f"{output_filename}.csv")
        
        # 保存为JSON
        if output_format in ['json', 'both']:
            save_as_json(qa_pairs, json_path)
            result['json_path'] = json_path
        
        # 保存为CSV
        if output_format in ['csv', 'both']:
            save_as_csv(qa_pairs, csv_path)
            result['csv_path'] = csv_path
        
        # 添加问答对数量到结果
        result['qa_count'] = len(qa_pairs)
        
        # 返回成功结果
        return jsonify(result)
        
    except Exception as e:
        # 详细记录异常信息
        error_msg = str(e)
        logger.error(f"预处理失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': f'预处理失败: {error_msg}',
            'details': traceback.format_exc()
        }), 500 