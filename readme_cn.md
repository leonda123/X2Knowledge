![LOGO](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/x2knowledge-logo.png)

# X2Knowledge V0.4.1 - 知识提取器工具

[<a href="/readme_cn.md">中文(简体)</a>] | [<a href="/readme.md">English</a>] 

X2Knowledge 是一个高效的开源知识提取器工具，专为企业知识库建设而设计。它支持将PDF、Word、PPT、Excel、WAV、MP3等多种格式的文件智能转换为结构化的TXT或Markdown格式，帮助用户快速将各类文档资料标准化地录入企业知识库系统。通过先进的格式解析和内容提取技术，该项目显著提升知识转换的效率和准确性，是RAG（检索增强生成）应用和企业知识管理的理想预处理工具。

![设计示意图](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/x2knowledge_cn.png)

[演示网站](http://115.190.8.7:8080/)：http://115.190.8.7:8080/ 服务器性能不佳，请在本地测试使用docling接口，服务器没有cuda环境！

由于个人或企业文档的多样性，在构建知识库的过程中，文档的处理如何在RAG/Agent的应用中能达到预期的效果，起到至关重要的作用。但是随着AI技术的发展，不断开源和商用的工具涌现，如何在选择和使用这些工具成为了一大难题。

本项目秉着：1.要么免费、2.要么速度快、3.要么准确率高、4.接口统一、5.持续更新的原则。
同时也欢迎大家一起讨论，后续计划在本人有限的时间内将olmOCR、MinerU、Marker等等优秀的开源项目接入到项目中。

大家敬请期待！

## 注意！默认marker不启用（离线模型文件过大），需要手动在requirements.txt中开启。

## 功能特点

- **多种转换引擎**
  - **MarkItDown**：针对Office文档（DOCX、XLSX、PPTX、CSV）优化，速度快、效率高
  - **Docling**：增强的PDF转换功能，提供更好的表格识别和VLM能力
  - **Marker**：高精度文档转换，优秀的表格、公式和图片提取能力

- **将多种文件格式转换为文本或Markdown**
  - 支持Word (.doc, .docx)、Excel (.xls, .xlsx)、PowerPoint (.ppt, .pptx)、PDF、文本文件等
  - 在Markdown转换模式下保持文档结构
  - 通过OCR从图像中提取文本

- **多种输出格式**
  - **文本**：简单的纯文本提取
  - **Markdown**：保留文档结构，包括标题、列表和表格
  - **HTML**：带有图片和公式支持的完整HTML输出
  - **JSON**：带有元数据的结构化文档表示

- **OCR支持**
  - 自动从文档中嵌入的图像提取文本
  - 适用于Word、PowerPoint和PDF文件中的图像

- **音频转换**
  - 将音频文件(.mp3, .wav)转换为文本/Markdown描述
  - 提取元数据，包括时长、声道和采样率

- **UTF-8编码**
  - 自动将文档转换为UTF-8编码
  - 解决中文字符显示问题
  - 无需手动配置编码

- **大文件支持**
  - 支持高达50MB的文件
  - 高效处理大型文档

## 转换器对比

以下是X2Knowledge中提供的三种文档转换引擎的比较：

| 特性 | MarkItDown | Docling | Marker |
|------|------------|---------|--------|
| **速度** | ★★★★★ (最快) | ★★★☆☆ (中等) | ★★☆☆☆ (较慢) |
| **准确性** | ★★★☆☆ (良好) | ★★★★☆ (很好) | ★★★★★ (优秀) |
| **表格处理** | ★★★☆☆ (基础) | ★★★★☆ (高级) | ★★★★★ (卓越) |
| **公式支持** | ★☆☆☆☆ (有限) | ★★★☆☆ (中等) | ★★★★★ (优秀) |
| **图片提取** | ★☆☆☆☆ (基本OCR) | ★★★★☆ (VLM支持) | ★★★★★ (详细) |
| **资源占用** | ★★★★★ (最小) | ★★☆☆☆ (大量) | ★★☆☆☆ (大量) |
| **最适用于** | Office文档 | PDF文档 | 包含表格和公式的复杂文档 |
| **GPU加速** | 否 | 是 | 是 |
| **支持的格式** | DOC, DOCX, XLS, XLSX, PPT, PPTX, PDF, TXT, MD | PDF, DOCX, XLSX, PPTX, 图片, HTML | PDF, DOCX, XLSX, PPTX, 图片, HTML |
| **输出格式** | 文本, Markdown | 文本, Markdown, HTML, JSON | 文本, Markdown, HTML, JSON |

选择最适合您需求的转换器：
- **MarkItDown**：当您需要快速转换Office文档并保持较好的保真度时
- **Docling**：当您需要更好地处理带有表格和图像的PDF文档时
- **Marker**：当您需要对复杂文档（尤其是包含公式和表格的文档）进行最高精度的转换时

## 使用方法

1. 选择转换模式（文本或Markdown）
2. 在使用Markdown模式时，选择MarkItDown（默认）、Docling或Marker转换器
   - MarkItDown：针对Office文档优化，处理速度更快
   - Docling：针对PDF文件和复杂表格布局效果更好
   - Marker：对于包含复杂元素（如表格、公式和图片）的文档具有最高精度
3. 上传您的文档（或拖放）
4. 查看、复制或下载转换结果
5. 使用Markdown预览功能查看格式化结果（使用Markdown模式时）

## REST API

本工具提供了REST API，以便程序化访问：

- **文本转换**：`POST /api/convert`
- **文本转换并保存文件**：`POST /api/convert-file`
- **Markdown转换（MarkItDown）**：`POST /api/convert-to-md`
- **Markdown转换并保存文件（MarkItDown）**：`POST /api/convert-to-md-file`
- **Markdown转换（Docling）**：`POST /api/convert-to-md-docling`
- **Markdown转换并保存文件（Docling）**：`POST /api/convert-to-md-file-docling`
- **HTML转换（Docling）**：`POST /api/convert-to-html-docling`
- **Markdown转换（Marker）**：`POST /api/convert-to-md-marker`
- **Markdown转换并保存文件（Marker）**：`POST /api/convert-to-md-file-marker`
- **HTML转换（Marker）**：`POST /api/convert-to-html-marker`
- **JSON转换（Marker）**：`POST /api/convert-to-json-marker`

要测试和查看API文档，请使用网页界面中的"API测试"按钮访问Swagger UI。

## 支持的格式

### 输入格式
- **Office文档**：DOC、DOCX、XLS、XLSX、PPT、PPTX、CSV
- **文本/标记语言**：PDF、TXT、MD、HTML、XHTML、EPUB
- **图像**：PNG、JPEG、TIFF、BMP
- **音频**：MP3、WAV

### 输出格式
- **纯文本**
- **Markdown**
- **HTML**
- **JSON**

## 系统截图

###界面

#### 主页
![主页](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/home_cn.png)
#### API调用
![API调用](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/API_cn.png)
#### 原始格式
![原始格式](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/original%20format_cn.png)
#### MD格式
![MD格式](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/MD%20format_cn.png)
### 效果
#### WORD文件
![WORD文件](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/word1.png)
#### WORD转换效果
![WORD转换效果](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/word2.png)
#### WORD中表格转换效果
![WORD中表格转换效果](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/word4.png)
#### Execel效果
![Execel效果](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/excel2.png)
#### PPT效果
![PPT效果](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/ppt1.png)
#### docling pdf zhuanhu md
![docling pdf to md](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/docling_pdf_md.png)

## 安装与部署

### 本地安装

#### 要求

- Python 3.11
- Flask
- pytesseract（用于OCR功能）
- Tesseract OCR引擎
- MarkItDown库
- Docling库（可选，用于增强PDF转换）
- Marker库（可选，用于高精度文档转换）

#### 设置

1. 克隆仓库：
   ```
   git clone https://github.com/leonda123/X2Knowledge.git
   cd X2Knowledge
   ```

2. 创建虚拟环境并安装依赖：
   ```
   python -m venv venv
   source venv/bin/activate  # 在Windows上：venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 安装可选的转换引擎：
   ```
   # 安装Docling支持
   pip install docling
   
   # 安装Marker支持
   pip install marker-pdf
   # 为支持更多格式安装额外组件
   pip install marker-pdf[full]
   ```

4. 安装Tesseract OCR引擎（用于OCR功能）：
   - Windows：从[GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)下载并安装
   - macOS：`brew install tesseract`
   - Linux：`sudo apt-get install tesseract-ocr`

5. 运行应用程序：
   ```
   python app.py
   ```

6. 打开Web浏览器并导航至`http://127.0.0.1:5000/`

### Docker部署

使用Docker可以更方便地部署X2Knowledge，避免环境配置问题。

#### 使用Docker Compose

1. 克隆仓库：
   ```
   git clone https://github.com/leonda123/X2Knowledge.git
   git clone https://gitee.com/leonda/X2Knowledge.git
   cd X2Knowledge
   ```

2. 构建并启动容器：
   ```
   docker-compose up -d
   ```

3. 访问应用程序：
   打开Web浏览器并导航至`http://localhost:5000/`

#### 手动构建Docker映像

1. 构建Docker映像：
   ```
   docker build -t x2knowledge .
   ```

2. 运行容器：
   ```
   docker run -d -p 5000:5000 --name x2knowledge -v ./uploads:/app/uploads -v ./logs:/app/logs x2knowledge
   ```

3. 访问应用程序：
   打开Web浏览器并导航至`http://localhost:5000/`

## 项目优势

- **多种转换引擎**：针对不同类型的文档选择最适合的引擎 - MarkItDown适合Office文档，Docling适合PDF，Marker适合高精度需求
- **高性能文档处理**：优化的文档解析引擎，能够高效处理各种格式的文档
- **低资源消耗**：即使在配置较低的服务器上也能流畅运行
- **准确的结构保留**：特别是在Markdown转换中，能够准确保留文档的原始结构
- **多平台支持**：可在Windows、macOS和Linux系统上部署
- **灵活的API接口**：提供RESTful API，方便与其他系统集成
- **无外部依赖的部署**：除OCR功能外，核心功能无需外部服务支持
- **容器化部署**：支持Docker部署，简化环境配置

## 已知问题

- 较旧的Word文档（.doc格式）处理时间可能较长；建议在上传前将其转换为.docx格式
- 一些复杂的文档布局在Markdown转换中可能无法完美保留
- OCR准确性取决于图像质量和文本复杂性
- Docling在CUDA加速环境下性能最佳，但如果不可用会回退到CPU模式
- Marker需要PyTorch，并且可能需要特定的PyTorch安装以支持GPU加速

## 未来计划

### 技术路线规划：

- 短期：集成OcrmyPDF（文档OCR）、MinerU（非结构化数据处理）、改进Marker集成
- 中期：开发智能路由模块，实现文档类型自适配处理
- 长期：为构建垂直领域大模型，支持垂直领域知识的蒸馏
- 首次发布，支持文本转换
- OCR功能
- UTF-8编码转换

## 许可证

本项目采用Apache-2.0许可证——详见LICENSE文件。

## 致谢

- [pytesseract](https://github.com/madmaze/pytesseract)提供OCR功能
- [Flask](https://flask.palletsprojects.com/)Web框架
- [Markidown](https://github.com/microsoft/markitdown.git)用于文档到Markdown的转换
- [Docling](https://github.com/docling-project/docling/)用于增强的PDF转换
- [marked.js](https://marked.js.org/)用于Markdown渲染
- [highlight.js](https://highlightjs.org/)用于代码语法高亮
- 各种文档处理库

---

##联系方式
- QQ：176942734
- 邮箱：dada_jiu45@hotmail.com

##如果觉得不错就请我喝个咖啡吧~
![打赏码](https://gitee.com/leonda/X2Knowledge/raw/main/screenshot/dashang.png)


项目链接：[GitHub](https://github.com/leonda123/X2Knowledge.git) | [Gitee](https://gitee.com/leonda/X2Knowledge.git) | [GitCode](https://gitcode.com/leonda/X2Knowledge.git) 
