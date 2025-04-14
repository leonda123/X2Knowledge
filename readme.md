![LOGO](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/x2knowledge-logo.png)

# X2Knowledge V0.5.2 - Document Conversion Tool

[<a href="/readme_cn.md">中文(简体)</a>] | [<a href="/readme.md">English</a>] 

X2Knowledge is an efficient open source knowledge extractor tool designed for enterprise knowledge base construction. It supports intelligent conversion of files in various formats such as PDF, Word, PPT, Excel, WAV, MP3, etc. into structured Markdown, HTML, and text formats, helping users to quickly and standardizedly enter various types of documents into the enterprise knowledge base system.
Through advanced format parsing and content extraction technology, the project significantly improves the efficiency and accuracy of knowledge conversion and is an ideal pre-processing tool for RAG (retrieval enhancement generation) applications and enterprise knowledge management.

![Design schematic](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/x2knowledge_en.png?raw=true)

[Demo website] (X2Knowledge v0.5.2 demo environment): http://115.190.8.7:8080/ The server performance is poor. Please use the docling interface for local testing. The server does not have a cuda environment!

Due to the diversity of personal or corporate documents, in the process of building a knowledge base, how to process documents in RAG/Agent applications can achieve the expected results plays a vital role. However, with the development of AI technology, open source and commercial tools have emerged, and how to choose and use these tools has become a major problem. The emergence of this tool successfully solved the problem of large models replying to pictures and texts

This project adheres to the principles of: 1. Either free, 2. Either fast, 3. Either high accuracy, 4. Unified interface, 5. Continuous update.
At the same time, everyone is welcome to discuss together. In the future, I plan to connect excellent open source projects such as olmOCR and MinerU to the project within my limited time.

## v0.5.3

### Update features:

- Temporarily remove the reference to the marker module function, and the introduction in the future is to be planned.
- Use Docling to extract and save images from documents, and support viewing in preview mode.
- Swagger interface, API calls are more intuitive.
- **New**: URL to Markdown conversion now supports using CSS selectors to precisely extract specific content from webpages.
- **New**: The file extraction table function supports exporting CSV, HTML, and Markdown.

## Features

- **Multiple conversion engines**
- **MarkItDown**: Optimized for Office documents (DOCX, XLSX, PPTX, CSV), fast and efficient
- **Docling**: Enhanced PDF conversion with better table recognition and VLM capabilities

- **Convert multiple file formats to text or Markdown**
- Support Word (.doc, .docx), Excel (.xls, .xlsx), PowerPoint (.ppt, .pptx), PDF, text files, etc.
- Maintain document structure in Markdown conversion mode
- Extract text from images via OCR
- **New**: Extract and save images from documents using Docling, supporting viewing in preview mode

- **Multiple output formats**
- **Text**: Simple plain text extraction
- **Markdown**: Preserve document structure, including headers, lists, and tables
- **HTML**: Full HTML output with image and formula support

