# X2Knowledge - Document Conversion Tool

X2Knowledge is an efficient open source knowledge extractor tool designed for enterprise knowledge base construction. It supports intelligent conversion of files in various formats such as PDF, Word, PPT, Excel, WAV, MP3, etc. into structured TXT or Markdown formats, helping users to quickly and standardizedly enter various types of documents into the enterprise knowledge base system. Through advanced format parsing and content extraction technology, the project significantly improves the efficiency and accuracy of knowledge conversion and is an ideal pre-processing tool for RAG (retrieval enhancement generation) applications and enterprise knowledge management.

This is a Python Flask-based web application that can convert various document formats (Word, Excel, PowerPoint, PDF, TXT and Markdown) into plain text or structured Markdown.

## Latest Updates (v2.1.0)

- **Enhanced Markdown Preview**: Using marked.js library for better Markdown rendering with perfect support for tables and images
- **Added Image Interaction**: Click on images to view them in fullscreen mode
- **Code Syntax Highlighting**: Added highlight.js for syntax highlighting of code blocks
- **Docker Deployment Support**: Added Dockerfile and docker-compose configuration
- **Fixed API Documentation**: Improved Markdown tab switching in API documentation

-[X2Knowledge - Document Conversion Tool](app/static/img/screenshot.png)

## Features

- **Convert multiple file formats to text or Markdown**
  - Support for Word (.doc, .docx), Excel (.xls, .xlsx), PowerPoint (.ppt, .pptx), PDF, text files, and more
  - Maintains document structure in Markdown conversion mode
  - Extracts text from images via OCR

- **Markdown Conversion**
  - Preserves document structure including headings, lists, and tables
  - Maintains links and formatting
  - Preview capability for converted Markdown

- **OCR Support**
  - Automatically extracts text from images embedded in documents
  - Works with images in Word, PowerPoint, and PDF files

- **Audio Conversion** (New)
  - Convert audio files (.mp3, .wav) to text/Markdown description
  - Extracts metadata including duration, channels, and sample rate

- **UTF-8 Encoding**
  - Automatically converts documents to UTF-8 encoding
  - Resolves Chinese character display issues
  - No manual encoding configuration needed

- **Large File Support**
  - Supports files up to 50MB
  - Efficient processing of large documents

## Usage

1. Select the conversion mode (Text or Markdown)
2. Upload your document (or drag and drop)
3. View, copy or download the conversion result
4. Use the Markdown preview feature to see formatted results (when using Markdown mode)

## REST API

The tool provides a REST API for programmatic access:

- **Text Conversion**: `POST /api/convert`
- **Markdown Conversion**: `POST /api/convert-to-md`

For detailed documentation and testing, visit the API Documentation page through the web interface.

## System screenshot
### Interface
#### Home page
![Home page](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/home.png?raw=true)
#### API call
![API call](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/API.png?raw=true)
#### Original format
![Original format](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/original%20format.png?raw=true)
#### MD format
![MD format](https://github.com/leonda123/X2Knowledge/blob/main/screenshot/original%20format.png?raw=true)
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

## Installation and Deployment

### Local Installation

#### Requirements

- Python 3.6+
- Flask
- pytesseract (for OCR functionality)
- Tesseract OCR engine

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

3. Install Tesseract OCR engine (for OCR functionality):
   - Windows: Download and install from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

4. Run the application:
   ```
   flask run
   ```

5. Open a web browser and navigate to `http://127.0.0.1:5000/`

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

## Future Plans

### Large Language Model Integration
- **DeepSeek Integration**: Plans to support DeepSeek for text semantic understanding and structured extraction
- **GPT Model Support**: Add integration with OpenAI GPT-3.5/4 for advanced document understanding and summary generation
- **Open-Source Model Support**: Add support for major open-source LLMs for document processing and enhancement

### Inference Platform Support
- **Ollama Local Deployment**: Support using Ollama for local deployment of open-source models for document processing
- **vLLM High-Performance Inference**: Plan to integrate vLLM to provide more efficient model inference capabilities
- **Model Quantization Support**: Add support for GPTQ, GGUF and other quantized models to reduce resource requirements

### RAG Enhancement
- **Automatic Document Chunking**: Intelligent segmentation algorithms to provide optimal retrieval granularity for RAG applications
- **Vector Embedding Generation**: Directly generate document vector embeddings to accelerate knowledge base construction
- **Knowledge Graph Export**: Extract entity relationships from documents to generate preliminary knowledge graphs

## Version History

### v2.1.0 (Current)
- Enhanced Markdown rendering with perfect table and image support
- Added Docker deployment support
- Improved image interaction experience
- Added code syntax highlighting

### v2.0.0
- Added Markdown conversion functionality
- Added Markdown preview capability
- Added support for audio file conversion
- Increased file size limit to 50MB
- Improved error handling and user feedback
- Enhanced documentation

### v1.0.0
- Initial release with text conversion support
- OCR functionality
- UTF-8 encoding conversion
- Basic web interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [pytesseract](https://github.com/madmaze/pytesseract) for OCR functionality
- [Flask](https://flask.palletsprojects.com/) web framework
- [Markidown](https://github.com/microsoft/markitdown.git)Markidown
- [marked.js](https://marked.js.org/) for Markdown rendering
- [highlight.js](https://highlightjs.org/) for code syntax highlighting
- Various document processing libraries

---

Developed with ❤️ using Flask and JavaScript 

Project Links: [GitHub](https://github.com/leonda123/X2Knowledge.git) | [Gitee](https://gitee.com/leonda/X2Knowledge.git) 