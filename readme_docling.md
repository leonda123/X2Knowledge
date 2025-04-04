# Docling 扩展使用说明

## 简介

Docling 扩展是X2Knowledge的一个强大转换引擎，专注于提供高质量的文档转换功能。相比于MarkItDown转换器，Docling在处理PDF文档和表格识别方面表现更佳，特别是对于复杂的排版和格式。

## 特点

- **更好的PDF处理能力**：优化的PDF解析能力，能够更准确地识别文档结构
- **增强的表格识别**：更精确地识别和重建表格结构
- **多格式支持**：支持PDF、Word、Excel、PPT、CSV、HTML、图片和XML等多种格式
- **多种输出格式**：支持转换为Markdown、HTML和JSON格式
- **GPU加速**：在CUDA环境下可以实现GPU加速，提升转换速度

## 支持的输入格式

- PDF文件 (`.pdf`)
- Word文档 (`.doc`, `.docx`)
- Excel电子表格 (`.xls`, `.xlsx`)
- PowerPoint演示文稿 (`.ppt`, `.pptx`)
- CSV文件 (`.csv`)
- HTML/XHTML文件 (`.html`, `.xhtml`)
- 图片文件 (`.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`)
- Markdown文件 (`.md`)
- XML文件 (`.xml`)

## 支持的输出格式

- Markdown (`.md`)
- HTML (`.html`)
- JSON (`.json`)

## 安装要求

要使用Docling扩展，您需要安装以下依赖：

```bash
pip install docling torch
```

为获得最佳性能，建议在支持CUDA的环境中运行：

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 使用方法

### Web界面

1. 在X2Knowledge主界面选择上传文件
2. 在转换选项中选择"Docling转换器"
3. 选择所需的输出格式（Markdown、HTML或JSON）
4. 点击"转换"按钮

### API使用

X2Knowledge提供了REST API接口，可以通过以下端点使用Docling转换功能：

#### Markdown转换API

```
POST /api/convert-to-markdown-docling
```

#### HTML转换API

```
POST /api/convert-to-html-docling
```

#### JSON转换API

```
POST /api/convert-to-json-docling
```

请求格式均为`multipart/form-data`，必须包含名为`file`的文件参数。

### 独立测试工具

项目中包含了一个独立的测试脚本`test_docling_conversion.py`，可用于测试Docling转换功能：

```bash
python test_docling_conversion.py [文件路径]
```

如果不提供文件路径参数，脚本将自动查找测试文件。

可选参数：
- `--type`: 指定测试文件类型，可选值为`pdf`、`xml`或`all`（默认为`pdf`）

## 性能说明

Docling转换器在运行时会检测系统是否支持CUDA。如果支持，将使用GPU加速；否则将使用CPU模式。GPU加速可以显著提高处理速度，特别是对于大型PDF文档。

## 故障排除

### 常见问题

1. **无法导入Docling库**
   - 确保已安装Docling: `pip install docling`

2. **转换过程中出现内存错误**
   - 对于大型文档，尝试在有更多内存的环境中运行
   - 检查是否有其他程序占用大量内存

3. **转换结果不理想**
   - 对于复杂格式的PDF，检查PDF文件是否为扫描版本
   - 尝试使用不同的转换引擎（MarkItDown或Docling）比较结果

### 日志查看

转换过程中的详细日志可以在控制台输出中查看，这有助于诊断转换问题。

## 开发者信息

如需扩展Docling转换功能或修复问题，可以查看`app/utils/converter_factory.py`文件中的`DoclingConverter`类。

## 更多信息

有关Docling库的更多信息，请访问[Docling官方文档](https://github.com/docling/)。
