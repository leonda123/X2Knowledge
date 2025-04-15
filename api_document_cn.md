# X2Knowledge API文档

## 目录
- [文件转文本](#文件转文本)
  - [文件转文本](#文件转文本-1)
  - [文件转文本并保存](#文件转文本并保存)
- [使用Markitdown将文件转Markdown](#使用Markitdown将文件转Markdown)
  - [使用Markitdown将文件转Markdown](#使用Markitdown将文件转Markdown-1)
  - [使用Markitdown将文件转Markdown并保存](#使用Markitdown将文件转Markdown并保存)
- [Docling转换](#docling转换)
  - [使用Docling将文件转换为Markdown格式](#使用docling将文件转换为markdown格式)
  - [使用Docling将文件转换为Markdown格式并保存到指定目录](#使用docling将文件转换为markdown格式并保存到指定目录)
  - [使用Docling将在线文档转换为Markdown格式](#使用docling将在线文档转换为markdown格式)
  - [使用Docling将在线文档转换为Markdown格式并保存到指定目录](#使用docling将在线文档转换为markdown格式并保存到指定目录)
  - [使用Docling将文件转换为Markdown格式并导出图片](#使用docling将文件转换为markdown格式并导出图片)
  - [使用Docling将文件转换为HTML格式](#使用docling将文件转换为html格式)
  - [使用Docling提取文件中的表格并导出为指定格式](#使用docling提取文件中的表格并导出为指定格式)
- [URL转Markdown](#url转markdown)
  - [将网页URL转换为Markdown格式](#将网页url转换为markdown格式)
  - [将网页URL转换为Markdown格式并保存到指定目录](#将网页url转换为markdown格式并保存到指定目录)
- [入库预处理](#入库预处理)
  - [入库预处理：将Markdown处理为JSON和CSV格式](#入库预处理将markdown处理为json和csv格式)

---

## 文件转文本

### 文件转文本

**接口**: `POST /api/convert`

**说明**: 将各种格式的文件转换为纯文本格式

**参数**:
- `file`：要转换为文本的文件，支持doc、docx、xls、xlsx、ppt、pptx、pdf、txt、md等格式 (必需)

**响应**:
- 200: 转换成功
  ```json
  {
    "text": "转换后的文本内容"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

### 文件转文本并保存

**接口**: `POST /api/convert-file`

**说明**: 将各种格式的文件转换为纯文本格式并保存为.txt文件

**参数**:
- `file`：要转换为文本的文件 (必需)
- `output_dir`：输出文件的目录路径 (必需)

**响应**:
- 200: 转换成功
  ```json
  {
    "output_path": "保存的文件路径",
    "filename": "原始文件名",
    "file_size": "文件大小（字节）",
    "processing_time": "处理耗时（秒）"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

## 使用Markitdown将文件转Markdown

### 使用Markitdown将文件转Markdown

**接口**: `POST /api/convert-to-md`

**说明**: 使用MarkItDown引擎将各种格式的文件转换为Markdown格式

**参数**:
- `file`：要转换为Markdown的文件，支持的文件格式（PDF、DOCX、PPTX、XLSX、XLS、CSV、JSON、XML、WAV、MP3）(必需)

**响应**:
- 200: 转换成功
  ```json
  {
    "text": "转换后的Markdown文本",
    "filename": "原始文件名",
    "file_size": "文件大小（字节）",
    "processing_time": "处理耗时（秒）"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

### 使用Markitdown将文件转Markdown并保存

**接口**: `POST /api/convert-to-md-file`

**说明**: 使用MarkItDown引擎将各种格式的文件转换为Markdown格式并保存为文件

**参数**:
- `file`：要转换为Markdown的文件，支持MarkItDown支持的文件格式 (必需)
- `output_dir`：输出文件的目录路径 (必需)

**响应**:
- 200: 转换成功
  ```json
  {
    "output_path": "保存的文件路径",
    "filename": "原始文件名",
    "file_size": "文件大小（字节）",
    "processing_time": "处理耗时（秒）"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

## Docling转换

### 使用Docling将文件转换为Markdown格式

**接口**: `POST /api/convert-to-md-docling`

**说明**: 使用Docling引擎将各种格式的文件转换为Markdown格式

**参数**:
- `file`：要转换为Markdown的文件，支持的文件格式（PDF、DOCX、XLSX、PPTX、Markdown、AsciiDoc、HTML、XHTML、CSV、PNG、JPEG、TIFF、BMP）(必需)

**响应**:
- 200: 转换成功
  ```json
  {
    "text": "转换后的Markdown文本",
    "filename": "原始文件名",
    "file_size": "文件大小（字节）",
    "processing_time": "处理耗时（秒）"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

### 使用Docling将文件转换为Markdown格式并保存到指定目录

**接口**: `POST /api/convert-to-md-file-docling`

**说明**: 使用Docling引擎将各种格式的文件转换为Markdown格式并保存为文件

**参数**:
- `file`：要转换为Markdown的文件，支持的文件格式（PDF、DOCX、XLSX、PPTX、Markdown、AsciiDoc、HTML、XHTML、CSV、PNG、JPEG、TIFF、BMP）(必需)
- `output_dir`：输出文件的目录路径 (必需)

**响应**:
- 200: 转换成功
  ```json
  {
    "output_path": "保存的文件路径",
    "filename": "原始文件名",
    "file_size": "文件大小（字节）",
    "processing_time": "处理耗时（秒）",
    "converter": "使用的转换器名称"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

### 使用Docling将在线文档转换为Markdown格式

**接口**: `POST /api/convert-online-docling`

**说明**: 使用Docling引擎将在线文档（如PDF、DOC等）转换为Markdown格式，无需下载文件

**参数**:
- `url`：要转换为Markdown的在线文档URL地址，支持PDF等文档格式 (必需)
- `file_type`：文档类型(如pdf)，若URL中未包含后缀名则需要指定 (可选)

**响应**:
- 200: 转换成功
  ```json
  {
    "text": "转换后的Markdown文本",
    "url": "原始URL",
    "processing_time": "处理耗时（秒）",
    "converter": "使用的转换器"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

### 使用Docling将在线文档转换为Markdown格式并保存到指定目录

**接口**: `POST /api/convert-online-docling-save`

**说明**: 使用Docling引擎将在线文档（如PDF、DOC等）转换为Markdown格式，并保存为文件

**参数**:
- `url`：要转换为Markdown的在线文档URL地址，支持PDF等文档格式 (必需)
- `output_dir`：输出文件的目录路径 (必需)
- `file_type`：文档类型(如pdf)，若URL中未包含后缀名则需要指定 (可选)

**响应**:
- 200: 转换成功
  ```json
  {
    "output_path": "保存的文件路径",
    "url": "原始URL",
    "filename": "生成的文件名",
    "processing_time": "处理耗时（秒）",
    "converter": "使用的转换器"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

### 使用Docling将文件转换为Markdown格式并导出图片

**接口**: `POST /api/convert-to-md-images-file-docling`

**说明**: 使用Docling引擎将各种格式的文件转换为Markdown格式，并导出文档中的图片（包括页面图片、表格和图像）

**参数**:
- `file`：要转换为Markdown并提取图片的文件，支持的文件格式（PDF、DOCX、XLSX、PPTX、Markdown、AsciiDoc、HTML、XHTML、CSV、PNG、JPEG、TIFF、BMP）(必需)
- `output_dir`：输出文件的目录路径，用于保存Markdown和图片 (必需)

**响应**:
- 200: 转换成功
  ```json
  {
    "output_path": "保存的Markdown文件路径",
    "filename": "原始文件名",
    "file_size": "文件大小（字节）",
    "processing_time": "处理耗时（秒）",
    "converter": "使用的转换器名称",
    "page_count": "文档页面数量",
    "table_count": "提取的表格数量",
    "picture_count": "提取的图片数量",
    "page_images": "页面图片的路径列表",
    "table_images": "表格图片的路径列表",
    "picture_images": "图片的路径列表"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

### 使用Docling将文件转换为HTML格式

**接口**: `POST /api/convert-to-html-docling`

**说明**: 使用Docling引擎将各种格式的文件转换为HTML格式

**参数**:
- `file`：要转换为HTML的文件，支持的文件格式（PDF、DOCX、XLSX、PPTX、Markdown、AsciiDoc、HTML、XHTML、CSV、PNG、JPEG、TIFF、BMP）(必需)

**响应**:
- 200: 转换成功
  ```json
  {
    "html": "转换后的HTML文本",
    "filename": "原始文件名",
    "file_size": "文件大小（字节）",
    "processing_time": "处理耗时（秒）"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

### 使用Docling提取文件中的表格并导出为指定格式

**接口**: `POST /api/export-tables-docling`

**说明**: 使用Docling引擎从文档中提取表格，并根据需要导出为Markdown、CSV或HTML格式

**参数**:
- `file`：要提取表格的文件，支持的文件格式（PDF、DOCX、XLSX、PPTX、HTML、XHTML、CSV）(必需)
- `output_dir`：保存表格文件的输出目录路径 (必需)
- `export_formats`：导出格式，多种格式用逗号分隔，支持md、csv、html，默认全部导出 (可选)

**响应**:
- 200: 表格提取成功
  ```json
  {
    "filename": "原始文件名",
    "file_size": "文件大小（字节）",
    "processing_time": "处理耗时（秒）",
    "export_formats": ["导出的格式列表，如 md、csv、html"],
    "table_count": "提取的表格数量",
    "tables": [
      {
        "index": "表格索引（从1开始）",
        "csv_path": "CSV格式表格文件的保存路径（如果导出CSV格式）",
        "md_path": "Markdown格式表格文件的保存路径（如果导出MD格式）",
        "html_path": "HTML格式表格文件的保存路径（如果导出HTML格式）"
      }
    ]
  }
  ```
- 200 (无表格): 文档中没有表格
  ```json
  {
    "warning": "文档中未检测到表格",
    "filename": "原始文件名",
    "file_size": "文件大小（字节）",
    "processing_time": "处理耗时（秒）",
    "table_count": 0,
    "tables": []
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

## URL转Markdown

### 将网页URL转换为Markdown格式

**接口**: `POST /api/convert-url-to-md`

**说明**: 使用Docling引擎将URL网页内容转换为Markdown格式，可选择移除页眉页脚或使用CSS选择器提取特定内容

**参数**:
- `url`：要转换为Markdown的网页URL地址 (必需)
- `remove_header_footer`：是否移除网页的页眉和页脚 (可选，默认值：true)
- `selector`：CSS选择器，用于选择页面的特定内容，如 '#content'、'.article'、'main' 等 (可选)

**响应**:
- 200: 转换成功
  ```json
  {
    "text": "转换后的Markdown文本",
    "url": "原始URL",
    "processing_time": "处理耗时（秒）"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

### 将网页URL转换为Markdown格式并保存到指定目录

**接口**: `POST /api/convert-url-to-md-file`

**说明**: 使用Docling引擎将URL网页内容转换为Markdown格式，可选择移除页眉页脚或使用CSS选择器提取特定内容，并保存为文件

**参数**:
- `url`：要转换为Markdown的网页URL地址 (必需)
- `output_dir`：输出文件的目录路径 (必需)
- `remove_header_footer`：是否移除网页的页眉和页脚 (可选，默认值：true)
- `selector`：CSS选择器，用于选择页面的特定内容，如 '#content'、'.article'、'main' 等 (可选)

**响应**:
- 200: 转换成功
  ```json
  {
    "output_path": "保存的文件路径",
    "url": "原始URL",
    "filename": "生成的文件名",
    "processing_time": "处理耗时（秒）"
  }
  ```
- 400: 请求错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```

## 入库预处理

### 入库预处理：将Markdown处理为JSON和CSV格式

**接口**: `POST /preprocess-for-storage`

**说明**: 将Markdown文件或文本处理为JSON和CSV格式，用于知识库入库前的数据准备

**参数**:
- `file`：Markdown文件，与text参数二选一提供 (可选)
- `text`：Markdown文本内容，与file参数二选一提供 (可选)
- `output_dir`：输出目录路径，默认为app.config['STORAGE_FOLDER'] (可选)
- `filename`：输出文件名（不含扩展名），默认为原始文件名或时间戳 (可选)
- `format`：输出格式，可选json、csv或both（同时输出两种格式），默认为both (可选)

**处理规则**:
1. 将标题(#)收集为question，标题下的所有文本内容收集为answer，直到下一个标题的出现
2. 如果是二级及以上标题，问题标题会拼接上级标题，格式为"{上级标题},{当前标题}"
3. 只有包含内容的标题会被处理，空标题会被忽略

**输出的JSON格式**:
```json
[
  {
    "question": "标题文本",
    "answer": "标题下的内容文本"
  },
  ...
]
```

**响应**:
- 200: 处理成功
  ```json
  {
    "json_path": "生成的JSON文件路径（当format为json或both时返回）",
    "csv_path": "生成的CSV文件路径（当format为csv或both时返回）",
    "qa_count": "生成的问答对数量"
  }
  ```
- 400: 请求参数错误
  ```json
  {
    "error": "错误信息"
  }
  ```
- 500: 服务器内部错误
  ```json
  {
    "error": "错误信息",
    "details": "详细错误信息"
  }
  ```