- **Web content conversion**
- Convert webpage content to structured Markdown documents
- **New**: Support using CSS selectors (like #content, .article, main) to precisely extract specific content from webpages
- Option to remove headers and footers for cleaner main content

- **Audio conversion**
- Convert audio files (.mp3, .wav) to text/Markdown descriptions
- Extract metadata including duration, channels and sampling rate

- **Large file support**
- Supports files up to 50MB
- Efficient handling of large documents

## Converter Comparison

Below is a comparison of the three document conversion engines available in X2Knowledge:

| Feature | MarkItDown | Docling |
|---------|------------|---------|
| **Speed** | ★★★★★ (Fastest) | ★★★☆☆ (Moderate) |
| **Accuracy** | ★★★☆☆ (Good) | ★★★★☆ (Very Good) |
| **Table Handling** | ★★★☆☆ (Basic) | ★★★★☆ (Advanced) |
| **Formula Support** | ★☆☆☆☆ (Limited) | ★★★☆☆ (Decent) |
| **Image Extraction** | ★☆☆☆☆ (Basic OCR) | ★★★★☆ (VLM Support) |
| **Resource Usage** | ★★★★★ (Minimal) | ★★☆☆☆ (Heavy) |
| **Best For** | Office documents | PDF documents with tables & formulas |
| **GPU Acceleration** | No | Yes |
| **Supported Formats** | DOC, DOCX, XLS, XLSX, PPT, PPTX, PDF, TXT, MD | PDF, DOCX, XLSX, PPTX, CSV, Images, HTML |
| **Output Formats** | Text, Markdown | Text, Markdown, HTML, JSON |

Choose the converter that best fits your needs:
- **MarkItDown**: When you need quick conversion of Office documents with good fidelity
- **Docling**: When you need better handling of PDF documents with tables and images

## Usage

1. Select the conversion mode (Text or Markdown)
2. If using Markdown mode, choose between MarkItDown (default), Docling, or Marker converters
   - MarkItDown: Optimized for Office documents, faster processing
   - Docling: Better for PDF files with complex tables and layouts
   - Marker: Highest precision for documents with complex elements like tables, formulas, and images
3. Upload your document (or drag and drop)
4. View, copy or download the conversion result
5. Use the Markdown preview feature to see formatted results (when using Markdown mode)

## REST API

This tool provides a REST API for programmatic access, see the [<a href="/api_document.md">reference document</a>] for details:

### Provided:

- [x] **Text conversion**: `POST /api/convert`
- [x] **Text conversion and save file**: `POST /api/convert-file`
- [x] **Markdown conversion (MarkItDown)**: `POST /api/convert-to-md`
- [x] **Markdown conversion and save file (MarkItDown)**: `POST /api/convert-to-md-file`
- [x] **Markdown conversion (Docling)**: `POST /api/convert-to-md-docling`
- [x] **Markdown conversion and save file (Docling)**: `POST /api/convert-to-md-file-docling`
- [x] **Markdown conversion and extract image (Docling)**: `POST /api/convert-to-md-images-file-docling`
- [x] **Extract tables from a file and export them to a specified format (Docling)**: `POST /api/export-tables-docling`
- [x] **HTML conversion (Docling)**: `POST /api/convert-to-html-docling`
- [x] **URL to Markdown conversion**: `POST /api/convert-url-to-md`
- [x] **URL to Markdown file conversion**: `POST /api/convert-url-to-md-file`

### To be provided:

- [ ] **Extract only tables from PDF, XML, and Office to Excel**
- [ ] **Recognition of PDF and code reference parts**
- [x] **welcome to raise more requirements. **

For API testing and documentation, use the "API Test" button in the web interface to access Swagger UI.

## System screenshot

### Interface

#### Home page
![Home page](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/home.png?raw=true)
#### Url to MD
![Url to MD](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/url2md.png?raw=true)
#### Swagger
![API call](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/swagger.png?raw=true)
### Reply effect (take dify as an example, Fastgpt, Maxkb, coze webui that supports MD display can all be realized)
#### Graphics and texts reply
![Graphics and texts reply](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/dify_test_1.png?raw=true)
![Graphics and texts reply](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/dify_test_3.png?raw=true)
#### Form reply
![Form reply](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/dify_test_2.png?raw=true)

## Installation and Deployment

### Local Installation

#### Requirements

- Python 3.12+
- Flask
- pytesseract (for OCR functionality)
- Tesseract OCR engine
- MarkItDown library
- Docling library (optional, for enhanced PDF conversion)

#### Setup

1. Clone the repository:
   ```
   git clone https://github.com/leonda123/X2Knowledge.git
   cd X2Knowledge
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Install optional conversion engines:
   ```
   # For Docling support
   pip install docling
   ```

4. Install Tesseract OCR engine (for OCR functionality):
   - Windows: Download and install from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

5. Run the application:
   ```
   python app.py
   ```

6. Open a web browser and navigate to `http://127.0.0.1:5000/`

### Docker Deployment

Docker makes deploying X2Knowledge easier by avoiding environment configuration issues.

#### Using Docker Compose

1. Clone the repository:
   ```
   git clone https://github.com/leonda123/X2Knowledge.git
   cd X2Knowledge
   ```

2. Build and start the container:
   ```
   docker-compose up -d
   ```

3. Access the application:
   Open a web browser and navigate to `http://localhost:5000/`

#### Manual Docker Image Build

1. Build the Docker image:
   ```
   docker build -t x2knowledge .
   ```

2. Run the container:
   ```
   docker run -d -p 5000:5000 --name x2knowledge -v ./uploads:/app/uploads -v ./logs:/app/logs x2knowledge
   ```

3. Access the application:
   Open a web browser and navigate to `http://localhost:5000/`

## Key Advantages

- **Multiple Conversion Engines**: Choose the best engine for your document type - MarkItDown for Office documents, Docling for PDFs
- **High-Performance Document Processing**: Optimized document parsing engine that efficiently handles various document formats
- **Low Resource Consumption**: Runs smoothly even on servers with modest configurations
- **Accurate Structure Preservation**: Especially in Markdown conversion, accurately preserves the original document structure
- **Cross-Platform Support**: Can be deployed on Windows, macOS, and Linux systems
- **Flexible API Interface**: Provides RESTful API for easy integration with other systems
- **Deployment Without External Dependencies**: Core functionality requires no external service support except for OCR features
- **Containerized Deployment**: Support for Docker deployment simplifies environment setup

## Known Issues

- Older Word documents (.doc format) may take longer to process; converting to .docx format before uploading is recommended
- Some complex document layouts might not be perfectly preserved in Markdown conversion
- OCR accuracy depends on image quality and text complexity
- Docling works best with CUDA acceleration, but will fall back to CPU mode if unavailable

## Future Plans

### Technology roadmap:

- Short-term: Integrate mature solutions such as OcrmyPDF (document OCR), MinerU (unstructured data processing), and improve Marker integration
- Medium-term: Develop intelligent routing modules to achieve self-adaptive processing of document types
- Long-term: To build a large model in a vertical field and support the distillation of vertical field knowledge

## License

This project is licensed under the Apache-2.0 License - see the LICENSE file for details.

## Acknowledgments

- [pytesseract](https://github.com/madmaze/pytesseract) for OCR functionality
- [Flask](https://flask.palletsprojects.com/) web framework
- [Markidown](https://github.com/microsoft/markitdown.git) for document to Markdown conversion
- [Docling](https://github.com/docling-project/docling/) for enhanced PDF conversion
- [marked.js](https://marked.js.org/) for Markdown rendering
- [highlight.js](https://highlightjs.org/) for code syntax highlighting
- Various document processing libraries

---

##Contact information

- Email: dadajiu45@gmail.com

Project Links: [GitHub](https://github.com/leonda123/X2Knowledge.git) | [Gitee](https://gitee.com/leonda/X2Knowledge.git) | [GitCode](https://gitcode.com/leonda/X2Knowledge.git) 