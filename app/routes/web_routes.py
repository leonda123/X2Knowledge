"""
Web表单处理路由，处理网页上的表单提交
"""
from flask import Blueprint, request, jsonify
import os
import traceback
import time
from datetime import datetime
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
from app.utils.converter_factory import converter_factory
from app.utils.common import cleanup_temp_file

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