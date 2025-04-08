# X2Knowledge - Document Conversion Tool

[<a href="/readme_cn.md">中文(简体)</a>] | [<a href="/readme.md">English</a>] 

X2Knowledge is an efficient open source knowledge extractor tool designed for enterprise knowledge base construction. It supports intelligent conversion of files in various formats such as PDF, Word, PPT, Excel, WAV, MP3, etc. into structured TXT or Markdown formats, helping users to quickly and standardizedly enter various types of documents into the enterprise knowledge base system. Through advanced format parsing and content extraction technology, the project significantly improves the efficiency and accuracy of knowledge conversion and is an ideal pre-processing tool for RAG (retrieval enhancement generation) applications and enterprise knowledge management.

![Design schematic](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/x2knowledge_en.png?raw=true)

[Demo website](http://115.190.8.7:8080/)：http://115.190.8.7:8080/ The server performance is poor. Please use the docling interface for local testing. The server does not have a cuda environment!

Due to the diversity of personal or corporate documents, in the process of building a knowledge base, how to process documents in RAG/Agent to achieve the expected results plays a vital role. However, with the development of AI technology, open source and commercial tools are emerging, and how to choose and use these tools has become a big problem.

This project adheres to the principles of: 1. Either free, 2. Either fast, 3. Either high accuracy, 4. Unified interface, 5. Continuous update.
At the same time, everyone is welcome to discuss together. In the future, I plan to integrate excellent open source projects such as olmOCR, MinerU, Marker, etc. into the project within my limited time.

Everyone, please stay tuned!

## Note! Docling and marker are not enabled by default (offline model files are too large), and need to be enabled manually in requirements.txt.

## Latest Updates (v0.4.0)

- **Updated API Interface Structure**: Restructured API endpoints for better consistency and usability
- **Added Marker Integration**: Integrated the Marker high-precision document converter with support for PDF, images, Office documents
- **Enhanced Output Formats**: Added support for HTML and JSON output in addition to Markdown
- **Improved UI Experience**: Enhanced frontend with converter selection options and better format display
- **Added Comprehensive API Documentation**: Complete documentation for all API endpoints including Marker methods
- **Updated Internationalization**: Added multilanguage support for all new features and converters
- **Upgraded Core Dependencies**: Updated libraries for better stability and performance

## Features

- **Multiple Conversion Engines**
  - **MarkItDown**: Fast and efficient for Office documents (DOCX, XLSX, PPTX)
  - **Docling**: Enhanced PDF conversion with better table recognition and VLM capabilities
  - **Marker**: High-precision document conversion with excellent table, formula and image extraction

- **Convert multiple file formats to text or Markdown**
  - Support for Word (.doc, .docx), Excel (.xls, .xlsx), PowerPoint (.ppt, .pptx), PDF, text files, and more
  - Maintains document structure in Markdown conversion mode
  - Extracts text from images via OCR

- **Multiple Output Formats**
  - **Text**: Simple plain text extraction
  - **Markdown**: Preserves document structure including headings, lists, and tables
  - **HTML**: Full HTML output with image and formula support
  - **JSON**: Structured document representation with metadata

- **OCR Support**
  - Automatically extracts text from images embedded in documents
  - Works with images in Word, PowerPoint, and PDF files

- **Audio Conversion**
  - Convert audio files (.mp3, .wav) to text/Markdown description
  - Extracts metadata including duration, channels, and sample rate

- **UTF-8 Encoding**
  - Automatically converts documents to UTF-8 encoding
  - Resolves Chinese character display issues
  - No manual encoding configuration needed

- **Large File Support**
  - Supports files up to 50MB
  - Efficient processing of large documents

## Converter Comparison

Below is a comparison of the three document conversion engines available in X2Knowledge:

| Feature | MarkItDown | Docling | Marker |
|---------|------------|---------|--------|
| **Speed** | ★★★★★ (Fastest) | ★★★☆☆ (Moderate) | ★★☆☆☆ (Slower) |
| **Accuracy** | ★★★☆☆ (Good) | ★★★★☆ (Very Good) | ★★★★★ (Excellent) |
| **Table Handling** | ★★★☆☆ (Basic) | ★★★★☆ (Advanced) | ★★★★★ (Superior) |
| **Formula Support** | ★☆☆☆☆ (Limited) | ★★★☆☆ (Decent) | ★★★★★ (Excellent) |
| **Image Extraction** | ★☆☆☆☆ (Basic OCR) | ★★★★☆ (VLM Support) | ★★★★★ (Detailed) |
| **Resource Usage** | ★★★★★ (Minimal) | ★★☆☆☆ (Heavy) | ★★☆☆☆ (Heavy) |
| **Best For** | Office documents | PDF documents | Complex documents with tables & formulas |
| **GPU Acceleration** | No | Yes | Yes |
| **Supported Formats** | DOC, DOCX, XLS, XLSX, PPT, PPTX, PDF, TXT, MD | PDF, DOCX, XLSX, PPTX, Images, HTML | PDF, DOCX, XLSX, PPTX, Images, HTML |
| **Output Formats** | Text, Markdown | Text, Markdown, HTML, JSON | Text, Markdown, HTML, JSON |

Choose the converter that best fits your needs:
- **MarkItDown**: When you need quick conversion of Office documents with good fidelity
- **Docling**: When you need better handling of PDF documents with tables and images
- **Marker**: When you need the highest possible accuracy for complex documents, especially with formulas and tables

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

The tool provides a REST API for programmatic access:

- **Text Conversion**: `POST /api/convert`
- **Markdown Conversion (MarkItDown)**: `POST /api/convert-to-md`
- **Markdown Conversion (Docling)**: `POST /api/convert-to-md-docling`
- **HTML Conversion (Docling)**: `POST /api/convert-to-html-docling`
- **JSON Conversion (Docling)**: `POST /api/convert-to-json-docling`
- **Markdown Conversion (Marker)**: `POST /api/convert-to-md-marker`
- **HTML Conversion (Marker)**: `POST /api/convert-to-html-marker`
- **JSON Conversion (Marker)**: `POST /api/convert-to-json-marker`
- **Batch Text Conversion**: `POST /api/convert-folder`
- **Batch Markdown Conversion (MarkItDown)**: `POST /api/convert-to-md-folder`
- **Batch Markdown Conversion (Docling)**: `POST /api/convert-to-md-docling-folder`
- **Batch Markdown Conversion (Marker)**: `POST /api/convert-to-md-marker-folder`

For detailed documentation and testing, visit the API Documentation page through the web interface.

## Supported Formats

### Input Formats
- **Office Documents**: DOC, DOCX, XLS, XLSX, PPT, PPTX, CSV
- **Text/Markup**: PDF, TXT, MD, HTML, XHTML, EPUB
- **Images**: PNG, JPEG, TIFF, BMP
- **Audio**: MP3, WAV

### Output Formats
- **Plain Text**
- **Markdown**
- **HTML**
- **JSON**

## System screenshot

### Interface

#### Home page
![Home page](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/home.png?raw=true)
#### API call
![API call](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/API.png?raw=true)
#### Original format
![Original format](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/original%20format.png?raw=true)
#### MD format
![MD format](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/MD%20format.png?raw=true)
### Effect
#### WORD file
![WORD file](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/word1.png?raw=true)
#### WORD conversion effect
![WORD conversion effect](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/word2.png?raw=true)
#### WORD table conversion effect
![WORD table conversion effect](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/word4.png?raw=true)
#### Execel effect
![Execel effect](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/excel2.png?raw=true)
#### PPT effect
![PPT effect](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/ppt1.png?raw=true)
#### docling pdf to md
![docling pdf to md](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/docling_pdf_md.png?raw=true)

## Installation and Deployment

### Local Installation

#### Requirements

- Python 3.6+
- Flask
- pytesseract (for OCR functionality)
- Tesseract OCR engine
- MarkItDown library
- Docling library (optional, for enhanced PDF conversion)
- Marker library (optional, for high-precision document conversion)

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
   
   # For Marker support
   pip install marker-pdf
   # For additional format support
   pip install marker-pdf[full]
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

- **Multiple Conversion Engines**: Choose the best engine for your document type - MarkItDown for Office documents, Docling for PDFs, Marker for high-precision needs
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
- Marker requires PyTorch and may need specific PyTorch installation for GPU acceleration

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