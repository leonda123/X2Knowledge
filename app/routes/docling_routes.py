"""
Docling API路由模块，包含Docling相关的文档转换API接口
"""
from flask import Blueprint, render_template, request, jsonify
import os
import traceback
import time
import re
from datetime import datetime
from flasgger import swag_from

from app import logger, app
from app.utils.converter_factory import converter_factory
from app.utils.common import cleanup_temp_file
from app.utils.converters import convert_to_markdown

# 创建Docling API蓝图
bp = Blueprint('docling', __name__)

# Docling转换为Markdown
@bp.route('/convert-to-md-docling', methods=['POST'])
def convert_md_docling_route():
    if 'file' not in request.files:
        logger.warning("没有文件上传(Docling)")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("未选择文件(Docling)")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"接收到文件(Docling转MD): {filename}, 类型: {file_ext}")
    
    # 获取docling转换器
    docling_converter = converter_factory.get_converter('docling')
    if not hasattr(docling_converter, 'is_available') or not docling_converter.is_available:
        logger.error("Docling转换器不可用")
        return jsonify({'error': 'Docling转换器不可用，请确认已安装docling库'}), 500
    
    # 检查文件扩展名是否支持
    if not docling_converter.is_format_supported(file_ext):
        logger.warning(f"Docling不支持的文件格式: {file_ext}")
        return jsonify({'error': f'Docling不支持的文件格式: {file_ext}'}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"文件保存成功(Docling转MD): {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"文件大小(Docling转MD): {file_size / 1024:.2f} KB")
        
        # 使用Docling转换为Markdown
        logger.info(f"开始使用Docling将文件转换为Markdown: {filename}")
        markdown_text = docling_converter.convert_to_markdown(file_path)
        
        # 记录转换结果
        text_length = len(markdown_text)
        logger.info(f"文件使用Docling转换为Markdown成功, 文本长度: {text_length} 字符")
        
        # 删除临时文件
        cleanup_temp_file(file_path, "Docling转MD：")
        
        return jsonify({'text': markdown_text})

    except Exception as e:
        # 详细记录异常信息
        error_msg = str(e)
        logger.error(f"Docling转换为Markdown失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        cleanup_temp_file(file_path, "Docling转MD：")
        
        return jsonify({
            'error': f'Docling转换为Markdown失败: {error_msg}', 
            'details': traceback.format_exc()
        }), 500

# API：使用Docling转换为Markdown
@bp.route('/api/convert-to-md-docling', methods=['POST'])
@swag_from('../swagger_docs/convert_to_md_docling.yml')
def api_convert_md_docling():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(Docling)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("API调用(Docling)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(Docling)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 获取docling转换器
    docling_converter = converter_factory.get_converter('docling')
    if not hasattr(docling_converter, 'is_available') or not docling_converter.is_available:
        logger.error("API调用(Docling)：Docling转换器不可用")
        return jsonify({'error': 'Docling转换器不可用，请确认已安装docling库'}), 500
    
    # 检查文件扩展名是否支持
    if not docling_converter.is_format_supported(file_ext):
        error_msg = f"Docling不支持的文件类型: {file_ext}"
        logger.warning(f"API调用(Docling)：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(Docling)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(Docling)：文件大小: {file_size / 1024:.2f} KB")
        
        # 使用Docling转换为Markdown
        logger.info(f"API调用(Docling)：开始转换文件: {filename}")
        markdown_text = docling_converter.convert_to_markdown(file_path)
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(Docling)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用(Docling)：")
        
        # 返回API响应
        return jsonify({
            'text': markdown_text,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2),
            'converter': 'docling'
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(Docling)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        cleanup_temp_file(file_path, "API调用(Docling)：")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：使用Docling转换为HTML
@bp.route('/api/convert-to-html-docling', methods=['POST'])
@swag_from('../swagger_docs/convert_to_html_docling.yml')
def api_convert_html_docling():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(Docling HTML)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("API调用(Docling HTML)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(Docling HTML)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 获取docling转换器
    docling_converter = converter_factory.get_converter('docling')
    if not hasattr(docling_converter, 'is_available') or not docling_converter.is_available:
        logger.error("API调用(Docling HTML)：Docling转换器不可用")
        return jsonify({'error': 'Docling转换器不可用，请确认已安装docling库'}), 500
    
    # 检查文件扩展名是否支持
    if not docling_converter.is_format_supported(file_ext):
        error_msg = f"Docling不支持的文件类型: {file_ext}"
        logger.warning(f"API调用(Docling HTML)：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(Docling HTML)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(Docling HTML)：文件大小: {file_size / 1024:.2f} KB")
        
        # 使用Docling转换为HTML
        logger.info(f"API调用(Docling HTML)：开始转换文件: {filename}")
        html_content = docling_converter.convert_to_html(file_path)
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(Docling HTML)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用(Docling HTML)：")
        
        # 返回API响应
        return jsonify({
            'html': html_content,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2),
            'converter': 'docling'
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(Docling HTML)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        cleanup_temp_file(file_path, "API调用(Docling HTML)：")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：使用Docling将文件转换为Markdown并保存到指定目录
@bp.route('/api/convert-to-md-file-docling', methods=['POST'])
@swag_from('../swagger_docs/convert_to_md_file_docling.yml')
def api_convert_md_file_docling():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(Docling保存)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    if 'output_dir' not in request.form:
        logger.warning("API调用(Docling保存)：未指定输出目录")
        return jsonify({'error': '未指定输出目录'}), 400
    
    file = request.files['file']
    output_dir = request.form['output_dir']
    
    if file.filename == '':
        logger.warning("API调用(Docling保存)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 检查输出目录是否存在，不存在则创建
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.info(f"API调用(Docling保存)：创建输出目录: {output_dir}")
        except Exception as e:
            error_msg = f"无法创建输出目录: {str(e)}"
            logger.error(f"API调用(Docling保存)：{error_msg}")
            return jsonify({'error': error_msg}), 500
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(Docling保存)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 获取docling转换器
    docling_converter = converter_factory.get_converter('docling')
    if not hasattr(docling_converter, 'is_available') or not docling_converter.is_available:
        logger.error("API调用(Docling保存)：Docling转换器不可用")
        return jsonify({'error': 'Docling转换器不可用，请确认已安装docling库'}), 500
    
    # 检查文件扩展名是否支持
    if not docling_converter.is_format_supported(file_ext):
        error_msg = f"Docling不支持的文件类型: {file_ext}"
        logger.warning(f"API调用(Docling保存)：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(Docling保存)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(Docling保存)：文件大小: {file_size / 1024:.2f} KB")
        
        # 使用Docling转换为Markdown
        logger.info(f"API调用(Docling保存)：开始转换文件: {filename}")
        markdown_text = docling_converter.convert_to_markdown(file_path)
        
        # 保存转换后的Markdown到输出目录
        output_filename = os.path.splitext(filename)[0] + '.md'
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        logger.info(f"API调用(Docling保存)：Markdown已保存到: {output_path}")
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(Docling保存)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用(Docling保存)：")
        
        # 返回API响应
        return jsonify({
            'output_path': output_path,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2),
            'converter': 'docling'
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(Docling保存)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        cleanup_temp_file(file_path, "API调用(Docling保存)：")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500 