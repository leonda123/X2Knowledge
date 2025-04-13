import os
import logging
import traceback
import time
import re
import requests
from bs4 import BeautifulSoup
import html2text

# 配置日志
logger = logging.getLogger(__name__)

class URLConverter:
    """URL内容转换器，用于将网页内容转换为Markdown格式"""
    
    def __init__(self):
        """初始化URL转换器"""
        self.html2text_converter = html2text.HTML2Text()
        self.html2text_converter.ignore_links = False
        self.html2text_converter.ignore_images = False
        self.html2text_converter.ignore_tables = False
        self.html2text_converter.unicode_snob = True
        self.html2text_converter.body_width = 0  # 禁用换行
        
    def fetch_url_content(self, url):
        """
        从URL获取网页内容
        
        Args:
            url: 网页URL地址
            
        Returns:
            str: 网页的HTML内容
        """
        try:
            logger.info(f"开始获取URL内容: {url}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
            }
            
            # 发送请求获取网页内容
            response = requests.get(url, headers=headers, timeout=30)
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"获取URL内容失败，HTTP状态码: {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # 尝试确定网页编码
            html_content = response.text
            
            logger.info(f"URL内容获取成功，长度: {len(html_content)} 字符")
            return html_content
        except Exception as e:
            error_msg = f"获取URL内容失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise Exception(error_msg)
    
    def remove_header_footer(self, html_content):
        """
        尝试移除网页中的页眉和页脚
        
        Args:
            html_content: 网页HTML内容
            
        Returns:
            str: 处理后的HTML内容
        """
        try:
            logger.info("开始移除页眉和页脚")
            
            # 解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除常见的页眉、页脚、导航、侧边栏等元素
            for element in soup.select('header, footer, nav, aside, .header, .footer, .nav, .sidebar, .menu, .advertisement, .ad, .ads, .advert'):
                element.decompose()
            
            # 移除脚本和样式元素
            for element in soup.select('script, style'):
                element.decompose()
            
            # 输出清理后的HTML
            cleaned_html = str(soup)
            
            logger.info(f"页眉和页脚移除完成，处理后长度: {len(cleaned_html)} 字符")
            return cleaned_html
        except Exception as e:
            error_msg = f"移除页眉和页脚失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            logger.warning("由于错误，将返回原始HTML内容")
            return html_content
    
    def extract_content_by_selector(self, html_content, selector):
        """
        使用CSS选择器提取网页中的特定内容
        
        Args:
            html_content: 网页HTML内容
            selector: CSS选择器，可以是标签名、ID或类名等
            
        Returns:
            str: 处理后的HTML内容
        """
        try:
            logger.info(f"开始使用选择器提取内容: {selector}")
            
            # 解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 使用选择器查找元素
            selected_elements = soup.select(selector)
            
            if not selected_elements:
                logger.warning(f"未找到与选择器 '{selector}' 匹配的元素")
                return html_content
            
            # 创建一个新的BS对象，包含我们找到的所有元素
            new_soup = BeautifulSoup('<div></div>', 'html.parser')
            main_div = new_soup.div
            
            # 添加所有找到的元素
            for element in selected_elements:
                main_div.append(element.extract())
            
            # 输出提取的HTML
            extracted_html = str(new_soup)
            
            logger.info(f"内容提取完成，提取后长度: {len(extracted_html)} 字符")
            return extracted_html
        except Exception as e:
            error_msg = f"使用选择器提取内容失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            logger.warning("由于错误，将返回原始HTML内容")
            return html_content
    
    def convert_html_to_markdown(self, html_content):
        """
        将HTML内容转换为Markdown格式
        
        Args:
            html_content: 网页HTML内容
            
        Returns:
            str: Markdown格式的文本
        """
        try:
            logger.info("开始将HTML转换为Markdown")
            
            # 使用html2text转换
            markdown_text = self.html2text_converter.handle(html_content)
            
            # 简单清理Markdown内容
            # 移除过多的空行
            markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
            
            logger.info(f"HTML转Markdown完成，长度: {len(markdown_text)} 字符")
            return markdown_text
        except Exception as e:
            error_msg = f"HTML转Markdown失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise Exception(error_msg)
    
    def convert_url_to_markdown(self, url, remove_header_footer=True, selector=None):
        """
        将URL网页内容转换为Markdown格式
        
        Args:
            url: 网页URL地址
            remove_header_footer: 是否移除页眉页脚
            selector: CSS选择器，用于选择页面的特定内容，如 '#content'、'.article'、'main' 等
            
        Returns:
            str: Markdown格式的文本
        """
        try:
            # 获取网页内容
            html_content = self.fetch_url_content(url)
            
            # 如果提供了CSS选择器，先根据选择器提取内容
            if selector:
                html_content = self.extract_content_by_selector(html_content, selector)
            
            # 移除页眉页脚（如果需要）
            if remove_header_footer:
                html_content = self.remove_header_footer(html_content)
            
            # 转换为Markdown
            markdown_text = self.convert_html_to_markdown(html_content)
            
            return markdown_text
        except Exception as e:
            error_msg = f"URL转Markdown失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise Exception(error_msg) 