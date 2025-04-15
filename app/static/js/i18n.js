/**
 * 多语言支持模块
 * 提供中英文切换功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 语言文本数据
    const translations = {
        'zh': {
            // 标题和导航
            'title': 'X2Knowledge - 知识提取器工具',
            'subtitle': '知识库原生支持：输出带元数据的Markdown，与RAG/LangChain/Agent等框架无缝对接',
            'api-docs-link': 'API文档',
            
            // 标签和上传区域
            'tab-text': '转为文本',
            'tab-markdown': '转为Markdown',
            'drop-files': '拖拽文件到此处或',
            'choose-file': '选择文件',
            'supported-types-text': '支持的文件类型: .doc, .docx, .xls, .xlsx, .ppt, .pptx, .pdf, .txt, .md, .xml',
            'supported-types-md': '支持的文件类型: .doc, .docx, .xls, .xlsx, .ppt, .pptx, .pdf, .txt, .md, .mp3, .wav, .xml',
            'doc-note': '注意: 处理旧版Word文档(.doc)可能需要更长时间，建议转换为.docx格式后上传',
            'markdown-note-structure': '注意: 转换为Markdown格式可以更好地保留文档结构',
            
            // 功能提示
            'ocr-feature': 'OCR功能: 自动识别文档中的图片文字',
            'encoding-feature': '编码功能: 自动将文档转换为UTF-8编码，解决中文乱码问题',
            'markdown-feature-structure': 'Markdown功能: 保留文档标题、列表、表格等结构',
            'markdown-feature-audio': '新增功能: 支持音频文件(.mp3, .wav)转换为Markdown描述',
            
            // 视图切换
            'source-view': '源码视图',
            'preview-view': '预览视图',
            
            // 结果区域
            'conversion-result': '转换结果',
            'copy-text': '复制文本',
            'copy-success': '文本已复制到剪贴板',
            'download-text': '下载文件',
            'new-conversion': '新的转换',
            'fullscreen': '全屏预览',
            'fullscreen-preview': '预览内容',
            
            // 加载状态
            'converting': '正在转换文件，请稍候...',
            'doc-loading-note': '旧版格式文件(.doc)可能需要较长时间',
            'ocr-loading-note': '正在进行图片文字识别...',
            
            // OCR部分
            'ocr-title': 'OCR图片文字识别',
            'ocr-intro': '本工具支持从文档中的图片提取文字，包括：',
            'ocr-feature-1': 'Word文档中的嵌入图片',
            'ocr-feature-2': 'PowerPoint幻灯片中的图片',
            'ocr-feature-3': 'PDF文档中的图片内容',
            'ocr-note': '注意：OCR功能需要安装Tesseract OCR引擎，',
            'ocr-install': '查看安装说明',
            
            // Markdown部分
            'markdown-conversion-title': 'Markdown转换',
            'markdown-intro': '使用MarkItDown转换功能可以：',
            'markdown-feature-1': '保留文档的标题、列表和表格结构',
            'markdown-feature-2': '保留文档中的超链接和图片',
            'markdown-feature-3': '提取音频文件的元数据',
            'markdown-feature-4': '比纯文本转换提供更好的文档结构',
            'markdown-use-case': '此功能特别适合需要保留文档格式的场景，如内容分析、文本挖掘或与大型语言模型交互。',
            
            // 编码部分
            'encoding-title': 'UTF-8编码转换',
            'encoding-intro': '本工具支持自动字符集编码转换：',
            'encoding-feature-1': '自动检测文档的原始编码',
            'encoding-feature-2': '将所有文本内容转换为UTF-8编码',
            'encoding-feature-3': '特别优化了中文字符的处理',
            'encoding-feature-4': '支持所有文件类型的编码转换',
            'encoding-benefit': '此功能可以有效解决中文乱码问题，无需用户手动设置编码。',
            
            // 页脚
            'footer': '© 2025 X2Knowledge v0.6.0 - 知识提取器工具 | by leonda',
            
            // API文档页面
            'api-doc-title': 'X2Knowledge - 知识提取器工具 - API文档',
            'api-doc-subtitle': 'REST API接口使用说明',
            'back-to-home': '返回首页',
            'api-docs-anchor': 'API文档',
            'api-docs-heading': 'API文档',
            'api-docs-intro': '本工具提供了REST API接口，可以通过程序调用实现文档转换功能。',
            'api-tab-text': '转为文本API',
            'api-tab-markdown': '转为Markdown API',
            'api-tab-markdown-docling': 'Docling转MD API',
            'api-tab-docling-html': 'Docling转HTML API',
            'api-tab-docling-json': 'Docling转JSON API',
            'text-api-title': '文档转文本API',
            'md-api-title': '文档转Markdown API',
            'docling-md-api-title': 'Docling文档转Markdown API',
            'docling-html-api-title': 'Docling文档转HTML API',
            'docling-json-api-title': 'Docling文档转JSON API',
            'content-type': '内容类型: multipart/form-data',
            'request-params': '请求参数',
            'param-name': '参数名',
            'param-type': '类型',
            'param-required': '必填',
            'param-desc': '描述',
            'file-type': '文件',
            'yes': '是',
            'file-desc': '要转换的文档文件',
            'supported-file-types': '支持的文件类型',
            'response-format': '响应格式',
            'success-response': '成功响应 (HTTP 200):',
            'error-response': '错误响应 (HTTP 4xx/5xx):',
            'audio-files': '音频文件 (.mp3, .wav)',
            'new-tag': '新增',
            'md-features': '特点',
            'md-features-intro': '与普通文本转换不同，Markdown转换将保留更多的原始文档结构：',
            'md-feature-1': '保留标题层级结构',
            'md-feature-2': '保留列表格式',
            'md-feature-3': '保留表格结构',
            'md-feature-4': '保留超链接',
            'md-feature-5': '对音频文件提取元数据，包括时长、声道数和采样率',
            'code-examples': '示例代码',
            'python-text-example': 'Python示例 - 转为文本',
            'python-md-example': 'Python示例 - 转为Markdown',
            
            // 提示和错误
            'select-file-alert': '请先选择文件',
            'file-type-not-supported': '不支持的文件类型！请上传支持的文件格式。',
            'file-too-large': '文件过大！最大支持50MB',
            'conversion-failed': '转换失败',
            'request-failed': '请求失败',
            'filename': '文件名',
            'file-size': '文件大小',
            'processing-time': '处理时间',
            'text-length': '文本长度',
            'seconds': '秒',
            'characters': '字符',
            'copied': '已复制!',
            'copy-failed': '复制失败',
            'copy-failed-manual': '复制失败，请手动选择文本并复制',
            'downloaded': '已下载!',
            
            // 转换器选项
            'markitdown-converter-label': '使用 MarkItDown 转换器 (默认)',
            'markitdown-converter-desc': '对原生Office格式文件（DOCX, XLSX, PPTX）支持非常好，速度快、准确率高，但对PDF格式文件效果较差',
            'docling-converter-label': '使用 Docling 转换器',
            'docling-converter-desc': '对PDF有优化的表格识别和VLM，准确率大大提升，支持更多输入格式，但需要CUDA环境最佳（当前使用CPU加速）',
            'docling-warning': '且时间较长，不建议在本测试环境使用！',
            'docling-images-converter-label': '使用 Docling 转换器（带图片）',
            'docling-images-converter-desc': '与普通Docling相同，但会提取文档中的图片并保存到静态文件夹中，支持预览图片',
            'docling-images-warning': '处理需要较长时间，不建议处理大文件！',
            'marker-converter-label': '使用 Marker 转换器',
            'docling-images-converter-desc': '高精度文档转换器，优秀的表格和公式处理能力，支持多种文档格式和图片',
            'docling-images-warning': '需要安装PyTorch，性能取决于系统配置',
            
            // 文件格式支持
            'markitdown-supported-formats': '.pdf, .docx, .pptx, .xlsx, .xls, .csv, .json, .xml, .wav, .mp3',
            'docling-supported-formats': '.pdf, .docx, .xlsx, .pptx, .md, .html, .xhtml, .csv, .png, .jpg, .jpeg, .tiff, .bmp',
            'docling-images-supported-formats': '.pdf, .docx, .xlsx, .pptx, .md, .html, .xhtml',
            'marker-supported-formats': '.pdf, .png, .jpg, .jpeg, .pptx, .docx, .xlsx, .html',
            
            // 批量转换API
            'api-tab-folder-conversion': '批量转换API',
            'folder-conversion-title': '批量文件夹转换API',
            'folder-conversion-note': '注意: 此API用于批量转换文件夹中的所有支持格式文件，会生成日志文件记录转换过程。',
            'text-folder-api-title': '批量转为文本API',
            'md-folder-api-title': '批量转为Markdown API (MarkItDown)',
            'docling-folder-api-title': '批量转为Markdown API (Docling)',
            'content-type-json': '内容类型: application/json',
            'request-example': '请求示例',
            'source-folder-desc': '要转换的源文件夹路径(绝对路径)',
            'output-folder-desc': '转换结果的输出文件夹路径，如不提供将在源文件夹创建output_text子文件夹',
            'output-folder-md-desc': '转换结果的输出文件夹路径，如不提供将在源文件夹创建output_markdown子文件夹',
            'output-folder-docling-desc': '转换结果的输出文件夹路径，如不提供将在源文件夹创建output_docling子文件夹',
            'no': '否',
            'folder-conversion-features': '批量转换特点',
            'folder-conversion-features-intro': '批量转换API提供以下功能：',
            'folder-feature-1': '递归处理指定文件夹及其子文件夹中的所有文件',
            'folder-feature-2': '在输出文件夹中保持原始文件夹结构',
            'folder-feature-3': '自动跳过不支持的文件格式',
            'folder-feature-4': '生成详细的转换日志记录',
            'folder-feature-5': '提供转换统计和详细信息',
            'python-folder-example': 'Python示例 - 批量转换文件夹',
            // API文档
            'api-docs-title': 'X2Knowledge API 文档',
            'api-extract-text': '文档文本提取 API',
            'api-markitdown-md': 'MarkItDown转MD API',
            'api-docling-md': 'Docling转MD API',
            'api-marker-md': 'Marker转MD API',
            'api-marker-html': 'Marker转HTML API',
            'api-marker-json': 'Marker转JSON API',
            
            // URL转Markdown相关
            'tab-url': 'URL转Markdown',
            'url-input-label': '输入网页URL：',
            'remove-header-footer': '移除页眉和页脚',
            'convert-url': '转换URL',
            'url-convert-description': '将网页内容转换为结构化的Markdown格式，保留原始内容的结构、链接和图片。',
            'url-convert-tip': '提示：移除页眉页脚选项可以帮助您获取更干净的主要内容。',
            'selector-label': 'CSS选择器（可选）：',
            'selector-hint': '输入CSS选择器来提取特定内容',
            'selector-tip': '选择器提示：使用CSS选择器（如 #content, .article, main）可以精确提取页面中的特定内容。',
            'selector-help-button': '查看选择器教程',
            'selector-help-title': 'CSS选择器使用教程',
            'selector-tab-basic': '基础选择器',
            'selector-tab-advanced': '高级选择器',
            'selector-tab-examples': '常用示例',
            'basic-selectors-title': '基础CSS选择器',
            'selector-syntax': '语法',
            'selector-example': '示例',
            'selector-description': '描述',
            'selector-id-desc': '选择ID为"content"的元素',
            'selector-class-desc': '选择所有class为"article"的元素',
            'selector-tag-desc': '选择所有<main>标签元素',
            'selector-tag-class-desc': '选择所有class为"content"的div元素',
            'selector-all-desc': '选择所有元素（不推荐使用）',
            'advanced-selectors-title': '高级CSS选择器',
            'selector-child-desc': '选择所有父元素为<article>的<p>元素',
            'selector-descendant-desc': '选择所有位于<article>内的<p>元素',
            'selector-attribute-desc': '选择所有具有role="main"属性的元素',
            'selector-first-child-desc': '选择每个父元素的第一个<li>子元素',
            'selector-multiple-desc': '同时选择多个元素，用逗号分隔',
            'common-examples-title': '常用网站内容提取示例',
            'website-type': '网站类型',
            'selector-to-try': '推荐选择器',
            'selector-purpose': '提取内容',
            'blog-articles': '博客文章',
            'blog-articles-desc': '提取文章正文，跳过评论和侧边栏',
            'news-sites': '新闻网站',
            'news-sites-desc': '提取新闻正文，跳过相关新闻和广告',
            'documentation': '技术文档',
            'documentation-desc': '提取文档内容，跳过导航菜单',
            'forum-posts': '论坛帖子',
            'forum-posts-desc': '提取帖子内容，跳过回复和侧边栏',
            'product-pages': '产品页面',
            'product-pages-desc': '提取产品描述，跳过推荐产品',
            'finding-selectors-title': '如何找到正确的选择器',
            'finding-selectors-tip1': '在网页上右击要提取的内容区域，选择"检查元素"',
            'finding-selectors-tip2': '在开发者工具中查看HTML结构，找到包含所需内容的主要元素',
            'finding-selectors-tip3': '查看该元素的ID或class属性，使用#id或.class作为选择器',
            'finding-selectors-tip4': '如果尝试一个选择器没效果，可以组合多个选择器（用逗号分隔）增加匹配概率',
            
            // Embedding预处理相关
            'tab-embedding': 'Embedding预处理',
            'embedding-title': 'Markdown知识库入库预处理',
            'embedding-description': '将Markdown文件或文本处理为JSON和CSV格式的问答对，用于知识库入库前的数据准备。',
            'embedding-rules-title': '处理规则说明：',
            'embedding-rule-1': '将标题(#)收集为question，标题下的所有文本内容收集为answer，直到下一个标题的出现',
            'embedding-rule-2': '如果是二级及以上标题，问题标题会拼接上级标题，格式为"{上级标题},{当前标题}"',
            'embedding-rule-3': '只有包含内容的标题会被处理，空标题会被忽略',
            'embedding-example-title': '示例：',
            'embedding-example-md-title': '原始Markdown：',
            'embedding-example-json-title': '生成的JSON：',
            'method-rules-title': '方法使用说明：',
            'method-rule-1': 'POST请求： /preprocess-for-storage 具体参数见swagger页面的调用方法',
            'method-rule-2': '该方法仅适用于Markdown文件，其他格式文件请使用其他方法',
            'method-rule-3': '同时文件中至少包含一个标题，否则内容为空'
        },
        'en': {
            // Title and Navigation
            'title': 'X2Knowledge - Document Conversion Tool',
            'subtitle': 'Knowledge base native support: Output Markdown with metadata, seamlessly integrates with RAG/LangChain/Agent frameworks',
            'ocr-badge': 'OCR Image Text Recognition',
            'encoding-badge': 'UTF-8 Encoding Conversion',
            'markdown-badge': 'New Feature: Convert to Markdown',
            'api-docs-link': 'API Documentation',
            
            // Tabs and Upload Area
            'tab-text': 'Convert to Text',
            'tab-markdown': 'Convert to Markdown',
            'drop-files': 'Drop files here or',
            'choose-file': 'Choose File',
            'supported-types-text': 'Supported file types: .doc, .docx, .xls, .xlsx, .ppt, .pptx, .pdf, .txt, .md, .xml',
            'supported-types-md': 'Supported file types: .doc, .docx, .xls, .xlsx, .ppt, .pptx, .pdf, .txt, .md, .mp3, .wav, .xml',
            'doc-note': 'Note: Processing older Word documents (.doc) may take longer, we recommend converting to .docx format before uploading',
            'markdown-note-structure': 'Note: Converting to Markdown format better preserves document structure',
            
            // 视图切换
            'source-view': 'Source View',
            'preview-view': 'Preview View',
            
            // Feature Notes
            'ocr-feature': 'OCR Feature: Automatically recognizes text in document images',
            'encoding-feature': 'Encoding Feature: Automatically converts documents to UTF-8 encoding, solving Chinese character issues',
            'markdown-feature-structure': 'Markdown Feature: Preserves document headings, lists, tables and other structures',
            'markdown-feature-audio': 'New Feature: Supports audio files (.mp3, .wav) conversion to Markdown description',
            
            // Results Area
            'conversion-result': 'Conversion Result',
            'copy-text': 'Copy Text',
            'copy-success': 'Text copied to clipboard',
            'download-text': 'Download File',
            'new-conversion': 'New Conversion',
            'fullscreen': 'Fullscreen Preview',
            'fullscreen-preview': 'Preview Content',
            
            // Loading Status
            'converting': 'Converting file, please wait...',
            'doc-loading-note': 'Older format files (.doc) may take longer',
            'ocr-loading-note': 'Performing image text recognition...',
            
            // OCR Section
            'ocr-title': 'OCR Image Text Recognition',
            'ocr-intro': 'This tool supports extracting text from images in documents, including:',
            'ocr-feature-1': 'Embedded images in Word documents',
            'ocr-feature-2': 'Images in PowerPoint slides',
            'ocr-feature-3': 'Image content in PDF documents',
            'ocr-note': 'Note: OCR feature requires Tesseract OCR engine installation,',
            'ocr-install': 'View installation instructions',
            
            // Markdown Section
            'markdown-conversion-title': 'Markdown Conversion',
            'markdown-intro': 'Using the MarkItDown conversion feature allows you to:',
            'markdown-feature-1': 'Preserve document headings, lists, and table structures',
            'markdown-feature-2': 'Preserve hyperlinks and images in the document',
            'markdown-feature-3': 'Extract metadata from audio files',
            'markdown-feature-4': 'Provide better document structure than plain text conversion',
            'markdown-use-case': 'This feature is particularly suitable for scenarios requiring document format preservation, such as content analysis, text mining, or interaction with large language models.',
            
            // Encoding Section
            'encoding-title': 'UTF-8 Encoding Conversion',
            'encoding-intro': 'This tool supports automatic character set encoding conversion:',
            'encoding-feature-1': 'Automatically detects document\'s original encoding',
            'encoding-feature-2': 'Converts all text content to UTF-8 encoding',
            'encoding-feature-3': 'Specially optimized for Chinese character processing',
            'encoding-feature-4': 'Supports encoding conversion for all file types',
            'encoding-benefit': 'This feature effectively solves Chinese character encoding issues without manual encoding settings.',
            
            // Footer
            'footer': '© 2025 X2Knowledge v0.6.0 - Document Conversion Tool | Built with Flask and JavaScript',
            
            // API Documentation Page
            'api-doc-title': 'X2Knowledge - Document Conversion Tool - API Documentation',
            'back-to-home': 'Back to Home',
            'api-docs-anchor': 'API Documentation',
            'api-test-anchor': 'Online Testing',
            'api-docs-heading': 'API Documentation',
            'api-docs-intro': 'This tool provides REST API interfaces for programmatic document conversion.',
            'api-tab-text': 'Convert to Text API',
            'api-tab-markdown': 'Convert to Markdown API',
            'api-tab-markdown-docling': 'Docling to Markdown API',
            'api-tab-docling-html': 'Docling to HTML API',
            'api-tab-docling-json': 'Docling to JSON API',
            'text-api-title': 'Document to Text API',
            'md-api-title': 'Document to Markdown API',
            'docling-md-api-title': 'Docling Document to Markdown API',
            'docling-html-api-title': 'Docling Document to HTML API',
            'docling-json-api-title': 'Docling Document to JSON API',
            'content-type': 'Content-Type: multipart/form-data',
            'request-params': 'Request Parameters',
            'param-name': 'Parameter',
            'param-type': 'Type',
            'param-required': 'Required',
            'param-desc': 'Description',
            'file-type': 'file',
            'yes': 'Yes',
            'file-desc': 'Document file to convert',
            'supported-file-types': 'Supported File Types',
            'response-format': 'Response Format',
            'success-response': 'Success Response (HTTP 200):',
            'error-response': 'Error Response (HTTP 4xx/5xx):',
            'audio-files': 'Audio files (.mp3, .wav)',
            'new-tag': 'NEW',
            'md-features': 'Features',
            'md-features-intro': 'Unlike plain text conversion, Markdown conversion preserves more of the original document structure:',
            'md-feature-1': 'Preserves heading hierarchy',
            'md-feature-2': 'Preserves list formats',
            'md-feature-3': 'Preserves table structures',
            'md-feature-4': 'Preserves hyperlinks',
            'md-feature-5': 'Extracts metadata from audio files, including duration, channels, and sample rate',
            'code-examples': 'Code Examples',
            'python-text-example': 'Python Example - Convert to Text',
            'python-md-example': 'Python Example - Convert to Markdown',
            
            // Alerts and Errors
            'select-file-alert': 'Please select a file first',
            'file-type-not-supported': 'File type not supported! Please upload a supported format.',
            'file-too-large': 'File is too large! Maximum size is 50MB',
            'conversion-failed': 'Conversion failed',
            'request-failed': 'Request failed',
            'filename': 'Filename',
            'file-size': 'File size',
            'processing-time': 'Processing time',
            'text-length': 'Text length',
            'seconds': 'seconds',
            'characters': 'characters',
            'copied': 'Copied!',
            'copy-failed': 'Copy failed',
            'copy-failed-manual': 'Copy failed, please select the text manually',
            'downloaded': 'Downloaded!',
            
            // Converter Options
            'markitdown-converter-label': 'Use MarkItDown Converter (Default)',
            'markitdown-converter-desc': 'Excellent support for native Office formats (DOCX, XLSX, PPTX), fast and accurate, but less effective for PDF files',
            'docling-converter-label': 'Use Docling Converter',
            'docling-converter-desc': 'Optimized table recognition and VLM for PDFs, greatly improved accuracy, supports more input formats, but works best with CUDA environment (currently using CPU acceleration)',
            'docling-warning': 'and takes longer, not recommended for this test environment!',
            'docling-images-converter-label': 'Use Docling Converter (with Images)',
            'docling-images-converter-desc': 'Same as regular Docling, but extracts images from the document and saves them to a static folder for preview',
            'docling-images-warning': 'Processing takes longer, not recommended for large files!',
            'marker-converter-label': 'Use Marker Converter',
            'docling-images-converter-desc': 'High-precision document converter, excellent table and formula processing capabilities, supports multiple document formats and images',
            'docling-images-warning': 'Requires PyTorch, performance depends on system configuration',
            
            // File Format Support
            'markitdown-supported-formats': '.pdf, .docx, .pptx, .xlsx, .xls, .csv, .json, .xml, .wav, .mp3',
            'docling-supported-formats': '.pdf, .docx, .xlsx, .pptx, .md, .html, .xhtml, .csv, .png, .jpg, .jpeg, .tiff, .bmp',
            'docling-images-supported-formats': '.pdf, .docx, .xlsx, .pptx, .md, .html, .xhtml',
            'marker-supported-formats': '.pdf, .png, .jpg, .jpeg, .pptx, .docx, .xlsx, .html',
            
            // Batch Conversion API
            'api-tab-folder-conversion': 'Batch Conversion API',
            'folder-conversion-title': 'Batch Folder Conversion API',
            'folder-conversion-note': 'Note: This API is used for batch conversion of all supported format files in a folder, and generates a log file recording the conversion process.',
            'text-folder-api-title': 'Batch to Text API',
            'md-folder-api-title': 'Batch to Markdown API (MarkItDown)',
            'docling-folder-api-title': 'Batch to Markdown API (Docling)',
            'content-type-json': 'Content-Type: application/json',
            'request-example': 'Request Example',
            'source-folder-desc': 'Source folder path to convert (absolute path)',
            'output-folder-desc': 'Output folder path for conversion results, if not provided, an output_text subfolder will be created in the source folder',
            'output-folder-md-desc': 'Output folder path for conversion results, if not provided, an output_markdown subfolder will be created in the source folder',
            'output-folder-docling-desc': 'Output folder path for conversion results, if not provided, an output_docling subfolder will be created in the source folder',
            'no': 'No',
            'folder-conversion-features': 'Batch Conversion Features',
            'folder-conversion-features-intro': 'The batch conversion API provides the following features:',
            'folder-feature-1': 'Recursively processes all files in the specified folder and its subfolders',
            'folder-feature-2': 'Maintains the original folder structure in the output folder',
            'folder-feature-3': 'Automatically skips unsupported file formats',
            'folder-feature-4': 'Generates detailed conversion log records',
            'folder-feature-5': 'Provides conversion statistics and details',
            'python-folder-example': 'Python Example - Batch Convert Folder',
            // API文档
            'api-docs-title': 'X2Knowledge API 文档',
            'api-extract-text': '文档文本提取 API',
            'api-markitdown-md': 'MarkItDown转MD API',
            'api-docling-md': 'Docling转MD API',
            'api-marker-md': 'Marker转MD API',
            'api-marker-html': 'Marker转HTML API',
            'api-marker-json': 'Marker转JSON API',
            
            // URL to Markdown related
            'tab-url': 'URL to Markdown',
            'url-input-label': 'Enter Website URL:',
            'remove-header-footer': 'Remove header and footer',
            'convert-url': 'Convert URL',
            'url-convert-description': 'Convert web content to structured Markdown format, preserving original structure, links and images.',
            'url-convert-tip': 'Tip: The option to remove headers and footers helps you get cleaner main content.',
            'selector-label': 'CSS Selector (Optional):',
            'selector-hint': 'Enter a CSS selector to extract specific content',
            'selector-tip': 'Selector Tip: Use CSS selectors (like #content, .article, main) to precisely extract specific content from the page.',
            'selector-help-button': 'View Selector Guide',
            'selector-help-title': 'CSS Selector Usage Guide',
            'selector-tab-basic': 'Basic Selectors',
            'selector-tab-advanced': 'Advanced Selectors',
            'selector-tab-examples': 'Common Examples',
            'basic-selectors-title': 'Basic CSS Selectors',
            'selector-syntax': 'Syntax',
            'selector-example': 'Example',
            'selector-description': 'Description',
            'selector-id-desc': 'Selects element with ID "content"',
            'selector-class-desc': 'Selects all elements with class "article"',
            'selector-tag-desc': 'Selects all <main> tag elements',
            'selector-tag-class-desc': 'Selects all div elements with class "content"',
            'selector-all-desc': 'Selects all elements (not recommended)',
            'advanced-selectors-title': 'Advanced CSS Selectors',
            'selector-child-desc': 'Selects all <p> elements that are direct children of <article>',
            'selector-descendant-desc': 'Selects all <p> elements inside <article> at any depth',
            'selector-attribute-desc': 'Selects all elements with attribute role="main"',
            'selector-first-child-desc': 'Selects the first <li> child of each parent element',
            'selector-multiple-desc': 'Selects multiple elements at once, separated by commas',
            'common-examples-title': 'Common Website Content Extraction Examples',
            'website-type': 'Website Type',
            'selector-to-try': 'Recommended Selectors',
            'selector-purpose': 'Content Extracted',
            'blog-articles': 'Blog Articles',
            'blog-articles-desc': 'Extract article body, skip comments and sidebars',
            'news-sites': 'News Sites',
            'news-sites-desc': 'Extract news content, skip related articles and ads',
            'documentation': 'Technical Docs',
            'documentation-desc': 'Extract documentation content, skip navigation menus',
            'forum-posts': 'Forum Posts',
            'forum-posts-desc': 'Extract post content, skip replies and sidebars',
            'product-pages': 'Product Pages',
            'product-pages-desc': 'Extract product descriptions, skip recommended products',
            'finding-selectors-title': 'How to Find the Right Selector',
            'finding-selectors-tip1': 'Right-click on the content area you want to extract and select "Inspect Element"',
            'finding-selectors-tip2': 'Examine the HTML structure in developer tools to find the main element containing desired content',
            'finding-selectors-tip3': 'Look for ID or class attributes of that element, use #id or .class as selector',
            'finding-selectors-tip4': 'If one selector doesn\'t work, try combining multiple selectors (comma-separated) to increase match probability',
            
            // Embedding preprocessing related
            'tab-embedding': 'Embedding Preprocessing',
            'embedding-title': 'Markdown Knowledge Base Preprocessing',
            'embedding-description': 'Process Markdown files or text into JSON and CSV format QA pairs for knowledge base preparation.',
            'embedding-rules-title': 'Processing Rules:',
            'embedding-rule-1': 'Collect headings (#) as questions, and all text content under the heading as answers, until the next heading appears',
            'embedding-rule-2': 'If it\'s a level 2 or higher heading, the question title will be concatenated with its parent heading in the format "{parent heading},{current heading}"',
            'embedding-rule-3': 'Only headings with content will be processed, empty headings will be ignored',
            'embedding-example-title': 'Example:',
            'embedding-example-md-title': 'Original Markdown:',
            'embedding-example-json-title': 'Generated JSON:',
            'method-rules-title': 'Method Usage Instructions:',
            'method-rule-1': 'POST request: /preprocess-for-storage See swagger page for specific parameters',
            'method-rule-2': 'This method is only applicable to Markdown files, please use other methods for other file formats',
            'method-rule-3': 'The file must contain at least one heading, otherwise the content will be empty'
        }
    };
    
    // 获取语言偏好或默认使用中文
    let currentLang = localStorage.getItem('x2knowledge_lang') || 'zh';
    
    // 获取所有语言切换按钮
    const languageBtns = document.querySelectorAll('.language-btn');
    
    // 根据保存的语言偏好设置激活状态
    languageBtns.forEach(btn => {
        if (btn.dataset.lang === currentLang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // 翻译页面元素
    translatePage(currentLang);
    
    // 为语言切换按钮添加点击事件
    languageBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const lang = this.dataset.lang;
            
            // 更新激活按钮
            languageBtns.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // 保存语言偏好到本地存储
            localStorage.setItem('x2knowledge_lang', lang);
            
            // 翻译页面
            translatePage(lang);
        });
    });
    
    // 翻译页面元素函数
    function translatePage(lang) {
        currentLang = lang;
        const elements = document.querySelectorAll('[data-i18n]');
        
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (translations[lang] && translations[lang][key]) {
                // 如果是输入元素
                if (element.tagName === 'INPUT' && element.type === 'text') {
                    element.placeholder = translations[lang][key];
                // 如果是常规元素
                } else {
                    element.textContent = translations[lang][key];
                }
            }
        });
    }
    
    // 提供一个获取翻译文本的公共方法
    window.getTranslatedText = function(key, fallback) {
        if (translations[currentLang] && translations[currentLang][key]) {
            return translations[currentLang][key];
        }
        return fallback || key;
    };
}); 