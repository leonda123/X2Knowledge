# OCR图片文字识别功能安装说明

为了使用文档转文本工具的OCR图片文字识别功能，您需要安装Tesseract OCR引擎和相关语言包。

## 安装Tesseract OCR

### Windows系统

1. 从官方GitHub页面下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
2. 选择适合您系统的安装包（32位或64位）
3. 运行安装程序，建议使用默认安装路径（`C:\Program Files\Tesseract-OCR`）
4. 在安装过程中，确保勾选"中文简体"和"英文"语言包
5. 安装完成后，将Tesseract的安装路径添加到系统环境变量PATH中
6. 重启应用程序

### macOS系统

使用Homebrew安装：

```bash
# 安装Homebrew（如果尚未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Tesseract
brew install tesseract

# 安装中文语言包
brew install tesseract-lang
```

### Linux系统（Ubuntu/Debian）

```bash
# 安装Tesseract
sudo apt update
sudo apt install tesseract-ocr

# 安装中文语言包
sudo apt install tesseract-ocr-chi-sim

# 安装英文语言包
sudo apt install tesseract-ocr-eng
```

## 验证安装

安装完成后，您可以通过以下命令验证Tesseract是否正确安装：

```bash
tesseract --version
```

如果显示版本信息，则表示安装成功。

## 应用程序配置

安装Tesseract后，应用程序将自动检测并使用它。如果您的Tesseract安装在非标准位置，您可能需要设置环境变量：

### Windows

```
set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

### macOS/Linux

```
export TESSDATA_PREFIX=/usr/local/share/tessdata
```

## 常见问题

1. **无法找到Tesseract**
   - 确保Tesseract已正确安装
   - 检查环境变量PATH是否包含Tesseract安装路径

2. **中文识别效果不佳**
   - 确保已安装中文语言包
   - 图片质量较低可能影响识别效果
   - 尝试调整图片对比度和清晰度

3. **应用程序报错**
   - 检查日志文件中的错误信息
   - 确保所有依赖项都已正确安装

## 支持的文件类型

OCR功能支持以下文件类型中的图片文字识别：

- Word文档（.docx, .doc）中的嵌入图片
- PowerPoint演示文稿（.pptx, .ppt）中的图片
- PDF文档中的图片内容

## 注意事项

- OCR识别效果受图片质量影响较大
- 复杂背景、特殊字体可能降低识别准确率
- 大型文档中包含大量图片可能导致处理时间较长 