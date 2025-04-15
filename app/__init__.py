"""
X2Knowledge 应用包初始化文件
"""
from flask import Flask
import os
import logging
from datetime import datetime
from flasgger import Swagger

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

# 创建Flask应用
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 限制上传文件大小为50MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STORAGE_FOLDER'] = 'storage'  # 添加存储文件夹配置

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# 确保存储文件夹存在
os.makedirs(app.config['STORAGE_FOLDER'], exist_ok=True)

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
        "title": "X2Knowledge API",
        "description": "用于文档转换的API接口",
        "version": "1.0.0",
        "contact": {
            "name": "X2Knowledge API",
        }
    },
    "x-i18n": {
        "zh": {
            "info": {
                "title": "X2Knowledge API",
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

# 初始化Swagger
swagger = Swagger(app, config=swagger_config, template=swagger_template)

# 导入路由模块
from app.routes import basic_routes, api_routes, docling_routes, web_routes

# 注册蓝图
app.register_blueprint(basic_routes.bp)
app.register_blueprint(api_routes.bp, url_prefix='/api')
app.register_blueprint(docling_routes.bp)
app.register_blueprint(web_routes.bp) 