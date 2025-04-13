"""
API路由模块，包含基本文档转换的API接口
"""
from flask import Blueprint, render_template, request, jsonify
import os
import traceback
import time
from datetime import datetime
from flasgger import swag_from
import re

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
from app.utils.url_converter import URLConverter
from app.utils.common import cleanup_temp_file

# 创建API蓝图
bp = Blueprint('api', __name__)

# API: 基本文本转换
@bp.route('/convert', methods=['POST'])
@swag_from('../../swagger_docs/convert.yml')
def api_convert():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("API调用：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用：接收到文件: {filename}, 类型: {file_ext}")
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用：文件大小: {file_size / 1024:.2f} KB")
        
        # 根据文件类型调用相应的转换函数
        if file_ext in ['.doc', '.docx']:
            logger.info(f"API调用：开始转换Word文档: {filename}")
            text = convert_docx(file_path)
        elif file_ext in ['.xls', '.xlsx']:
            logger.info(f"API调用：开始转换Excel文件: {filename}")
            text = convert_xlsx(file_path)
        elif file_ext in ['.ppt', '.pptx']:
            logger.info(f"API调用：开始转换PowerPoint文件: {filename}")
            text = convert_pptx(file_path)
        elif file_ext == '.pdf':
            logger.info(f"API调用：开始转换PDF文件: {filename}")
            text = convert_pdf(file_path)
        elif file_ext == '.txt':
            logger.info(f"API调用：开始转换文本文件: {filename}")
            text = convert_txt(file_path)
        elif file_ext == '.md':
            logger.info(f"API调用：开始转换Markdown文件: {filename}")
            text = convert_md(file_path)
        elif file_ext in ['.mp3', '.wav']:
            logger.info(f"API调用：开始转换音频文件: {filename}")
            text = "音频文件支持Markdown格式导出，请使用转MD API"
        else:
            error_msg = f"不支持的文件类型: {file_ext}"
            logger.warning(f"API调用：{error_msg}")
            
            # 删除临时文件
            cleanup_temp_file(file_path, "API调用：")
            
            return jsonify({'error': error_msg}), 400
        
        processing_time = time.time() - start_time
        logger.info(f"API调用：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用：")
        
        # 返回API响应
        return jsonify({
            'text': text,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2)
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用：")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：转换为Markdown
@bp.route('/convert-to-md', methods=['POST'])
@swag_from('../../swagger_docs/convert_to_md.yml')
def api_convert_md():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(转MD)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("API调用(转MD)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(转MD)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 检查文件扩展名
    supported_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.md', '.mp3', '.wav']
    if file_ext not in supported_extensions:
        logger.warning(f"API调用(转MD)：不支持的文件格式: {file_ext}")
        return jsonify({'error': f'不支持的文件格式: {file_ext}'}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(转MD)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(转MD)：文件大小: {file_size / 1024:.2f} KB")
        
        # 使用MarkItDown转换为Markdown
        logger.info(f"API调用(转MD)：开始将文件转换为Markdown: {filename}")
        markdown_text = convert_to_markdown(file_path)
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(转MD)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用(转MD)：")
        
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
        logger.error(f"API调用(转MD)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用(转MD)：")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：将文件转换为文本并保存到指定目录
@bp.route('/convert-file', methods=['POST'])
@swag_from('../../swagger_docs/convert_file.yml')
def api_convert_file():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(保存文本)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    if 'output_dir' not in request.form:
        logger.warning("API调用(保存文本)：未指定输出目录")
        return jsonify({'error': '未指定输出目录'}), 400
    
    file = request.files['file']
    output_dir = request.form['output_dir']
    
    if file.filename == '':
        logger.warning("API调用(保存文本)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 检查输出目录是否存在，不存在则创建
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.info(f"API调用(保存文本)：创建输出目录: {output_dir}")
        except Exception as e:
            error_msg = f"无法创建输出目录: {str(e)}"
            logger.error(f"API调用(保存文本)：{error_msg}")
            return jsonify({'error': error_msg}), 500
                
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(保存文本)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(保存文本)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(保存文本)：文件大小: {file_size / 1024:.2f} KB")
        
        # 根据文件类型调用相应的转换函数
        if file_ext in ['.doc', '.docx']:
            logger.info(f"API调用(保存文本)：开始转换Word文档: {filename}")
            text = convert_docx(file_path)
        elif file_ext in ['.xls', '.xlsx']:
            logger.info(f"API调用(保存文本)：开始转换Excel文件: {filename}")
            text = convert_xlsx(file_path)
        elif file_ext in ['.ppt', '.pptx']:
            logger.info(f"API调用(保存文本)：开始转换PowerPoint文件: {filename}")
            text = convert_pptx(file_path)
        elif file_ext == '.pdf':
            logger.info(f"API调用(保存文本)：开始转换PDF文件: {filename}")
            text = convert_pdf(file_path)
        elif file_ext == '.txt':
            logger.info(f"API调用(保存文本)：开始读取文本文件: {filename}")
            text = convert_txt(file_path)
        elif file_ext == '.md':
            logger.info(f"API调用(保存文本)：开始转换Markdown文件: {filename}")
            text = convert_md(file_path)
        elif file_ext in ['.mp3', '.wav']:
            logger.info(f"API调用(保存文本)：开始转换音频文件: {filename}")
            text = "音频文件支持Markdown格式导出，请使用转MD API"
        else:
            error_msg = f"不支持的文件类型: {file_ext}"
            logger.warning(f"API调用(保存文本)：{error_msg}")
            
            # 删除临时文件
            cleanup_temp_file(file_path, "API调用(保存文本)：")
            
            return jsonify({'error': error_msg}), 400
        
        # 保存转换后的文本到输出目录
        output_filename = os.path.splitext(filename)[0] + '.txt'
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.info(f"API调用(保存文本)：文本已保存到: {output_path}")
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(保存文本)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用(保存文本)：")
        
        # 返回API响应
        return jsonify({
            'output_path': output_path,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2)
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(保存文本)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用(保存文本)：")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：将文件转换为Markdown并保存到指定目录
@bp.route('/convert-to-md-file', methods=['POST'])
@swag_from('../../swagger_docs/convert_to_md_file.yml')
def api_convert_md_file():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(保存MD)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    if 'output_dir' not in request.form:
        logger.warning("API调用(保存MD)：未指定输出目录")
        return jsonify({'error': '未指定输出目录'}), 400
    
    file = request.files['file']
    output_dir = request.form['output_dir']
    
    if file.filename == '':
        logger.warning("API调用(保存MD)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 检查输出目录是否存在，不存在则创建
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.info(f"API调用(保存MD)：创建输出目录: {output_dir}")
        except Exception as e:
            error_msg = f"无法创建输出目录: {str(e)}"
            logger.error(f"API调用(保存MD)：{error_msg}")
            return jsonify({'error': error_msg}), 500
                
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(保存MD)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 检查文件扩展名
    supported_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.md', '.mp3', '.wav']
    if file_ext not in supported_extensions:
        logger.warning(f"API调用(保存MD)：不支持的文件格式: {file_ext}")
        return jsonify({'error': f'不支持的文件格式: {file_ext}'}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(保存MD)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(保存MD)：文件大小: {file_size / 1024:.2f} KB")
        
        # 使用MarkItDown转换为Markdown
        logger.info(f"API调用(保存MD)：开始将文件转换为Markdown: {filename}")
        markdown_text = convert_to_markdown(file_path)
        
        # 保存转换后的Markdown到输出目录
        output_filename = os.path.splitext(filename)[0] + '.md'
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        logger.info(f"API调用(保存MD)：Markdown已保存到: {output_path}")
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(保存MD)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用(保存MD)：")
        
        # 返回API响应
        return jsonify({
            'output_path': output_path,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2)
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(保存MD)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 删除临时文件
        cleanup_temp_file(file_path, "API调用(保存MD)：")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：将URL转换为Markdown
@bp.route('/convert-url-to-md', methods=['POST'])
@swag_from('../../swagger_docs/convert_url_to_md.yml')
def api_convert_url_to_md():
    """
    将URL网页内容转换为Markdown格式
    """
    start_time = time.time()
    
    # 检查是否提供了URL
    if 'url' not in request.form:
        logger.warning("API调用(URL转MD)：未提供URL")
        return jsonify({'error': '未提供URL'}), 400
    
    url = request.form['url']
    remove_header_footer = request.form.get('remove_header_footer', 'true').lower() in ['true', '1', 't', 'y', 'yes']
    selector = request.form.get('selector')  # 获取CSS选择器参数
    
    logger.info(f"API调用(URL转MD)：开始处理URL: {url}，移除页眉页脚: {remove_header_footer}，选择器: {selector}")
    
    # 初始化URL转换器
    url_converter = URLConverter()
    
    try:
        # 将URL转换为Markdown
        markdown_text = url_converter.convert_url_to_markdown(url, remove_header_footer, selector)
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(URL转MD)：URL转换完成，耗时: {processing_time:.2f}秒")
        
        # 返回API响应
        return jsonify({
            'text': markdown_text,
            'url': url,
            'processing_time': round(processing_time, 2)
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(URL转MD)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：将URL转换为Markdown文件并保存
@bp.route('/convert-url-to-md-file', methods=['POST'])
@swag_from('../../swagger_docs/convert_url_to_md_file.yml')
def api_convert_url_to_md_file():
    """
    将URL网页内容转换为Markdown格式并保存为文件
    """
    start_time = time.time()
    
    # 检查是否提供了URL和输出目录
    if 'url' not in request.form:
        logger.warning("API调用(URL转MD文件)：未提供URL")
        return jsonify({'error': '未提供URL'}), 400
    
    if 'output_dir' not in request.form:
        logger.warning("API调用(URL转MD文件)：未提供输出目录")
        return jsonify({'error': '未提供输出目录'}), 400
    
    url = request.form['url']
    output_dir = request.form['output_dir']
    remove_header_footer = request.form.get('remove_header_footer', 'true').lower() in ['true', '1', 't', 'y', 'yes']
    selector = request.form.get('selector')  # 获取CSS选择器参数
    
    logger.info(f"API调用(URL转MD文件)：开始处理URL: {url}，输出目录: {output_dir}，移除页眉页脚: {remove_header_footer}，选择器: {selector}")
    
    # 确保输出目录存在
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"确保输出目录存在: {output_dir}")
    except Exception as e:
        error_msg = f"创建输出目录失败: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500
    
    # 初始化URL转换器
    url_converter = URLConverter()
    
    try:
        # 将URL转换为Markdown
        markdown_text = url_converter.convert_url_to_markdown(url, remove_header_footer, selector)
        
        # 从URL中提取文件名
        import re
        from urllib.parse import urlparse
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # 生成安全的文件名
        if path and path != '/':
            # 从路径中提取最后一部分作为文件名
            filename_base = path.strip('/').split('/')[-1]
            # 清理文件名
            filename_base = re.sub(r'[\\/*?:"<>|]', '_', filename_base)
            if not filename_base:
                filename_base = domain
        else:
            filename_base = domain
        
        # 如果文件名太长或为空，则使用域名
        if len(filename_base) > 100 or not filename_base:
            filename_base = domain.replace('.', '_')
        
        # 添加时间戳避免重名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{filename_base}_{timestamp}.md"
        
        # 保存为Markdown文件
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(URL转MD文件)：URL转换完成并保存到: {output_path}，耗时: {processing_time:.2f}秒")
        
        # 返回API响应
        return jsonify({
            'output_path': output_path,
            'url': url,
            'filename': filename,
            'processing_time': round(processing_time, 2)
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(URL转MD文件)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500 