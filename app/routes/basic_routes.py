"""
基础路由模块，包含网站基本页面的路由
"""
from flask import Blueprint, render_template, jsonify
import os
from app import logger

# 创建蓝图
bp = Blueprint('basic', __name__)

@bp.route('/')
def index():
    """首页路由"""
    logger.info("访问首页")
    return render_template('index.html')

@bp.route('/OCR安装说明.md')
def ocr_installation():
    """OCR安装说明路由"""
    logger.info("访问OCR安装说明")
    try:
        with open('OCR安装说明.md', 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/markdown'}
    except Exception as e:
        logger.error(f"读取OCR安装说明失败: {str(e)}")
        return "OCR安装说明文件不存在", 404

@bp.route('/api-docs')
def api_docs():
    """API文档页面路由"""
    logger.info("访问API文档页面")
    return render_template('api-docs.html')

@bp.route('/about')
def about_page():
    """关于页面路由"""
    logger.info("访问关于页面")
    return render_template('about.html') 