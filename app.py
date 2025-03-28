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
    logger.warning(f"页面未找到: {request.path}")
    return jsonify({'error': '页面未找到'}), 404

if __name__ == '__main__':
    logger.info("应用启动")
    app.run(host='0.0.0.0', port=5000,debug=True)
    logger.info("应用关闭") 