from flask import Flask, render_template, request, jsonify
import os
import logging
from datetime import datetime
import traceback
import time
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

# 配置日志
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 限制上传文件大小为50MB
app.config['UPLOAD_FOLDER'] = 'uploads'

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    logger.info("访问首页")
    return render_template('index.html')

@app.route('/OCR安装说明.md')
def ocr_installation():
    logger.info("访问OCR安装说明")
    try:
        with open('OCR安装说明.md', 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/markdown'}
    except Exception as e:
        logger.error(f"读取OCR安装说明失败: {str(e)}")
        return "OCR安装说明文件不存在", 404

@app.route('/api-docs')
def api_docs():
    logger.info("访问API文档页面")
    return render_template('api-docs.html')

# 转换为文本
@app.route('/convert', methods=['POST'])
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
        
        # 对所有文件类型尝试转换编码为UTF-8
        try:
            logger.info("尝试转换文件编码为UTF-8")
            convert_file_to_utf8(file_path, file_ext)
        except Exception as e:
            logger.warning(f"转换编码失败: {str(e)}，将使用原始文件")
        
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
            os.remove(file_path)  # 删除不支持的文件
            return jsonify({'error': f'不支持的文件格式: {file_ext}'}), 400
        
        # 记录转换结果
        text_length = len(text)
        logger.info(f"文件转换成功, 文本长度: {text_length} 字符")
        
        # 删除临时文件
        try:
            os.remove(file_path)
            logger.info(f"临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"无法删除临时文件: {file_path}, 原因: {str(e)}")
            # 尝试强制关闭文件句柄后再删除
            try:
                import gc
                gc.collect()  # 触发垃圾回收，释放未关闭的文件句柄
                os.remove(file_path)
                logger.info(f"临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
                # 不再尝试删除，避免阻塞程序
        
        return jsonify({'text': text})

    except Exception as e:
        # 详细记录异常信息
        error_msg = str(e)
        logger.error(f"转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"无法删除临时文件: {file_path}, 原因: {str(del_e)}")
                # 不再尝试删除，避免阻塞程序
            
        return jsonify({
            'error': f'转换失败: {error_msg}', 
            'details': traceback.format_exc()
        }), 500

# 转换为Markdown
@app.route('/convert-to-md', methods=['POST'])
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
        try:
            os.remove(file_path)
            logger.info(f"临时文件已删除(转MD): {file_path}")
        except Exception as e:
            logger.warning(f"无法删除临时文件(转MD): {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"临时文件已删除(转MD)(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"无法删除临时文件(转MD)(第二次尝试): {file_path}, 原因: {str(e2)}")
        
        return jsonify({'text': markdown_text})

    except Exception as e:
        # 详细记录异常信息
        error_msg = str(e)
        logger.error(f"转换为Markdown失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"清理临时文件(转MD): {file_path}")
            except Exception as del_e:
                logger.warning(f"无法删除临时文件(转MD): {file_path}, 原因: {str(del_e)}")
            
        return jsonify({
            'error': f'转换为Markdown失败: {error_msg}', 
            'details': traceback.format_exc()
        }), 500

@app.route('/api/convert', methods=['POST'])
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
        
        # 对所有文件类型尝试转换编码为UTF-8
        try:
            logger.info("API调用：尝试转换文件编码为UTF-8")
            convert_file_to_utf8(file_path, file_ext)
        except Exception as e:
            logger.warning(f"API调用：转换编码失败: {str(e)}，将使用原始文件")
        
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
            try:
                os.remove(file_path)
                logger.info(f"API调用：临时文件已删除: {file_path}")
            except Exception as e:
                logger.warning(f"API调用：无法删除临时文件: {file_path}, 原因: {str(e)}")
            
            return jsonify({'error': error_msg}), 400
        
        processing_time = time.time() - start_time
        logger.info(f"API调用：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        try:
            os.remove(file_path)
            logger.info(f"API调用：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用：无法删除临时文件: {file_path}, 原因: {str(e)}")
            # 尝试强制关闭文件句柄后再删除
            try:
                import gc
                gc.collect()  # 触发垃圾回收，释放未关闭的文件句柄
                os.remove(file_path)
                logger.info(f"API调用：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
                # 不再尝试删除，避免阻塞程序
        
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
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：转换为Markdown
@app.route('/api/convert-to-md', methods=['POST'])
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
        try:
            os.remove(file_path)
            logger.info(f"API调用(转MD)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(转MD)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"API调用(转MD)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(转MD)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
        
        # 返回API响应
        return jsonify({
            'text': markdown_text,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2)
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(转MD)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(转MD)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(转MD)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# Docling转换为Markdown
@app.route('/convert-to-md-docling', methods=['POST'])
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
        try:
            os.remove(file_path)
            logger.info(f"临时文件已删除(Docling转MD): {file_path}")
        except Exception as e:
            logger.warning(f"无法删除临时文件(Docling转MD): {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"临时文件已删除(Docling转MD)(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"无法删除临时文件(Docling转MD)(第二次尝试): {file_path}, 原因: {str(e2)}")
        
        return jsonify({'text': markdown_text})

    except Exception as e:
        # 详细记录异常信息
        error_msg = str(e)
        logger.error(f"Docling转换为Markdown失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"清理临时文件(Docling转MD): {file_path}")
            except Exception as del_e:
                logger.warning(f"无法删除临时文件(Docling转MD): {file_path}, 原因: {str(del_e)}")
            
        return jsonify({
            'error': f'Docling转换为Markdown失败: {error_msg}', 
            'details': traceback.format_exc()
        }), 500

# API：使用Docling转换为Markdown
@app.route('/api/convert-to-md-docling', methods=['POST'])
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
        try:
            os.remove(file_path)
            logger.info(f"API调用(Docling)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(Docling)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"API调用(Docling)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(Docling)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
        
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
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(Docling)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(Docling)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：使用Docling转换为HTML
@app.route('/api/convert-to-html-docling', methods=['POST'])
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
        try:
            os.remove(file_path)
            logger.info(f"API调用(Docling HTML)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(Docling HTML)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"API调用(Docling HTML)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(Docling HTML)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
        
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
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(Docling HTML)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(Docling HTML)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：使用Docling转换为JSON
@app.route('/api/convert-to-json-docling', methods=['POST'])
def api_convert_json_docling():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(Docling JSON)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("API调用(Docling JSON)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(Docling JSON)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 获取docling转换器
    docling_converter = converter_factory.get_converter('docling')
    if not hasattr(docling_converter, 'is_available') or not docling_converter.is_available:
        logger.error("API调用(Docling JSON)：Docling转换器不可用")
        return jsonify({'error': 'Docling转换器不可用，请确认已安装docling库'}), 500
    
    # 检查文件扩展名是否支持
    if not docling_converter.is_format_supported(file_ext):
        error_msg = f"Docling不支持的文件类型: {file_ext}"
        logger.warning(f"API调用(Docling JSON)：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(Docling JSON)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(Docling JSON)：文件大小: {file_size / 1024:.2f} KB")
        
        # 使用Docling转换为JSON
        logger.info(f"API调用(Docling JSON)：开始转换文件: {filename}")
        json_content = docling_converter.convert_to_json(file_path)
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(Docling JSON)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        try:
            os.remove(file_path)
            logger.info(f"API调用(Docling JSON)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(Docling JSON)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"API调用(Docling JSON)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(Docling JSON)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
        
        # 返回API响应
        return jsonify({
            'json_content': json_content,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2),
            'converter': 'docling'
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(Docling JSON)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(Docling JSON)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(Docling JSON)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：批量转换文件夹内所有文件为文本
@app.route('/api/convert-folder', methods=['POST'])
def api_convert_folder():
    start_time = time.time()
    
    # 获取请求参数
    data = request.json
    if not data:
        logger.warning("API调用（批量文本）：无效的请求数据")
        return jsonify({'error': '无效的请求数据'}), 400
    
    source_folder = data.get('source_folder')
    output_folder = data.get('output_folder')
    
    if not source_folder:
        logger.warning("API调用（批量文本）：未提供源文件夹路径")
        return jsonify({'error': '必须提供源文件夹路径'}), 400
    
    if not output_folder:
        # 如果未提供输出文件夹，则在源文件夹创建一个output子文件夹
        output_folder = os.path.join(source_folder, 'output_text')
    
    # 检查源文件夹是否存在
    if not os.path.exists(source_folder) or not os.path.isdir(source_folder):
        logger.warning(f"API调用（批量文本）：源文件夹不存在或不是一个目录: {source_folder}")
        return jsonify({'error': f'源文件夹不存在或不是一个目录: {source_folder}'}), 400
    
    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)
    
    # 创建日志文件
    log_file = os.path.join(output_folder, "conversion_log.txt")
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"批量文本转换开始：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"源文件夹：{source_folder}\n")
        log.write(f"输出文件夹：{output_folder}\n")
        log.write("="*50 + "\n")
        
        # 获取转换器
        markitdown_converter = converter_factory.get_converter('markitdown')
        
        # 支持的文件格式
        supported_formats = [ext for ext in markitdown_converter.supported_input_formats]
        
        # 添加进度追踪
        conversion_results = {
            'total_files': 0,
            'converted_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'conversion_details': []
        }
        
        # 遍历源文件夹中的所有文件
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 获取相对路径，用于创建输出文件的路径
                rel_path = os.path.relpath(root, source_folder)
                output_subdir = os.path.join(output_folder, rel_path) if rel_path != '.' else output_folder
                os.makedirs(output_subdir, exist_ok=True)
                
                # 获取文件扩展名
                file_ext = os.path.splitext(file)[1].lower()
                
                # 更新总文件计数
                conversion_results['total_files'] += 1
                
                # 检查文件是否支持
                if file_ext not in supported_formats:
                    log.write(f"跳过不支持的文件：{file_path} (格式: {file_ext})\n")
                    conversion_results['skipped_files'] += 1
                    conversion_results['conversion_details'].append({
                        'file': file_path,
                        'status': 'skipped',
                        'reason': f'不支持的文件格式: {file_ext}'
                    })
                    continue
                
                # 转换文件
                log.write(f"开始转换文件：{file_path}\n")
                file_start_time = time.time()
                
                try:
                    # 执行转换
                    text_content = markitdown_converter.convert_to_text(file_path)
                    
                    # 创建输出文件名
                    output_file = os.path.join(output_subdir, os.path.splitext(file)[0] + '.txt')
                    
                    # 写入转换结果
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text_content)
                    
                    # 计算转换时间
                    file_process_time = time.time() - file_start_time
                    
                    # 更新日志
                    log.write(f"成功转换：{file_path} -> {output_file} (用时: {file_process_time:.2f}秒)\n")
                    log.write("-"*50 + "\n")
                    
                    # 更新计数
                    conversion_results['converted_files'] += 1
                    conversion_results['conversion_details'].append({
                        'file': file_path,
                        'status': 'success',
                        'output': output_file,
                        'processing_time': round(file_process_time, 2)
                    })
                    
                except Exception as e:
                    # 处理转换错误
                    log.write(f"转换失败：{file_path} - 错误: {str(e)}\n")
                    log.write("-"*50 + "\n")
                    
                    # 更新计数
                    conversion_results['failed_files'] += 1
                    conversion_results['conversion_details'].append({
                        'file': file_path,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
                    logger.error(f"批量转换：文件{file_path}转换失败: {str(e)}")
                    logger.error(traceback.format_exc())
        
        # 写入总结
        total_time = time.time() - start_time
        log.write("\n" + "="*50 + "\n")
        log.write(f"转换完成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"总用时：{total_time:.2f}秒\n")
        log.write(f"总文件数：{conversion_results['total_files']}\n")
        log.write(f"成功转换：{conversion_results['converted_files']}个文件\n")
        log.write(f"跳过文件：{conversion_results['skipped_files']}个文件\n")
        log.write(f"转换失败：{conversion_results['failed_files']}个文件\n")
    
    # 返回API响应
    response = {
        'source_folder': source_folder,
        'output_folder': output_folder,
        'log_file': log_file,
        'total_time': round(total_time, 2),
        'results': conversion_results
    }
    
    logger.info(f"API调用（批量文本）：完成文件夹转换，总耗时: {total_time:.2f}秒")
    return jsonify(response)

# API：批量转换文件夹内所有文件为Markdown (MarkItDown)
@app.route('/api/convert-to-md-folder', methods=['POST'])
def api_convert_md_folder():
    start_time = time.time()
    
    # 获取请求参数
    data = request.json
    if not data:
        logger.warning("API调用（批量Markdown）：无效的请求数据")
        return jsonify({'error': '无效的请求数据'}), 400
    
    source_folder = data.get('source_folder')
    output_folder = data.get('output_folder')
    
    if not source_folder:
        logger.warning("API调用（批量Markdown）：未提供源文件夹路径")
        return jsonify({'error': '必须提供源文件夹路径'}), 400
    
    if not output_folder:
        # 如果未提供输出文件夹，则在源文件夹创建一个output子文件夹
        output_folder = os.path.join(source_folder, 'output_markdown')
    
    # 检查源文件夹是否存在
    if not os.path.exists(source_folder) or not os.path.isdir(source_folder):
        logger.warning(f"API调用（批量Markdown）：源文件夹不存在或不是一个目录: {source_folder}")
        return jsonify({'error': f'源文件夹不存在或不是一个目录: {source_folder}'}), 400
    
    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)
    
    # 创建日志文件
    log_file = os.path.join(output_folder, "conversion_log.txt")
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"批量Markdown转换开始：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"源文件夹：{source_folder}\n")
        log.write(f"输出文件夹：{output_folder}\n")
        log.write("="*50 + "\n")
        
        # 获取转换器
        markitdown_converter = converter_factory.get_converter('markitdown')
        
        # 支持的文件格式
        supported_formats = [ext for ext in markitdown_converter.supported_input_formats]
        
        # 添加进度追踪
        conversion_results = {
            'total_files': 0,
            'converted_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'conversion_details': []
        }
        
        # 遍历源文件夹中的所有文件
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 获取相对路径，用于创建输出文件的路径
                rel_path = os.path.relpath(root, source_folder)
                output_subdir = os.path.join(output_folder, rel_path) if rel_path != '.' else output_folder
                os.makedirs(output_subdir, exist_ok=True)
                
                # 获取文件扩展名
                file_ext = os.path.splitext(file)[1].lower()
                
                # 更新总文件计数
                conversion_results['total_files'] += 1
                
                # 检查文件是否支持
                if file_ext not in supported_formats:
                    log.write(f"跳过不支持的文件：{file_path} (格式: {file_ext})\n")
                    conversion_results['skipped_files'] += 1
                    conversion_results['conversion_details'].append({
                        'file': file_path,
                        'status': 'skipped',
                        'reason': f'不支持的文件格式: {file_ext}'
                    })
                    continue
                
                # 转换文件
                log.write(f"开始转换文件：{file_path}\n")
                file_start_time = time.time()
                
                try:
                    # 执行转换
                    md_content = markitdown_converter.convert_to_markdown(file_path)
                    
                    # 创建输出文件名
                    output_file = os.path.join(output_subdir, os.path.splitext(file)[0] + '.md')
                    
                    # 写入转换结果
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    
                    # 计算转换时间
                    file_process_time = time.time() - file_start_time
                    
                    # 更新日志
                    log.write(f"成功转换：{file_path} -> {output_file} (用时: {file_process_time:.2f}秒)\n")
                    log.write("-"*50 + "\n")
                    
                    # 更新计数
                    conversion_results['converted_files'] += 1
                    conversion_results['conversion_details'].append({
                        'file': file_path,
                        'status': 'success',
                        'output': output_file,
                        'processing_time': round(file_process_time, 2)
                    })
                    
                except Exception as e:
                    # 处理转换错误
                    log.write(f"转换失败：{file_path} - 错误: {str(e)}\n")
                    log.write("-"*50 + "\n")
                    
                    # 更新计数
                    conversion_results['failed_files'] += 1
                    conversion_results['conversion_details'].append({
                        'file': file_path,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
                    logger.error(f"批量转换：文件{file_path}转换失败: {str(e)}")
                    logger.error(traceback.format_exc())
        
        # 写入总结
        total_time = time.time() - start_time
        log.write("\n" + "="*50 + "\n")
        log.write(f"转换完成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"总用时：{total_time:.2f}秒\n")
        log.write(f"总文件数：{conversion_results['total_files']}\n")
        log.write(f"成功转换：{conversion_results['converted_files']}个文件\n")
        log.write(f"跳过文件：{conversion_results['skipped_files']}个文件\n")
        log.write(f"转换失败：{conversion_results['failed_files']}个文件\n")
    
    # 返回API响应
    response = {
        'source_folder': source_folder,
        'output_folder': output_folder,
        'log_file': log_file,
        'total_time': round(total_time, 2),
        'results': conversion_results
    }
    
    logger.info(f"API调用（批量Markdown）：完成文件夹转换，总耗时: {total_time:.2f}秒")
    return jsonify(response)

# API：批量转换文件夹内所有文件为Markdown (Docling)
@app.route('/api/convert-to-md-docling-folder', methods=['POST'])
def api_convert_md_docling_folder():
    start_time = time.time()
    
    # 获取请求参数
    data = request.json
    if not data:
        logger.warning("API调用（批量Docling）：无效的请求数据")
        return jsonify({'error': '无效的请求数据'}), 400
    
    source_folder = data.get('source_folder')
    output_folder = data.get('output_folder')
    
    if not source_folder:
        logger.warning("API调用（批量Docling）：未提供源文件夹路径")
        return jsonify({'error': '必须提供源文件夹路径'}), 400
    
    if not output_folder:
        # 如果未提供输出文件夹，则在源文件夹创建一个output子文件夹
        output_folder = os.path.join(source_folder, 'output_docling')
    
    # 检查源文件夹是否存在
    if not os.path.exists(source_folder) or not os.path.isdir(source_folder):
        logger.warning(f"API调用（批量Docling）：源文件夹不存在或不是一个目录: {source_folder}")
        return jsonify({'error': f'源文件夹不存在或不是一个目录: {source_folder}'}), 400
    
    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)
    
    # 获取Docling转换器
    docling_converter = converter_factory.get_converter('docling')
    if not hasattr(docling_converter, 'is_available') or not docling_converter.is_available:
        error_msg = "Docling转换器不可用，请确认已安装docling库"
        logger.error(f"API调用（批量Docling）：{error_msg}")
        return jsonify({'error': error_msg}), 500
    
    # 创建日志文件
    log_file = os.path.join(output_folder, "conversion_log.txt")
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"批量Docling Markdown转换开始：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"源文件夹：{source_folder}\n")
        log.write(f"输出文件夹：{output_folder}\n")
        log.write("="*50 + "\n")
        
        # 支持的文件格式
        supported_formats = [ext for ext in docling_converter.supported_input_formats]
        
        # 添加进度追踪
        conversion_results = {
            'total_files': 0,
            'converted_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'conversion_details': []
        }
        
        # 遍历源文件夹中的所有文件
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 获取相对路径，用于创建输出文件的路径
                rel_path = os.path.relpath(root, source_folder)
                output_subdir = os.path.join(output_folder, rel_path) if rel_path != '.' else output_folder
                os.makedirs(output_subdir, exist_ok=True)
                
                # 获取文件扩展名
                file_ext = os.path.splitext(file)[1].lower()
                
                # 更新总文件计数
                conversion_results['total_files'] += 1
                
                # 检查文件是否支持
                if file_ext not in supported_formats:
                    log.write(f"跳过不支持的文件：{file_path} (格式: {file_ext})\n")
                    conversion_results['skipped_files'] += 1
                    conversion_results['conversion_details'].append({
                        'file': file_path,
                        'status': 'skipped',
                        'reason': f'不支持的文件格式: {file_ext}'
                    })
                    continue
                
                # 转换文件
                log.write(f"开始转换文件：{file_path}\n")
                file_start_time = time.time()
                
                try:
                    # 执行转换
                    md_content = docling_converter.convert_to_markdown(file_path)
                    
                    # 创建输出文件名
                    output_file = os.path.join(output_subdir, os.path.splitext(file)[0] + '.md')
                    
                    # 写入转换结果
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    
                    # 计算转换时间
                    file_process_time = time.time() - file_start_time
                    
                    # 更新日志
                    log.write(f"成功转换：{file_path} -> {output_file} (用时: {file_process_time:.2f}秒)\n")
                    log.write("-"*50 + "\n")
                    
                    # 更新计数
                    conversion_results['converted_files'] += 1
                    conversion_results['conversion_details'].append({
                        'file': file_path,
                        'status': 'success',
                        'output': output_file,
                        'processing_time': round(file_process_time, 2)
                    })
                    
                except Exception as e:
                    # 处理转换错误
                    log.write(f"转换失败：{file_path} - 错误: {str(e)}\n")
                    log.write("-"*50 + "\n")
                    
                    # 更新计数
                    conversion_results['failed_files'] += 1
                    conversion_results['conversion_details'].append({
                        'file': file_path,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
                    logger.error(f"批量转换：文件{file_path}转换失败: {str(e)}")
                    logger.error(traceback.format_exc())
        
        # 写入总结
        total_time = time.time() - start_time
        log.write("\n" + "="*50 + "\n")
        log.write(f"转换完成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"总用时：{total_time:.2f}秒\n")
        log.write(f"总文件数：{conversion_results['total_files']}\n")
        log.write(f"成功转换：{conversion_results['converted_files']}个文件\n")
        log.write(f"跳过文件：{conversion_results['skipped_files']}个文件\n")
        log.write(f"转换失败：{conversion_results['failed_files']}个文件\n")
    
    # 返回API响应
    response = {
        'source_folder': source_folder,
        'output_folder': output_folder,
        'log_file': log_file,
        'total_time': round(total_time, 2),
        'results': conversion_results
    }
    
    logger.info(f"API调用（批量Docling）：完成文件夹转换，总耗时: {total_time:.2f}秒")
    return jsonify(response)

def convert_file_to_utf8(file_path, file_ext=None):
    """尝试将文件转换为UTF-8编码"""
    # 文本类文件直接处理
    text_file_exts = ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm']
    if file_ext in text_file_exts:
        _convert_text_file_to_utf8(file_path)
        return
    
    # 对于二进制文件，根据类型进行特殊处理
    if file_ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf']:
        logger.info(f"二进制文件 {file_ext} 将在转换过程中处理编码")
        return
    
    # 默认作为文本文件处理
    logger.info("未知文件类型，尝试作为文本文件处理")
    try:
        _convert_text_file_to_utf8(file_path)
    except Exception as e:
        logger.warning(f"作为文本文件处理失败: {str(e)}")

def _convert_text_file_to_utf8(file_path):
    """将文本文件转换为UTF-8编码"""
    # 检测文件编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'cp936', 'latin-1', 'cp1252']
    detected_encoding = None
    content = None
    
    # 读取文件内容
    with open(file_path, 'rb') as f:
        raw_content = f.read()
    
    # 尝试不同的编码
    for encoding in encodings:
        try:
            content = raw_content.decode(encoding)
            # 检查是否有中文字符，如果有则可能是正确的编码
            if any('\u4e00' <= char <= '\u9fff' for char in content):
                detected_encoding = encoding
                logger.info(f"检测到文件编码: {encoding}")
                break
            # 如果没有中文字符，但解码成功，记录为可能的编码
            if detected_encoding is None:
                detected_encoding = encoding
        except UnicodeDecodeError:
            continue
    
    # 如果没有检测到编码，使用默认的utf-8 with errors='replace'
    if detected_encoding is None:
        logger.warning("无法检测文件编码，使用utf-8替换模式")
        content = raw_content.decode('utf-8', errors='replace')
        detected_encoding = 'utf-8 (with replacement)'
    
    # 如果检测到的编码不是utf-8，则转换并重写文件
    if detected_encoding.lower() != 'utf-8':
        logger.info(f"将文件从 {detected_encoding} 转换为 UTF-8")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info("文件编码转换完成")
    else:
        logger.info("文件已经是UTF-8编码，无需转换")

@app.errorhandler(413)
def request_entity_too_large(error):
    logger.warning("上传文件过大，超过大小限制")
    return jsonify({'error': '上传文件过大，请确保文件小于50MB'}), 413

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"服务器内部错误: {str(error)}")
    return jsonify({'error': '服务器内部错误，请稍后重试'}), 500

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'error': '请求的资源不存在'}), 404

# API：使用Marker转换为Markdown
@app.route('/api/convert-to-md-marker', methods=['POST'])
def api_convert_md_marker():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(Marker)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("API调用(Marker)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(Marker)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 获取marker转换器
    marker_converter = converter_factory.get_converter('marker')
    if not hasattr(marker_converter, 'is_available') or not marker_converter.is_available:
        logger.error("API调用(Marker)：Marker转换器不可用")
        return jsonify({'error': 'Marker转换器不可用，请确认已安装marker-pdf库'}), 500
    
    # 检查文件扩展名是否支持
    if not marker_converter.is_format_supported(file_ext):
        error_msg = f"Marker不支持的文件类型: {file_ext}"
        logger.warning(f"API调用(Marker)：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(Marker)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(Marker)：文件大小: {file_size / 1024:.2f} KB")
        
        # 使用Marker转换为Markdown
        logger.info(f"API调用(Marker)：开始转换文件: {filename}")
        markdown_text = marker_converter.convert_to_markdown(file_path)
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(Marker)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        try:
            os.remove(file_path)
            logger.info(f"API调用(Marker)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(Marker)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"API调用(Marker)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(Marker)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
        
        # 返回API响应
        return jsonify({
            'text': markdown_text,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2),
            'converter': 'marker'
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(Marker)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(Marker)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(Marker)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：使用Marker转换为HTML
@app.route('/api/convert-to-html-marker', methods=['POST'])
def api_convert_html_marker():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(Marker HTML)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("API调用(Marker HTML)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(Marker HTML)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 获取marker转换器
    marker_converter = converter_factory.get_converter('marker')
    if not hasattr(marker_converter, 'is_available') or not marker_converter.is_available:
        logger.error("API调用(Marker HTML)：Marker转换器不可用")
        return jsonify({'error': 'Marker转换器不可用，请确认已安装marker-pdf库'}), 500
    
    # 检查文件扩展名是否支持
    if not marker_converter.is_format_supported(file_ext):
        error_msg = f"Marker不支持的文件类型: {file_ext}"
        logger.warning(f"API调用(Marker HTML)：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(Marker HTML)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(Marker HTML)：文件大小: {file_size / 1024:.2f} KB")
        
        # 使用Marker转换为HTML
        logger.info(f"API调用(Marker HTML)：开始转换文件: {filename}")
        html_content = marker_converter.convert_to_html(file_path)
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(Marker HTML)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        try:
            os.remove(file_path)
            logger.info(f"API调用(Marker HTML)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(Marker HTML)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"API调用(Marker HTML)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(Marker HTML)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
        
        # 返回API响应
        return jsonify({
            'html': html_content,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2),
            'converter': 'marker'
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(Marker HTML)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(Marker HTML)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(Marker HTML)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：使用Marker转换为JSON
@app.route('/api/convert-to-json-marker', methods=['POST'])
def api_convert_json_marker():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(Marker JSON)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("API调用(Marker JSON)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(Marker JSON)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 获取marker转换器
    marker_converter = converter_factory.get_converter('marker')
    if not hasattr(marker_converter, 'is_available') or not marker_converter.is_available:
        logger.error("API调用(Marker JSON)：Marker转换器不可用")
        return jsonify({'error': 'Marker转换器不可用，请确认已安装marker-pdf库'}), 500
    
    # 检查文件扩展名是否支持
    if not marker_converter.is_format_supported(file_ext):
        error_msg = f"Marker不支持的文件类型: {file_ext}"
        logger.warning(f"API调用(Marker JSON)：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(Marker JSON)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(Marker JSON)：文件大小: {file_size / 1024:.2f} KB")
        
        # 使用Marker转换为JSON
        logger.info(f"API调用(Marker JSON)：开始转换文件: {filename}")
        json_content = marker_converter.convert_to_json(file_path)
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(Marker JSON)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        try:
            os.remove(file_path)
            logger.info(f"API调用(Marker JSON)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(Marker JSON)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"API调用(Marker JSON)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(Marker JSON)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
        
        # 返回API响应
        return jsonify({
            'json': json_content,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2),
            'converter': 'marker'
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(Marker JSON)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(Marker JSON)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(Marker JSON)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    logger.info("应用启动")
    app.run(host='0.0.0.0', port=5000,debug=True)
    logger.info("应用关闭") 