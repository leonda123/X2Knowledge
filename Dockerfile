FROM python:3.13.2

LABEL maintainer="X2Knowledge Team <dadajiu45@gmail.com>"
LABEL version="0.4.1"
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
    libspatialindex-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 升级pip并安装依赖
RUN pip install --upgrade pip && \
    # 确保关键依赖先安装
    pip install --no-cache-dir markupsafe flask werkzeug jinja2 typing_extensions lxml pydantic docling docling_core filetype pydantic-settings tqdm scipy rtree beautifulsoup4 marko pypdfium2 pylatexenc pluggy typer docling-parse docling-ibm-models transformers jsonlines numpy safetensors easyocr && \
    # 手动安装markitdown
    pip install --no-cache-dir markitdown && \
    # 手动安装pydub及其依赖
    pip install --no-cache-dir pydub && \
    # 尝试直接安装，忽略哈希检查
    pip install --no-cache-dir --no-deps -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt || \
    # 使用国内镜像源安装
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 创建上传和日志目录并设置权限
RUN mkdir -p /app/uploads /app/logs \
    && chmod 777 /app/uploads /app/logs

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"] 