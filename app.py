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
# 导入flasgger相关模块
from flasgger import Swagger, swag_from

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

# 配置Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/",
    "uiversion": 3,
    "ui_params": {
        "defaultModelsExpandDepth": -1,  # 不显示Models部分
        "docExpansion": "list", # 默认展开列表
        "displayRequestDuration": True, # 显示请求持续时间
        "defaultModelRendering": "model" # 使用模型渲染
    }
}

# 添加国际化支持
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "文档转换API",
        "description": "用于文档转换的API接口",
        "version": "1.0.0",
        "contact": {
            "name": "X2Knowledge API",
        }
    },
    "x-i18n": {
        "zh": {
            "info": {
                "title": "文档转换API",
                "description": "用于文档转换的API接口"
            }
        },
        "en": {
            "info": {
                "title": "Document Conversion API",
                "description": "API interfaces for document conversion"
            }
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

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

# API: 基本文本转换
@app.route('/api/convert', methods=['POST'])
@swag_from('swagger_docs/convert.yml')
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
@swag_from('swagger_docs/convert_to_md.yml')
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
@swag_from('swagger_docs/convert_to_md_docling.yml')
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
@swag_from('swagger_docs/convert_to_html_docling.yml')
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

# API：使用Marker转换为Markdown
@app.route('/api/convert-to-md-marker', methods=['POST'])
@swag_from('swagger_docs/convert_to_md_marker.yml')
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
@swag_from('swagger_docs/convert_to_html_marker.yml')
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
@swag_from('swagger_docs/convert_to_json_marker.yml')
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
            'processing_time': round(processing_time, 2)
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

# API：将文件转换为文本并保存到指定目录
@app.route('/api/convert-file', methods=['POST'])
@swag_from('swagger_docs/convert_file.yml')
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
        
        # 对所有文件类型尝试转换编码为UTF-8
        try:
            logger.info("API调用(保存文本)：尝试转换文件编码为UTF-8")
            convert_file_to_utf8(file_path, file_ext)
        except Exception as e:
            logger.warning(f"API调用(保存文本)：转换编码失败: {str(e)}，将使用原始文件")
        
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
            try:
                os.remove(file_path)
                logger.info(f"API调用(保存文本)：临时文件已删除: {file_path}")
            except Exception as e:
                logger.warning(f"API调用(保存文本)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            
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
        try:
            os.remove(file_path)
            logger.info(f"API调用(保存文本)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(保存文本)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            # 尝试强制关闭文件句柄后再删除
            try:
                import gc
                gc.collect()  # 触发垃圾回收，释放未关闭的文件句柄
                os.remove(file_path)
                logger.info(f"API调用(保存文本)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(保存文本)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
                # 不再尝试删除，避免阻塞程序
        
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
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(保存文本)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(保存文本)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：将文件转换为Markdown并保存到指定目录
@app.route('/api/convert-to-md-file', methods=['POST'])
@swag_from('swagger_docs/convert_to_md_file.yml')
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
        try:
            os.remove(file_path)
            logger.info(f"API调用(保存MD)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(保存MD)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"API调用(保存MD)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(保存MD)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
        
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
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(保存MD)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(保存MD)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：使用Docling将文件转换为Markdown并保存到指定目录
@app.route('/api/convert-to-md-file-docling', methods=['POST'])
@swag_from('swagger_docs/convert_to_md_file_docling.yml')
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
        try:
            os.remove(file_path)
            logger.info(f"API调用(Docling保存)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(Docling保存)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"API调用(Docling保存)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(Docling保存)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
        
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
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(Docling保存)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(Docling保存)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

# API：使用Marker将文件转换为Markdown并保存到指定目录
@app.route('/api/convert-to-md-file-marker', methods=['POST'])
@swag_from('swagger_docs/convert_to_md_file_marker.yml')
def api_convert_md_file_marker():
    start_time = time.time()
    
    if 'file' not in request.files:
        logger.warning("API调用(Marker保存)：没有文件上传")
        return jsonify({'error': '没有文件上传'}), 400
    
    if 'output_dir' not in request.form:
        logger.warning("API调用(Marker保存)：未指定输出目录")
        return jsonify({'error': '未指定输出目录'}), 400
    
    file = request.files['file']
    output_dir = request.form['output_dir']
    
    if file.filename == '':
        logger.warning("API调用(Marker保存)：未选择文件")
        return jsonify({'error': '未选择文件'}), 400
    
    # 检查输出目录是否存在，不存在则创建
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.info(f"API调用(Marker保存)：创建输出目录: {output_dir}")
        except Exception as e:
            error_msg = f"无法创建输出目录: {str(e)}"
            logger.error(f"API调用(Marker保存)：{error_msg}")
            return jsonify({'error': error_msg}), 500
    
    # 获取文件扩展名
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    logger.info(f"API调用(Marker保存)：接收到文件: {filename}, 类型: {file_ext}")
    
    # 获取marker转换器
    marker_converter = converter_factory.get_converter('marker')
    if not hasattr(marker_converter, 'is_available') or not marker_converter.is_available:
        logger.error("API调用(Marker保存)：Marker转换器不可用")
        return jsonify({'error': 'Marker转换器不可用，请确认已安装marker-pdf库'}), 500
    
    # 检查文件扩展名是否支持
    if not marker_converter.is_format_supported(file_ext):
        error_msg = f"Marker不支持的文件类型: {file_ext}"
        logger.warning(f"API调用(Marker保存)：{error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 保存上传的文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
        logger.info(f"API调用(Marker保存)：文件保存成功: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"API调用(Marker保存)：文件大小: {file_size / 1024:.2f} KB")
        
        # 使用Marker转换为Markdown
        logger.info(f"API调用(Marker保存)：开始转换文件: {filename}")
        markdown_text = marker_converter.convert_to_markdown(file_path)
        
        # 保存转换后的Markdown到输出目录
        output_filename = os.path.splitext(filename)[0] + '.md'
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        logger.info(f"API调用(Marker保存)：Markdown已保存到: {output_path}")
        
        processing_time = time.time() - start_time
        logger.info(f"API调用(Marker保存)：文件转换完成，耗时: {processing_time:.2f}秒")
        
        # 删除临时文件
        try:
            os.remove(file_path)
            logger.info(f"API调用(Marker保存)：临时文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"API调用(Marker保存)：无法删除临时文件: {file_path}, 原因: {str(e)}")
            try:
                import gc
                gc.collect()
                os.remove(file_path)
                logger.info(f"API调用(Marker保存)：临时文件已删除(第二次尝试): {file_path}")
            except Exception as e2:
                logger.error(f"API调用(Marker保存)：无法删除临时文件(第二次尝试): {file_path}, 原因: {str(e2)}")
        
        # 返回API响应
        return jsonify({
            'output_path': output_path,
            'filename': filename,
            'file_size': file_size,
            'processing_time': round(processing_time, 2),
            'converter': 'marker'
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"API调用(Marker保存)：转换失败: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 出错时删除临时文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"API调用(Marker保存)：清理临时文件: {file_path}")
            except Exception as del_e:
                logger.warning(f"API调用(Marker保存)：无法删除临时文件: {file_path}, 原因: {str(del_e)}")
        
        return jsonify({
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

@app.route('/about')
def about_page():
    logger.info("访问关于页面")
    return render_template('about.html')

if __name__ == '__main__':
    logger.info("应用启动")
    app.run(host='0.0.0.0', port=5000,debug=True)
    logger.info("应用关闭") 