# X2Knowledge API Documentation

## Table of contents
- [File to text](#File to text)
- [File to text](#File to text-1)
- [Convert the file to text and save](#Convert the file to text and save)
- [Use Markitdown to convert files to Markdown](#Use Markitdown to convert files to Markdown)
- [Use Markitdown to convert files to Markdown](#Use Markitdown to convert files to Markdown-1)
- [Use Markitdown to convert files to Markdown and save](#Use Markitdown to convert files to Markdown and save)
- [ Docling conversion](#docling conversion)
- [Use Docling to convert files to Markdown format](#Use Docling to convert files to Markdown format)
- [Use Docling to convert the file to Markdown format and save it to the specified directory](#Use Docling to convert the file to Markdown format and save it to the specified directory)
- [Use Docling to convert online documents to Markdown format](#Use Docling to convert online documents to Markdown format)
- [Use Docling to convert online documents to Markdown format and save to a specified directory](#Use Docling to convert online documents to Markdown format and save to a specified directory)
- [Use Docling to convert files to Markdown format and export images](#Use Docling to convert files to Markdown format and export images)
- [Use Docling to convert files to HTML format](#Use Docling to convert files to HTML format)
- [Use Docling to extract tables from files and export them to a specified format](#Use Docling to extract tables from files and export them to a specified format)
- [URL to Markdown](#url to markdown)
- [Convert web page URL to Markdown format](#Convert web page URL to Markdown format)
- [Convert the webpage URL to Markdown format and save it to the specified directory](#Convert the webpage URL to Markdown format and save it to the specified directory)
- [Warehouse preprocessing](#Warehouse preprocessing)
- [Pre-processing before storage: convert Markdown to JSON and CSV format](#Pre-processing before storage: convert Markdown to JSON and CSV format)

---

## Convert file to text

### Convert files to text

**Interface**: `POST / api /convert`

**Description**: Convert files of various formats to plain text format

**parameter**:
- `file`: the file to be converted to text, supporting doc, docx, xls , xlsx, ppt, pptx, pdf, txt, md and other formats (required)

**response**:
- 200: Conversion successful
``` json
{
"text": "Converted text content"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

### Convert files to text and save

**Interface**: `POST / api /convert-file`

**Description**: Convert files of various formats to plain text format and save as .txt files

**parameter**:
- `file`: the file to be converted to text (required)
- ` output_dir` : Directory path for output files (required)

**response**:
- 200: Conversion successful
``` json
{
" output_path ": "Saved file path",
"filename": "Original file name",
" file_size ": "File size (bytes)",
" processing_time ": "Processing time (seconds)"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

## Use Markitdown to convert files to Markdown

Convert files to Markdown using Markitdown

**Interface**: `POST / api /convert-to-md`

**Description**: Use the MarkItDown engine to convert files in various formats to Markdown format

**parameter**:
- `file`: the file to be converted to Markdown, supported file formats (PDF, DOCX, PPTX, XLSX, XLS, CSV, JSON, XML, WAV, MP3) (required)

**response**:
- 200: Conversion successful
``` json
{
"text": "Converted Markdown text",
"filename": "Original file name",
" file_size ": "File size (bytes)",
" processing_time ": "Processing time (seconds)"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

### Use Markitdown to convert the file to Markdown and save it

**Interface**: `POST / api /convert-to-md-file`

**Description**: Use the MarkItDown engine to convert files of various formats into Markdown format and save them as files

**parameter**:
- `file`: the file to be converted to Markdown, supporting file formats supported by MarkItDown (required)
- ` output_dir` : Directory path for output files (required)

**response**:
- 200: Conversion successful
``` json
{
" output_path ": "Saved file path",
"filename": "Original file name",
" file_size ": "File size (bytes)",
" processing_time ": "Processing time (seconds)"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

## Docling Conversion

### Convert files to Markdown format using Docling

**Interface**: `POST / api /convert-to-md - docling`

**Description**: Use the Docling engine to convert files in various formats to Markdown format

**parameter**:
- `file`: the file to be converted to Markdown, supported file formats (PDF, DOCX, XLSX, PPTX, Markdown, AsciiDoc , HTML, XHTML, CSV, PNG, JPEG, TIFF, BMP) (required)

**response**:
- 200: Conversion successful
``` json
{
"text": "Converted Markdown text",
"filename": "Original file name",
" file_size ": "File size (bytes)",
" processing_time ": "Processing time (seconds)"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

### Use Docling to convert the file to Markdown format and save it to the specified directory

**Interface**: `POST / api /convert-to-md-file - docling`

**Description**: Use the Docling engine to convert files of various formats into Markdown format and save them as files

**parameter**:
- `file`: the file to be converted to Markdown, supported file formats (PDF, DOCX, XLSX, PPTX, Markdown, AsciiDoc , HTML, XHTML, CSV, PNG, JPEG, TIFF, BMP) (required)
- ` output_dir` : Directory path for output files (required)

**response**:
- 200: Conversion successful
``` json
{
" output_path ": "Saved file path",
"filename": "Original file name",
" file_size ": "File size (bytes)",
" processing_time ": "Processing time (seconds)",
"converter": "The name of the converter to use"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

Convert online documents to Markdown format using Docling

**Interface**: `POST / api /convert-online - docling`

**Description**: Use Docling engine to convert online documents (such as PDF, DOC, etc.) into Markdown format without downloading files

**parameter**:
- ` url` : URL of the online document to be converted to Markdown, supports PDF and other document formats (required)
- ` file_type `: document type (such as pdf), which needs to be specified if the URL does not contain a suffix (optional)

**response**:
- 200: Conversion successful
``` json
{
"text": "Converted Markdown text",
" url ": "Original URL",
" processing_time ": "Processing time (seconds)",
"converter": "Converter to use"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

### Use Docling to convert online documents to Markdown format and save them to the specified directory

**Interface**: `POST / api /convert-online -docling -save`

**Description**: Use the Docling engine to convert online documents (such as PDF, DOC, etc.) into Markdown format and save them as files

**parameter**:
- ` url` : URL of the online document to be converted to Markdown, supports PDF and other document formats (required)
- ` output_dir` : Directory path for output files (required)
- ` file_type `: document type (such as pdf), which needs to be specified if the URL does not contain a suffix (optional)

**response**:
- 200: Conversion successful
``` json
{
" output_path ": "Saved file path",
" url ": "Original URL",
"filename": "Generated file name",
" processing_time ": "Processing time (seconds)",
"converter": "Converter to use"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

### Use Docling to convert files to Markdown format and export images

**Interface**: `POST / api /convert-to-md-images-file - docling`

**Description**: Use the Docling engine to convert files of various formats into Markdown format and export images in the document (including page images, tables and images)

**parameter**:
- `file`: the file to be converted to Markdown and images to be extracted, supported file formats (PDF, DOCX, XLSX, PPTX, Markdown, AsciiDoc , HTML, XHTML, CSV, PNG, JPEG, TIFF, BMP) (required)
- ` output_dir` : The directory path of the output files, used to save Markdown and images (required)

**response**:
- 200: Conversion successful
``` json
{
" output_path ": "Saved Markdown file path",
"filename": "Original file name",
" file_size ": "File size (bytes)",
" processing_time ": "Processing time (seconds)",
"converter": "The name of the converter used",
" page_count ": "Number of document pages",
" table_count ": "Number of tables extracted",
" picture_count ": "Number of pictures extracted",
" page_images ": "Path list of page images",
" table_images ": "Path list of table images",
" picture_images ": "Path list of pictures"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

### Convert files to HTML format using Docling

**Interface**: `POST / api /convert-to-html - docling`

**Description**: Use the Docling engine to convert files of various formats into HTML format

**parameter**:
- `file`: the file to be converted to HTML, supported file formats (PDF, DOCX, XLSX, PPTX, Markdown, AsciiDoc , HTML, XHTML, CSV, PNG, JPEG, TIFF, BMP) (required)

**response**:
- 200: Conversion successful
``` json
{
"html": "Converted HTML text",
"filename": "Original file name",
" file_size ": "File size (bytes)",
" processing_time ": "Processing time (seconds)"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

### Use Docling to extract the table in the file and export it to the specified format

**Interface**: `POST / api /export-tables - docling`

**Description**: Use the Docling engine to extract tables from documents and export them to Markdown, CSV or HTML format as needed

**parameter**:
- `file`: the file to extract the table from, supported file formats (PDF, DOCX, XLSX, PPTX, HTML, XHTML, CSV) (required)
- ` output_dir` : Output directory path where table files are saved (required)
- ` export_formats `: export format, multiple formats are separated by commas, support md, csv, html, all are exported by default (optional)

**response**:
- 200: Table extraction successful
``` json
{
"filename": "Original file name",
" file_size ": "File size (bytes)",
" processing_time ": "Processing time (seconds)",
" export_formats ": ["Export format list, such as md, csv, html"],
" table_count ": "Number of tables extracted",
    "tables": [
      {
"index": "Table index (starting from 1)",
" csv_path ": "The path where the CSV format table file is saved (if exported in CSV format)",
" md_path ": "The path where the Markdown format table file is saved (if exported to MD format)",
" html_path ": "The path where the HTML format table file is saved (if exported to HTML format)"
      }
    ]
  }
  ```
- 200 (No Table): There is no table in the document
``` json
{
"warning": "No table detected in the document",
"filename": "Original file name",
" file_size ": "File size (bytes)",
" processing_time ": "Processing time (seconds)",
" table_count ": 0,
    "tables": []
  }
  ```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

## Convert URL to Markdown

### Convert web page URL to Markdown format

**Interface**: `POST / api /convert- url -to-md`

**Description**: Use the Docling engine to convert URL webpage content into Markdown format. You can choose to remove headers and footers or use CSS selectors to extract specific content.

**parameter**:
- ` url` : URL of the web page to be converted to Markdown (required)
- ` remove_header_footer` : whether to remove the header and footer of the web page (optional, default value: true)
- `selector`: CSS selector used to select specific content of the page, such as '#content', '.article', 'main', etc. (optional)

**response**:
- 200: Conversion successful
``` json
{
"text": "Converted Markdown text",
" url ": "Original URL",
" processing_time ": "Processing time (seconds)"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

### Convert the webpage URL to Markdown format and save it to the specified directory

**Interface**: `POST / api /convert- url -to-md-file`

**Description**: Use the Docling engine to convert URL webpage content into Markdown format. You can choose to remove headers and footers or use CSS selectors to extract specific content and save it as a file

**parameter**:
- ` url` : URL of the web page to be converted to Markdown (required)
- ` output_dir` : Directory path for output files (required)
- ` remove_header_footer` : whether to remove the header and footer of the web page (optional, default value: true)
- `selector`: CSS selector used to select specific content of the page, such as '#content', '.article', 'main', etc. (optional)

**response**:
- 200: Conversion successful
``` json
{
" output_path ": "Saved file path",
" url ": "Original URL",
"filename": "Generated file name",
" processing_time ": "Processing time (seconds)"
}
```
- 400: Bad Request
``` json
{
"error": "Error message"
}
```
- 500: Server Error
``` json
{
"error": "Error message",
"details": "Detailed error information"
}
```

## Pre-processing before entering the warehouse

### Pre-processing before storage: convert Markdown to JSON and CSV formats

**Interface**: `POST /preprocess-for-storage`

**Description**: Process Markdown files or text into JSON and CSV formats for data preparation before knowledge base entry

**parameter**:
- `file`: Markdown file, either provided with the text parameter (optional)
- `text`: Markdown text content, either provided with the file parameter or not (optional)
- ` output_dir` : Output directory path, defaults to app.config ['STORAGE_FOLDER'] (optional)
- `filename`: output file name (without extension), defaults to original file name or timestamp (optional)
- `format`: output format, optional json , csv or both (output two formats at the same time), the default is both (optional)

**Processing rules**:
1. Collect the title (#) as question, and collect all the text content under the title as answer, until the next title appears
2. If it is a second-level title or above, the question title will be concatenated with the parent title in the format of "{parent title},{current title}"
3. Only headers with content will be processed, empty headers will be ignored

**Output JSON format**:
``` json
[
{
"question": "Title text",
"answer": "Content text under the title"
},
...
]
```

**response**:
- 200: Processed successfully
``` json
{
" json_path ": "Generated JSON file path (returned when format is json or both)",
" csv_path ": "Generated CSV file path (returned when format is csv or both)",
" qa_count ": "Number of question-answer pairs generated"
}
```
- 400: Incorrect request parameters
``` json
{
"error": "Error message"
}
```
- 500: Internal server error
``` json
{
"error": "Error message",
"details": "Detailed error information"
  }
  ```
