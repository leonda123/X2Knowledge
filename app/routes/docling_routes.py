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
@swag_from('../../swagger_docs/convert_to_md_docling.yml')
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
@swag_from('../../swagger_docs/convert_to_html_docling.yml')
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
@swag_from('../../swagger_docs/convert_to_md_file_docling.yml')
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
    
# 转换为Markdown并导出图片（Docling）
@bp.route('/convert-to-md-images-file-docling', methods=['POST'])
def convert_to_md_images_file_docling():
    """
    使用Docling将文件转换为Markdown并导出图片，同时将图片放入静态目录中以支持预览
    """
    start_time = time.time()
    execution_id = datetime.now().strftime("%Y%m%d%H%M%S")
    # 获取当前请求的主机和协议
    host_url = request.host_url.rstrip('/') 
    
    # 获取上传的文件
    if 'file' not in request.files:
        logger.warning(f"Docling图片导出{execution_id}：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning(f"Docling图片导出{execution_id}：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    base_filename = os.path.splitext(filename)[0]
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"Docling图片导出{execution_id}：接收到文件: {filename}, 类型: {file_ext}")
    
    # 初始化Docling转换器
    docling_converter = converter_factory.get_converter("docling")
    
    # 检查文件扩展名是否支持
    if not docling_converter.is_format_supported(file_ext):
        error_msg = f"Docling不支持的文件类型: {file_ext}"
        logger.warning(f"Docling图片导出{execution_id}：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # 创建保存图片的静态目录
    static_img_dir = os.path.join('app', 'static', 'images', 'exported', execution_id)
    static_img_url_path = f"{host_url}/static/images/exported/{execution_id}"
    
    try:
        file.save(file_path)
        logger.info(f"Docling图片导出{execution_id}：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"Docling图片导出{execution_id}：文件大小: {file_size / 1024:.2f} KB")
        
        # 创建静态图片目录
        if not os.path.exists(static_img_dir):
            os.makedirs(static_img_dir, exist_ok=True)
            logger.info(f"Docling图片导出{execution_id}：创建静态图片目录: {static_img_dir}")
        
        # 使用Docling处理文件
        try:
            from docling.document_converter import DocumentConverter
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.datamodel.base_models import InputFormat, FigureElement
            from docling.document_converter import PdfFormatOption
            from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
            
            # 设置Docling选项，启用图片导出
            IMAGE_RESOLUTION_SCALE = 2.0
            pipeline_options = PdfPipelineOptions()
            pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
            pipeline_options.generate_page_images = True
            pipeline_options.generate_picture_images = True
            
            # 创建通用格式选项
            format_options = {}
            
            # 根据文件类型添加适当的格式选项
            if file_ext.lower() in ['.pdf']:
                format_options[InputFormat.PDF] = PdfFormatOption(pipeline_options=pipeline_options)
            # 对于其他格式，不设置特定选项，使用Docling默认设置
            
            doc_converter = DocumentConverter(format_options=format_options)
            
            logger.info(f"Docling图片导出{execution_id}：开始转换文件并导出图片")
            doc_converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
            
            logger.info(f"Docling图片导出{execution_id}：开始转换文件并导出图片")
            
            # 转换文件
            conv_res = doc_converter.convert(file_path)
            doc_filename = conv_res.input.file.stem
            
            # 保存Markdown文件
            md_filename_full = os.path.join(static_img_dir, f"{doc_filename}.md")
            
            # 先使用独立引用模式保存原始的markdown
            conv_res.document.save_as_markdown(md_filename_full, image_mode=ImageRefMode.REFERENCED)
            logger.info(f"Docling图片导出{execution_id}：Markdown已保存到: {md_filename_full}")
            
            # 计数器
            page_counter = 0
            table_counter = 0
            picture_counter = 0
            
            # 保存页面图片
            page_image_paths = []
            page_image_urls = []
            for page_no, page in conv_res.document.pages.items():
                page_no = page.page_no
                page_image_filename = f"{doc_filename}-page-{page_no}.png"
                page_image_path = os.path.join(static_img_dir, page_image_filename)
                page_image_url = f"{static_img_url_path}/{page_image_filename}"
                
                try:
                    if hasattr(page, 'image') and page.image is not None and hasattr(page.image, 'pil_image') and page.image.pil_image is not None:
                        with open(page_image_path, 'wb') as fp:
                            page.image.pil_image.save(fp, format="PNG")
                        page_image_paths.append(page_image_path)
                        page_image_urls.append(page_image_url)
                        page_counter += 1
                        logger.info(f"Docling图片导出{execution_id}：页面图片已保存: {page_image_path}")
                    else:
                        logger.warning(f"Docling图片导出{execution_id}：页面 {page_no} 没有可用的图片")
                except Exception as e:
                    logger.warning(f"Docling图片导出{execution_id}：保存页面 {page_no} 图片时出错: {str(e)}")
            
            # 保存图片和表格
            table_image_paths = []
            table_image_urls = []
            picture_image_paths = []
            picture_image_urls = []
            
            for element, _level in conv_res.document.iterate_items():
                if isinstance(element, TableItem):
                    try:
                        image = element.get_image(conv_res.document)
                        if image is not None:
                            table_counter += 1  # 只有当成功获取图片时才增加计数
                            table_image_filename = f"{doc_filename}-table-{table_counter}.png"
                            table_image_path = os.path.join(static_img_dir, table_image_filename)
                            table_image_url = f"{static_img_url_path}/{table_image_filename}"
                            
                            with open(table_image_path, 'wb') as fp:
                                image.save(fp, "PNG")
                            table_image_paths.append(table_image_path)
                            table_image_urls.append(table_image_url)
                            logger.info(f"Docling图片导出{execution_id}：表格图片已保存: {table_image_path}")
                        else:
                            logger.warning(f"Docling图片导出{execution_id}：无法获取表格图片，图片为None")
                    except Exception as e:
                        logger.warning(f"Docling图片导出{execution_id}：处理表格图片时出错: {str(e)}")
                
                if isinstance(element, PictureItem):
                    try:
                        image = element.get_image(conv_res.document)
                        if image is not None:
                            picture_counter += 1  # 只有当成功获取图片时才增加计数
                            picture_image_filename = f"{doc_filename}-picture-{picture_counter}.png"
                            picture_image_path = os.path.join(static_img_dir, picture_image_filename)
                            picture_image_url = f"{static_img_url_path}/{picture_image_filename}"
                            
                            with open(picture_image_path, 'wb') as fp:
                                image.save(fp, "PNG")
                            picture_image_paths.append(picture_image_path)
                            picture_image_urls.append(picture_image_url)
                            logger.info(f"Docling图片导出{execution_id}：图片已保存: {picture_image_path}")
                        else:
                            logger.warning(f"Docling图片导出{execution_id}：无法获取图片，图片为None")
                    except Exception as e:
                        logger.warning(f"Docling图片导出{execution_id}：处理图片时出错: {str(e)}")
            
            # 读取原始Markdown内容
            with open(md_filename_full, 'r', encoding='utf-8') as f:
                markdown_text = f.read()
            
            # 将相对路径替换为完整URL路径
            # 提取artifacts文件夹名
            artifacts_dir = f"{doc_filename}_artifacts"
            
            # 替换 ![Image](artifacts_dir/imagename.png) 模式的图片路径
            pattern = r'!\[([^\]]*)\]\((' + re.escape(artifacts_dir) + r'[^)]+)\)'
            replacement = r'![\1](' + static_img_url_path + r'/\2)'
            
            markdown_text = re.sub(pattern, replacement, markdown_text)

            # 修复带有 backslashes 的 Windows 风格路径
            def replace_with_forward_slash(match):
                path = match.group(1)
                return f'![Image]({path.replace("\\", "/")})'
            
            # 匹配图片链接中的路径并替换反斜杠
            markdown_text = re.sub(r'!\[Image\]\(([^)]+)\)', replace_with_forward_slash, markdown_text)
            
            # 替换页面图片路径
            for i, path in enumerate(page_image_paths):
                markdown_text = markdown_text.replace(path, page_image_urls[i])
            
            # 替换表格图片路径
            for i, path in enumerate(table_image_paths):
                markdown_text = markdown_text.replace(path, table_image_urls[i])
            
            # 替换普通图片路径
            for i, path in enumerate(picture_image_paths):
                markdown_text = markdown_text.replace(path, picture_image_urls[i])
            
            # 保存修改后的Markdown内容
            with open(md_filename_full, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            
            processing_time = time.time() - start_time
            logger.info(f"Docling图片导出{execution_id}：处理完成，耗时: {processing_time:.2f}秒")
            
            # 删除临时文件
            cleanup_temp_file(file_path, f"Docling图片导出{execution_id}：")
            
            # 返回处理结果
            return jsonify({
                'text': markdown_text,
                'processing_time': round(processing_time, 2),
                'converter': 'docling',
                'page_count': page_counter,
                'table_count': table_counter,
                'picture_count': picture_counter
            })
            
        except ImportError as e:
            error_msg = f"Docling库导入错误: {str(e)}"
            logger.error(f"Docling图片导出{execution_id}：{error_msg}")
            cleanup_temp_file(file_path, f"Docling图片导出{execution_id}：")
            return jsonify({'error': error_msg}), 500
        except Exception as e:
            error_msg = f"Docling处理失败: {str(e)}"
            logger.error(f"Docling图片导出{execution_id}：{error_msg}")
            logger.error(traceback.format_exc())
            cleanup_temp_file(file_path, f"Docling图片导出{execution_id}：")
            return jsonify({'error': error_msg, 'details': traceback.format_exc()}), 500
    
    except Exception as e:
        error_msg = f"处理文件时出错: {str(e)}"
        logger.error(f"Docling图片导出{execution_id}：{error_msg}")
        logger.error(traceback.format_exc())
        
        # 删除临时文件
        cleanup_temp_file(file_path, f"Docling图片导出{execution_id}：")
        
        return jsonify({'error': error_msg, 'details': traceback.format_exc()}), 500 
@app.route('/api/convert-to-md-images-file-docling', methods=['POST'])
@swag_from('../../swagger_docs/convert_to_md_images_file_docling.yml')
def api_convert_to_md_images_file_docling():
    """
    使用Docling将文件转换为Markdown并导出图片
    """
    start_time = time.time()
    execution_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 获取上传的文件
    if 'file' not in request.files:
        logger.warning(f"API调用(Docling图片导出){execution_id}：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning(f"API调用(Docling图片导出){execution_id}：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取输出目录
    output_dir = request.form.get('output_dir')
    if not output_dir:
        logger.warning(f"API调用(Docling图片导出){execution_id}：未指定输出目录")
        return jsonify({'error': '未指定输出目录'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    base_filename = os.path.splitext(filename)[0]
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(Docling图片导出){execution_id}：接收到文件: {filename}, 类型: {file_ext}")
    
    # 初始化Docling转换器
    docling_converter = converter_factory.get_converter("docling")
    
    # 检查文件扩展名是否支持
    if not docling_converter.is_format_supported(file_ext):
        error_msg = f"Docling不支持的文件类型: {file_ext}"
        logger.warning(f"API调用(Docling图片导出){execution_id}：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(Docling图片导出){execution_id}：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(Docling图片导出){execution_id}：文件大小: {file_size / 1024:.2f} KB")
        
        # 检查输出目录是否存在，不存在则创建
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"API调用(Docling图片导出){execution_id}：创建输出目录: {output_dir}")
            except Exception as e:
                error_msg = f"无法创建输出目录: {str(e)}"
                logger.error(f"API调用(Docling图片导出){execution_id}：{error_msg}")
                
                # 删除临时文件
                try:
                    os.remove(file_path)
                    logger.info(f"API调用(Docling图片导出){execution_id}：临时文件已删除: {file_path}")
                except Exception as del_e:
                    logger.warning(f"API调用(Docling图片导出){execution_id}：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
                
                return jsonify({'error': error_msg}), 500
        
        # 使用Docling处理文件
        try:
            from docling.document_converter import DocumentConverter
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.datamodel.base_models import InputFormat, FigureElement
            from docling.document_converter import PdfFormatOption
            from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
            
            # 设置Docling选项，启用图片导出
            IMAGE_RESOLUTION_SCALE = 2.0
            pipeline_options = PdfPipelineOptions()
            pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
            pipeline_options.generate_page_images = True
            pipeline_options.generate_picture_images = True
            
            # 创建通用格式选项
            format_options = {}
            
            # 根据文件类型添加适当的格式选项
            if file_ext.lower() in ['.pdf']:
                format_options[InputFormat.PDF] = PdfFormatOption(pipeline_options=pipeline_options)
            # 对于其他格式，不设置特定选项，使用Docling默认设置
            
            doc_converter = DocumentConverter(format_options=format_options)
            
            logger.info(f"API调用(Docling图片导出){execution_id}：开始转换文件并导出图片")
            doc_converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
            
            logger.info(f"API调用(Docling图片导出){execution_id}：开始转换文件并导出图片")
            
            # 转换文件
            conv_res = doc_converter.convert(file_path)
            doc_filename = conv_res.input.file.stem
            
            # 保存Markdown文件
            md_filename = os.path.join(output_dir, f"{doc_filename}.md")
            conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)
            logger.info(f"API调用(Docling图片导出){execution_id}：Markdown已保存到: {md_filename}")
            
            # 保存页面图片
            page_image_paths = []
            for page_no, page in conv_res.document.pages.items():
                page_no = page.page_no
                page_image_filename = os.path.join(output_dir, f"{doc_filename}-page-{page_no}.png")
                try:
                    if hasattr(page, 'image') and page.image is not None and hasattr(page.image, 'pil_image') and page.image.pil_image is not None:
                        with open(page_image_filename, 'wb') as fp:
                            page.image.pil_image.save(fp, format="PNG")
                        page_image_paths.append(page_image_filename)
                        logger.info(f"API调用(Docling图片导出){execution_id}：页面图片已保存: {page_image_filename}")
                    else:
                        logger.warning(f"API调用(Docling图片导出){execution_id}：页面 {page_no} 没有可用的图片")
                except Exception as e:
                    logger.warning(f"API调用(Docling图片导出){execution_id}：保存页面 {page_no} 图片时出错: {str(e)}")
            
            # 保存图片和表格
            table_counter = 0  # 实际成功提取的表格数量
            picture_counter = 0  # 实际成功提取的图片数量
            table_image_paths = []
            picture_image_paths = []
            
            for element, _level in conv_res.document.iterate_items():
                if isinstance(element, TableItem):
                    try:
                        image = element.get_image(conv_res.document)
                        if image is not None:
                            table_counter += 1  # 只有当成功获取图片时才增加计数
                            element_image_filename = os.path.join(output_dir, f"{doc_filename}-table-{table_counter}.png")
                            with open(element_image_filename, 'wb') as fp:
                                image.save(fp, "PNG")
                            table_image_paths.append(element_image_filename)
                            logger.info(f"API调用(Docling图片导出){execution_id}：表格图片已保存: {element_image_filename}")
                        else:
                            logger.warning(f"API调用(Docling图片导出){execution_id}：无法获取表格图片，图片为None")
                    except Exception as e:
                        logger.warning(f"API调用(Docling图片导出){execution_id}：处理表格图片时出错: {str(e)}")
                
                if isinstance(element, PictureItem):
                    try:
                        image = element.get_image(conv_res.document)
                        if image is not None:
                            picture_counter += 1  # 只有当成功获取图片时才增加计数
                            element_image_filename = os.path.join(output_dir, f"{doc_filename}-picture-{picture_counter}.png")
                            with open(element_image_filename, 'wb') as fp:
                                image.save(fp, "PNG")
                            picture_image_paths.append(element_image_filename)
                            logger.info(f"API调用(Docling图片导出){execution_id}：图片已保存: {element_image_filename}")
                        else:
                            logger.warning(f"API调用(Docling图片导出){execution_id}：无法获取图片，图片为None")
                    except Exception as e:
                        logger.warning(f"API调用(Docling图片导出){execution_id}：处理图片时出错: {str(e)}")
            
            # 读取Markdown内容
            with open(md_filename, 'r', encoding='utf-8') as f:
                markdown_text = f.read()
            
            processing_time = time.time() - start_time
            logger.info(f"API调用(Docling图片导出){execution_id}：处理完成，耗时: {processing_time:.2f}秒")
            
            # 返回处理结果
            return jsonify({
                'output_path': md_filename,
                'filename': filename,
                'file_size': file_size,
                'processing_time': round(processing_time, 2),
                'converter': 'docling',
                'page_count': len(page_image_paths),
                'table_count': table_counter,
                'picture_count': picture_counter,
                'page_images': page_image_paths,
                'table_images': table_image_paths,
                'picture_images': picture_image_paths
            })
            
        except ImportError as e:
            error_msg = f"Docling库导入错误: {str(e)}"
            logger.error(f"API调用(Docling图片导出){execution_id}：{error_msg}")
            return jsonify({'error': error_msg}), 500
        except Exception as e:
            error_msg = f"Docling处理失败: {str(e)}"
            logger.error(f"API调用(Docling图片导出){execution_id}：{error_msg}")
            logger.error(traceback.format_exc())
            return jsonify({'error': error_msg, 'details': traceback.format_exc()}), 500
    
    except Exception as e:
        error_msg = f"处理文件时出错: {str(e)}"
        logger.error(f"API调用(Docling图片导出){execution_id}：{error_msg}")
        logger.error(traceback.format_exc())
        
        # 删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(Docling图片导出){execution_id}：临时文件已删除: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(Docling图片导出){execution_id}：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({'error': error_msg, 'details': traceback.format_exc()}), 500
    
    finally:
        # 删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(Docling图片导出){execution_id}：临时文件已删除: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(Docling图片导出){execution_id}：无法删除临时文件: {file_path}, 原因: {str(del_e)}")

# 使用Doling 导出表格
@bp.route('/api/export-tables-docling', methods=['POST'])
@swag_from('../../swagger_docs/export_tables_docling.yml')
def api_export_tables_docling():
    """
    使用Docling将文件中的表格导出为指定格式(md、csv、html)
    """
    start_time = time.time()
    execution_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 获取上传的文件
    if 'file' not in request.files:
        logger.warning(f"API调用(Docling表格导出){execution_id}：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning(f"API调用(Docling表格导出){execution_id}：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取输出目录
    output_dir = request.form.get('output_dir')
    if not output_dir:
        logger.warning(f"API调用(Docling表格导出){execution_id}：未指定输出目录")
        return jsonify({'error': '未指定输出目录'}), 400
    
    # 获取导出格式，默认全部导出
    export_formats = request.form.get('export_formats', 'md,csv,html').lower().split(',')
    valid_formats = {'md', 'csv', 'html'}
    export_formats = [fmt.strip() for fmt in export_formats if fmt.strip() in valid_formats]
    
    if not export_formats:
        logger.warning(f"API调用(Docling表格导出){execution_id}：未指定有效的导出格式")
        return jsonify({'error': '未指定有效的导出格式，支持的格式为：md、csv、html'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    base_filename = os.path.splitext(filename)[0]
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(Docling表格导出){execution_id}：接收到文件: {filename}, 类型: {file_ext}, 导出格式: {export_formats}")
    
    # 初始化Docling转换器
    docling_converter = converter_factory.get_converter("docling")
    
    # 检查文件扩展名是否支持
    if not docling_converter.is_format_supported(file_ext):
        error_msg = f"Docling不支持的文件类型: {file_ext}"
        logger.warning(f"API调用(Docling表格导出){execution_id}：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(Docling表格导出){execution_id}：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(Docling表格导出){execution_id}：文件大小: {file_size / 1024:.2f} KB")
        
        # 检查输出目录是否存在，不存在则创建
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"API调用(Docling表格导出){execution_id}：创建输出目录: {output_dir}")
            except Exception as e:
                error_msg = f"无法创建输出目录: {str(e)}"
                logger.error(f"API调用(Docling表格导出){execution_id}：{error_msg}")
                cleanup_temp_file(file_path, f"API调用(Docling表格导出){execution_id}：")
                return jsonify({'error': error_msg}), 500
        
        # 使用Docling处理文件
        try:
            import pandas as pd
            from docling.document_converter import DocumentConverter
            
            logger.info(f"API调用(Docling表格导出){execution_id}：开始转换文件并导出表格")
            
            # 创建文档转换器
            doc_converter = DocumentConverter()
            
            # 转换文件
            conv_res = doc_converter.convert(file_path)
            doc_filename = conv_res.input.file.stem
            
            # 保存表格
            table_outputs = []
            
            if not conv_res.document.tables:
                logger.warning(f"API调用(Docling表格导出){execution_id}：文档中未检测到表格")
                return jsonify({
                    'warning': '文档中未检测到表格',
                    'filename': filename,
                    'file_size': file_size,
                    'processing_time': round(time.time() - start_time, 2),
                    'table_count': 0,
                    'tables': []
                })
            
            for table_ix, table in enumerate(conv_res.document.tables):
                table_outputs_item = {'index': table_ix + 1}
                
                # 导出表格到DataFrame
                try:
                    table_df = table.export_to_dataframe()
                    logger.info(f"API调用(Docling表格导出){execution_id}：成功提取表格 {table_ix + 1}")
                    
                    # 保存为CSV
                    if 'csv' in export_formats:
                        csv_filename = f"{doc_filename}-table-{table_ix+1}.csv"
                        csv_path = os.path.join(output_dir, csv_filename)
                        table_df.to_csv(csv_path, index=False, encoding='utf-8')
                        logger.info(f"API调用(Docling表格导出){execution_id}：表格已保存为CSV: {csv_path}")
                        table_outputs_item['csv_path'] = csv_path
                    
                    # 保存为Markdown
                    if 'md' in export_formats:
                        md_filename = f"{doc_filename}-table-{table_ix+1}.md"
                        md_path = os.path.join(output_dir, md_filename)
                        with open(md_path, 'w', encoding='utf-8') as f:
                            f.write(table_df.to_markdown(index=False))
                        logger.info(f"API调用(Docling表格导出){execution_id}：表格已保存为Markdown: {md_path}")
                        table_outputs_item['md_path'] = md_path
                    
                    # 保存为HTML
                    if 'html' in export_formats:
                        html_filename = f"{doc_filename}-table-{table_ix+1}.html"
                        html_path = os.path.join(output_dir, html_filename)
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(table.export_to_html(doc=conv_res.document))
                        logger.info(f"API调用(Docling表格导出){execution_id}：表格已保存为HTML: {html_path}")
                        table_outputs_item['html_path'] = html_path
                    
                    # 添加到输出列表
                    table_outputs.append(table_outputs_item)
                    
                except Exception as table_error:
                    error_msg = f"处理表格 {table_ix + 1} 时出错: {str(table_error)}"
                    logger.error(f"API调用(Docling表格导出){execution_id}：{error_msg}")
                    logger.error(traceback.format_exc())
                    # 继续处理其他表格，不中断
            
            processing_time = time.time() - start_time
            logger.info(f"API调用(Docling表格导出){execution_id}：处理完成，耗时: {processing_time:.2f}秒")
            
            # 返回处理结果
            return jsonify({
                'filename': filename,
                'file_size': file_size,
                'processing_time': round(processing_time, 2),
                'export_formats': export_formats,
                'table_count': len(table_outputs),
                'tables': table_outputs
            })
            
        except ImportError as e:
            error_msg = f"Docling库导入错误: {str(e)}"
            logger.error(f"API调用(Docling表格导出){execution_id}：{error_msg}")
            logger.error(traceback.format_exc())
            cleanup_temp_file(file_path, f"API调用(Docling表格导出){execution_id}：")
            return jsonify({'error': error_msg}), 500
        except Exception as e:
            error_msg = f"Docling处理失败: {str(e)}"
            logger.error(f"API调用(Docling表格导出){execution_id}：{error_msg}")
            logger.error(traceback.format_exc())
            cleanup_temp_file(file_path, f"API调用(Docling表格导出){execution_id}：")
            return jsonify({'error': error_msg, 'details': traceback.format_exc()}), 500
    
    except Exception as e:
        error_msg = f"处理文件时出错: {str(e)}"
        logger.error(f"API调用(Docling表格导出){execution_id}：{error_msg}")
        logger.error(traceback.format_exc())
        cleanup_temp_file(file_path, f"API调用(Docling表格导出){execution_id}：")
        return jsonify({'error': error_msg, 'details': traceback.format_exc()}), 500
    
    finally:
        # 删除临时文件
        cleanup_temp_file(file_path, f"API调用(Docling表格导出){execution_id}：")