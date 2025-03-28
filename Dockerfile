FROM python:3.12

LABEL maintainer="X2Knowledge Team <support@x2knowledge.com>"
LABEL version="2.1.0"
LABEL description="X2Knowledge - 知识提取器工具 Docker 映像"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1 \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建上传和日志目录并设置权限
RUN mkdir -p /app/uploads /app/logs \
    && chmod 777 /app/uploads /app/logs

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"] 