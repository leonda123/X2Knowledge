"""
开发环境运行脚本
"""
from app import app, logger

if __name__ == '__main__':
    logger.info("开发环境应用启动")
    app.run(host='0.0.0.0', port=5000, debug=True)
    logger.info("应用关闭") 