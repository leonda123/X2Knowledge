import os
import logging
import tempfile
import traceback
from PIL import Image
import pytesseract
import sys
import io
from pdf2image import convert_from_path

# 获取日志记录器
logger = logging.getLogger(__name__)

# 检查是否安装了Tesseract OCR
HAS_TESSERACT = False
try:
    # 尝试获取Tesseract版本
    tesseract_version = pytesseract.get_tesseract_version()
    HAS_TESSERACT = True
    logger.info(f"成功检测到Tesseract OCR，版本: {tesseract_version}")
except Exception as e:
    logger.warning(f"未检测到Tesseract OCR: {str(e)}")
    logger.warning("OCR功能将不可用，请安装Tesseract OCR: https://github.com/tesseract-ocr/tesseract")

def extract_text_from_image(image_path, lang='chi_sim+eng'):
    """从图片中提取文本"""
    if not HAS_TESSERACT:
        logger.warning("Tesseract OCR未安装，无法提取图片文本")
        return "[图片文本提取失败: Tesseract OCR未安装]"
    
    try:
        logger.info(f"开始从图片提取文本: {image_path}")
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            logger.error(f"图片文件不存在: {image_path}")
            return "[图片不存在]"
        
        # 打开图片
        image = Image.open(image_path)
        
        # 记录图片信息
        logger.info(f"图片尺寸: {image.size}, 格式: {image.format}, 模式: {image.mode}")
        
        # 使用pytesseract提取文本
        text = pytesseract.image_to_string(image, lang=lang)
        
        # 检查提取结果
        if text.strip():
            # 确保OCR识别的文本使用UTF-8编码
            if any(ord(c) > 127 for c in text):
                logger.debug("OCR识别的文本包含非ASCII字符，确保UTF-8编码")
                
                # 尝试检测编码并转换为UTF-8
                try:
                    # 将文本编码为bytes，然后解码为UTF-8
                    text_bytes = text.encode('utf-8', errors='replace')
                    text = text_bytes.decode('utf-8')
                    logger.debug("成功将OCR文本转换为UTF-8编码")
                except Exception as e:
                    logger.warning(f"OCR文本编码转换失败: {str(e)}")
            
            logger.info(f"成功从图片提取文本，共 {len(text)} 个字符")
            return text.strip()
        else:
            logger.warning("图片中未检测到文本")
            return "[图片中未检测到文本]"
    
    except Exception as e:
        error_msg = f"图片文本提取失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return f"[{error_msg}]"

def extract_text_from_image_bytes(image_bytes, lang='chi_sim+eng'):
    """从图片字节数据中提取文本"""
    if not HAS_TESSERACT:
        logger.warning("Tesseract OCR未安装，无法提取图片文本")
        return "[图片文本提取失败: Tesseract OCR未安装]"
    
    try:
        logger.info("开始从图片字节数据提取文本")
        
        # 从字节数据创建图片对象
        image = Image.open(io.BytesIO(image_bytes))
        
        # 记录图片信息
        logger.info(f"图片尺寸: {image.size}, 格式: {image.format}, 模式: {image.mode}")
        
        # 使用pytesseract提取文本
        text = pytesseract.image_to_string(image, lang=lang)
        
        # 检查提取结果
        if text.strip():
            # 确保OCR识别的文本使用UTF-8编码
            if any(ord(c) > 127 for c in text):
                logger.debug("OCR识别的文本包含非ASCII字符，确保UTF-8编码")
                
                # 尝试检测编码并转换为UTF-8
                try:
                    # 将文本编码为bytes，然后解码为UTF-8
                    text_bytes = text.encode('utf-8', errors='replace')
                    text = text_bytes.decode('utf-8')
                    logger.debug("成功将OCR文本转换为UTF-8编码")
                except Exception as e:
                    logger.warning(f"OCR文本编码转换失败: {str(e)}")
            
            logger.info(f"成功从图片提取文本，共 {len(text)} 个字符")
            return text.strip()
        else:
            logger.warning("图片中未检测到文本")
            return "[图片中未检测到文本]"
    
    except Exception as e:
        error_msg = f"图片文本提取失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return f"[{error_msg}]"

def extract_text_from_pdf_images(pdf_path, lang='chi_sim+eng'):
    """从PDF文件中提取图片并识别文本"""
    if not HAS_TESSERACT:
        logger.warning("Tesseract OCR未安装，无法提取PDF图片文本")
        return []
    
    try:
        logger.info(f"开始从PDF提取图片文本: {pdf_path}")
        
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            logger.error(f"PDF文件不存在: {pdf_path}")
            return []
        
        # 创建临时目录存储图片
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"创建临时目录: {temp_dir}")
            
            # 将PDF转换为图片
            try:
                logger.info("将PDF转换为图片")
                images = convert_from_path(pdf_path)
                logger.info(f"成功将PDF转换为 {len(images)} 张图片")
            except Exception as e:
                logger.error(f"PDF转图片失败: {str(e)}")
                return []
            
            # 处理每张图片
            results = []
            for i, image in enumerate(images):
                # 保存图片到临时文件
                image_path = os.path.join(temp_dir, f"page_{i+1}.png")
                image.save(image_path, "PNG")
                
                # 提取文本
                logger.info(f"处理第 {i+1} 页图片")
                text = extract_text_from_image(image_path, lang)
                
                # 添加结果
                if text and text != "[图片中未检测到文本]":
                    results.append({
                        'page': i+1,
                        'text': text
                    })
            
            logger.info(f"从PDF中提取了 {len(results)} 页图片文本")
            return results
    
    except Exception as e:
        error_msg = f"PDF图片文本提取失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return [] 