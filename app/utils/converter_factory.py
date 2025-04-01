"""
转换器工厂模块
提供不同文档格式转换的抽象工厂
"""
import os
import logging
import traceback
from abc import ABC, abstractmethod

# 配置日志
logger = logging.getLogger(__name__)

class BaseConverter(ABC):
    """转换器基类，定义了转换器的通用接口"""
    
    @abstractmethod
    def convert_to_text(self, file_path):
        """将文件转换为纯文本格式"""
        pass
    
    @abstractmethod
    def convert_to_markdown(self, file_path):
        """将文件转换为Markdown格式"""
        pass
    
    @property
    @abstractmethod
    def supported_input_formats(self):
        """支持的输入文件格式列表"""
        pass
    
    @property
    @abstractmethod
    def name(self):
        """转换器名称"""
        pass
    
    @property
    def description(self):
        """转换器描述"""
        return f"{self.name} 文档转换器"
    
    def is_format_supported(self, file_ext):
        """检查文件扩展名是否支持"""
        return file_ext.lower() in self.supported_input_formats

class MarkItDownConverter(BaseConverter):
    """使用MarkItDown库的转换器"""
    
    def __init__(self):
        self._has_markitdown = False
        try:
            from markitdown import MarkItDown
            self._has_markitdown = True
            self._markitdown = MarkItDown(enable_plugins=False)
            logger.info("成功初始化MarkItDown转换器")
        except ImportError:
            logger.warning("无法导入MarkItDown库，将使用替代方法")
    
    @property
    def name(self):
        return "MarkItDown"
    
    @property
    def description(self):
        return "优化处理Office文档（DOCX, XLSX, PPTX）的转换器，速度快，准确率高"
    
    @property
    def supported_input_formats(self):
        return [
            '.doc', '.docx', '.xls', '.xlsx', 
            '.ppt', '.pptx', '.pdf', '.txt', 
            '.md', '.mp3', '.wav', '.xml'
        ]
    
    def convert_to_text(self, file_path):
        """使用现有的转换函数进行文本转换"""
        from app.utils.converters import (
            convert_docx, convert_xlsx, convert_pptx,
            convert_pdf, convert_txt, convert_md, convert_xml
        )
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 根据文件类型调用相应的转换函数
        if file_ext in ['.doc', '.docx']:
            return convert_docx(file_path)
        elif file_ext in ['.xls', '.xlsx']:
            return convert_xlsx(file_path)
        elif file_ext in ['.ppt', '.pptx']:
            return convert_pptx(file_path)
        elif file_ext == '.pdf':
            return convert_pdf(file_path)
        elif file_ext == '.txt':
            return convert_txt(file_path)
        elif file_ext == '.md':
            return convert_md(file_path)
        elif file_ext == '.xml':
            return convert_xml(file_path)
        elif file_ext in ['.mp3', '.wav']:
            return "音频文件支持Markdown格式导出，请使用转MD功能"
        else:
            error_msg = f"不支持的文件格式: {file_ext}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def convert_to_markdown(self, file_path):
        """使用MarkItDown将文件转换为Markdown格式"""
        try:
            logger.info(f"使用MarkItDown开始处理文件: {file_path}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                error_msg = f"文件不存在: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            if self._has_markitdown:
                # 转换文件
                result = self._markitdown.convert(file_path)
                
                # 获取Markdown内容
                markdown_content = result.text_content
                
                logger.info(f"MarkItDown转换成功，生成了 {len(markdown_content)} 个字符的Markdown内容")
                return markdown_content
            else:
                logger.warning("MarkItDown库不可用，使用替代方法")
                from app.utils.converters import convert_to_markdown
                return convert_to_markdown(file_path)
        except Exception as e:
            error_msg = f"MarkItDown转换失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise Exception(error_msg)

class DoclingConverter(BaseConverter):
    """使用Docling库的转换器"""
    
    def __init__(self):
        self._has_docling = False
        self._docling = None
        
        try:
            import docling
            self._has_docling = True
            self._docling = docling
            logger.info("成功初始化Docling转换器")
            
            # 检查是否有CUDA支持
            self._has_cuda = self._check_cuda_support()
            if self._has_cuda:
                logger.info("Docling检测到CUDA支持，将使用GPU加速")
            else:
                logger.info("Docling未检测到CUDA支持，将使用CPU模式")
                
        except ImportError:
            logger.warning("无法导入Docling库，此转换器将不可用")
    
    def _check_cuda_support(self):
        """检查系统是否支持CUDA"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    @property
    def name(self):
        return "Docling"
    
    @property
    def description(self):
        return "针对PDF格式优化的转换器，具有表格识别和VLM能力，对PDF的准确率高"
    
    @property
    def is_available(self):
        """检查Docling是否可用"""
        return self._has_docling
    
    @property
    def supported_input_formats(self):
        """Docling支持的输入文件格式"""
        return [
            '.pdf', '.docx', '.xlsx', '.pptx', '.csv',
            '.html', '.xhtml', '.png', '.jpg', '.jpeg',
            '.tiff', '.bmp', '.md', '.xml'
        ]
    
    def convert_to_text(self, file_path):
        """使用Docling将文件转换为纯文本格式"""
        try:
            if not self._has_docling:
                raise ImportError("Docling库不可用")
            
            logger.info(f"使用Docling开始将文件转换为文本: {file_path}")
            
            # 使用Docling的转换器（先转为Markdown再转为纯文本）
            md_content = self.convert_to_markdown(file_path)
            
            # 移除Markdown格式，获取纯文本
            lines = md_content.split('\n')
            text_lines = []
            
            for line in lines:
                # 移除标题标记 # 
                if line.startswith('#'):
                    text_lines.append(line.lstrip('#').strip())
                    continue
                
                # 移除列表标记 - *
                if line.startswith('-') or line.startswith('*'):
                    text_lines.append(line[1:].strip())
                    continue
                
                # 保留其他行
                text_lines.append(line)
            
            text_content = '\n'.join(text_lines)
            logger.info(f"Docling文本转换完成，生成了 {len(text_content)} 个字符")
            return text_content
            
        except Exception as e:
            error_msg = f"Docling文本转换失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise Exception(error_msg)
    
    def convert_to_markdown(self, file_path):
        """使用Docling将文件转换为Markdown格式"""
        try:
            if not self._has_docling:
                raise ImportError("Docling库不可用")
            
            logger.info(f"使用Docling开始将文件转换为Markdown: {file_path}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                error_msg = f"文件不存在: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # 获取文件扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.supported_input_formats:
                error_msg = f"Docling不支持此文件格式: {file_ext}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 使用Docling处理文件
            file_name = os.path.basename(file_path)
            
            # 将文件转换为Markdown
            device = "cuda" if self._has_cuda else "cpu"
            
            # 使用正确的Docling API调用
            from docling.document_converter import DocumentConverter
            converter = DocumentConverter()
            result = converter.convert(file_path)
            markdown_content = result.document.export_to_markdown()
            
            logger.info(f"Docling转换成功，生成了Markdown内容")
            return markdown_content
            
        except Exception as e:
            error_msg = f"Docling转换失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise Exception(error_msg)
            
    def convert_to_html(self, file_path):
        """使用Docling将文件转换为HTML格式"""
        try:
            if not self._has_docling:
                raise ImportError("Docling库不可用")
            
            logger.info(f"使用Docling开始将文件转换为HTML: {file_path}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                error_msg = f"文件不存在: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # 获取文件扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.supported_input_formats:
                error_msg = f"Docling不支持此文件格式: {file_ext}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 使用Docling处理文件
            file_name = os.path.basename(file_path)
            
            # 将文件转换为HTML
            device = "cuda" if self._has_cuda else "cpu"
            
            # 使用Docling API调用
            from docling.document_converter import DocumentConverter
            converter = DocumentConverter()
            result = converter.convert(file_path)
            html_content = result.document.export_to_html()
            
            logger.info(f"Docling转换成功，生成了HTML内容")
            return html_content
            
        except Exception as e:
            error_msg = f"Docling HTML转换失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise Exception(error_msg)
            
    def convert_to_json(self, file_path):
        """使用Docling将文件转换为JSON格式"""
        try:
            if not self._has_docling:
                raise ImportError("Docling库不可用")
            
            logger.info(f"使用Docling开始将文件转换为JSON: {file_path}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                error_msg = f"文件不存在: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # 获取文件扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.supported_input_formats:
                error_msg = f"Docling不支持此文件格式: {file_ext}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 使用Docling处理文件
            file_name = os.path.basename(file_path)
            
            # 将文件转换为JSON
            device = "cuda" if self._has_cuda else "cpu"
            
            # 使用Docling API调用
            from docling.document_converter import DocumentConverter
            converter = DocumentConverter()
            result = converter.convert(file_path)
            json_content = result.document.to_dict()
            
            logger.info(f"Docling转换成功，生成了JSON内容")
            return json_content
            
        except Exception as e:
            error_msg = f"Docling JSON转换失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise Exception(error_msg)

class ConverterFactory:
    """转换器工厂类，负责创建和管理各种转换器实例"""
    
    def __init__(self):
        self._converters = {}
        self._register_converters()
    
    def _register_converters(self):
        """注册所有可用的转换器"""
        # 注册MarkItDown转换器
        markitdown_converter = MarkItDownConverter()
        self._converters['markitdown'] = markitdown_converter
        
        # 注册Docling转换器
        docling_converter = DoclingConverter()
        if docling_converter.is_available:
            self._converters['docling'] = docling_converter
    
    def get_converter(self, converter_name=None, file_ext=None):
        """获取转换器实例
        
        如果指定了converter_name，则返回对应的转换器
        如果指定了file_ext，则返回支持该文件格式的首个转换器
        如果两者都未指定，则返回默认转换器（MarkItDown）
        """
        if converter_name:
            if converter_name in self._converters:
                return self._converters[converter_name]
            else:
                raise ValueError(f"未知的转换器: {converter_name}")
        
        if file_ext:
            for converter in self._converters.values():
                if converter.is_format_supported(file_ext):
                    return converter
        
        # 返回默认转换器
        return self._converters.get('markitdown')
    
    def get_converters_for_format(self, file_ext):
        """获取支持指定文件格式的所有转换器"""
        supported_converters = []
        
        for converter in self._converters.values():
            if converter.is_format_supported(file_ext):
                supported_converters.append(converter)
        
        return supported_converters
    
    def get_default_converter(self):
        """获取默认转换器（MarkItDown）"""
        return self._converters.get('markitdown')
    
    def get_available_converters(self):
        """获取所有可用的转换器"""
        return list(self._converters.values())
    
    def get_converter_names(self):
        """获取所有转换器的名称"""
        return list(self._converters.keys())

# 创建全局转换器工厂实例
converter_factory = ConverterFactory() 