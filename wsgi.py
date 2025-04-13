"""
WSGI入口文件，用于生产环境部署
"""
from app import app, logger

if __name__ == '__main__':
    logger.info("应用启动")
    app.run(host='0.0.0.0', port=5000)
    logger.info("应用关闭") 