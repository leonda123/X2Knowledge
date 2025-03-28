/**
 * API测试页面JavaScript
 * 提供API接口测试功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 元素获取
    const apiTestTabs = document.querySelectorAll('.api-test-tab');
    const apiTestContents = document.querySelectorAll('.api-test-content');
    const apiFileInputText = document.getElementById('apiFileInputText');
    const apiFileInputMarkdown = document.getElementById('apiFileInputMarkdown');
    const apiSubmitText = document.getElementById('apiSubmitText');
    const apiSubmitMarkdown = document.getElementById('apiSubmitMarkdown');
    const apiTestDropAreaText = document.getElementById('apiTestDropAreaText');
    const apiTestDropAreaMarkdown = document.getElementById('apiTestDropAreaMarkdown');
    const apiTestLoadingIndicator = document.getElementById('apiTestLoadingIndicator');
    const apiTestResponseContainer = document.getElementById('apiTestResponseContainer');
    const apiTestResponseTitle = document.getElementById('apiTestResponseTitle');
    const apiTestResponseStats = document.getElementById('apiTestResponseStats');
    const apiTestResponseContent = document.getElementById('apiTestResponseContent');
    const copyResponseBtn = document.getElementById('copyResponseBtn');
    const downloadResponseBtn = document.getElementById('downloadResponseBtn');
    const apiMdControls = document.querySelector('.api-md-controls');
    const apiMdPreview = document.querySelector('.api-md-preview');
    
    // 当前状态
    let currentApiTestTab = 'text';
    let currentResponseData = null;
    let originalMarkdown = '';
    
    // 标签切换功能
    apiTestTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // 移除所有active类
            apiTestTabs.forEach(t => t.classList.remove('active'));
            apiTestContents.forEach(c => c.classList.remove('active'));
            
            // 添加active类到当前tab
            this.classList.add('active');
            currentApiTestTab = this.dataset.testTab;
            document.getElementById(`test-content-${currentApiTestTab}`).classList.add('active');
        });
    });
    
    // 拖拽事件处理
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        apiTestDropAreaText.addEventListener(eventName, preventDefault, false);
        apiTestDropAreaMarkdown.addEventListener(eventName, preventDefault, false);
    });
    
    function preventDefault(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        apiTestDropAreaText.addEventListener(eventName, () => highlight(apiTestDropAreaText), false);
        apiTestDropAreaMarkdown.addEventListener(eventName, () => highlight(apiTestDropAreaMarkdown), false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        apiTestDropAreaText.addEventListener(eventName, () => unhighlight(apiTestDropAreaText), false);
        apiTestDropAreaMarkdown.addEventListener(eventName, () => unhighlight(apiTestDropAreaMarkdown), false);
    });
    
    function highlight(element) {
        element.classList.add('dragover');
    }
    
    function unhighlight(element) {
        element.classList.remove('dragover');
    }
    
    // 处理拖放文件
    apiTestDropAreaText.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            apiFileInputText.files = files;
            handleApiTest(files[0], 'text');
        }
    }, false);
    
    apiTestDropAreaMarkdown.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            apiFileInputMarkdown.files = files;
            handleApiTest(files[0], 'markdown');
        }
    }, false);
    
    // 处理文件选择
    apiFileInputText.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleApiTest(this.files[0], 'text');
        }
    });
    
    apiFileInputMarkdown.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleApiTest(this.files[0], 'markdown');
        }
    });
    
    // 提交按钮事件
    apiSubmitText.addEventListener('click', function() {
        if (apiFileInputText.files.length > 0) {
            handleApiTest(apiFileInputText.files[0], 'text');
        } else {
            alert(getTranslatedText('select-file-alert', '请先选择文件'));
        }
    });
    
    apiSubmitMarkdown.addEventListener('click', function() {
        if (apiFileInputMarkdown.files.length > 0) {
            handleApiTest(apiFileInputMarkdown.files[0], 'markdown');
        } else {
            alert(getTranslatedText('select-file-alert', '请先选择文件'));
        }
    });
    
    // 复制响应按钮
    copyResponseBtn.addEventListener('click', function() {
        if (!currentResponseData) return;
        
        let textToCopy;
        
        // 如果是预览模式下，复制markdown原文
        if (apiMdControls.style.display !== 'none' && 
            apiMdPreview.style.display !== 'none') {
            textToCopy = originalMarkdown;
        } else {
            textToCopy = currentResponseData.text;
        }
        
        copyToClipboard(textToCopy);
    });
    
    // 下载响应按钮
    downloadResponseBtn.addEventListener('click', function() {
        if (!currentResponseData) return;
        
        let textToDownload = currentResponseData.text;
        const extension = currentApiTestTab === 'markdown' ? '.md' : '.txt';
        const filename = `${currentResponseData.filename || 'conversion-result'}${extension}`;
        
        downloadText(textToDownload, filename);
    });
    
    // Markdown预览切换
    const viewButtons = document.querySelectorAll('.api-md-controls .view-btn');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            viewButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            if (view === 'raw') {
                apiTestResponseContent.style.display = 'block';
                apiMdPreview.style.display = 'none';
            } else {
                apiTestResponseContent.style.display = 'none';
                apiMdPreview.style.display = 'block';
                renderMarkdown(originalMarkdown);
            }
        });
    });
    
    // 处理API测试
    function handleApiTest(file, type) {
        const fileExt = file.name.split('.').pop().toLowerCase();
        let supportedTypes;
        
        if (type === 'text') {
            supportedTypes = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'txt', 'md'];
        } else { // markdown
            supportedTypes = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'txt', 'md', 'mp3', 'wav'];
        }
        
        if (!supportedTypes.includes(fileExt)) {
            alert(getTranslatedText('file-type-not-supported', `不支持的文件类型: ${fileExt}！请上传支持的文件格式。`));
            return;
        }
        
        // 检查文件大小
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            alert(getTranslatedText('file-too-large', `文件过大！最大支持50MB，当前文件大小: ${(file.size / (1024 * 1024)).toFixed(2)}MB`));
            return;
        }
        
        // 显示加载指示器
        apiTestDropAreaText.style.display = 'none';
        apiTestDropAreaMarkdown.style.display = 'none';
        apiTestLoadingIndicator.style.display = 'block';
        apiTestResponseContainer.style.display = 'none';
        apiMdControls.style.display = 'none';
        apiMdPreview.style.display = 'none';
        
        // 开始时间
        const startTime = Date.now();
        
        // 创建FormData对象
        const formData = new FormData();
        formData.append('file', file);
        
        // 确定API端点
        const endpoint = type === 'text' ? '/api/convert' : '/api/convert-to-md';
        
        // 发送文件到服务器
        fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            // 显示响应
            apiTestLoadingIndicator.style.display = 'none';
            apiTestResponseContainer.style.display = 'block';
            
            if (!response.ok) {
                return response.json().then(data => {
                    showErrorResponse(data, file, response.status);
                    throw new Error(data.error || getTranslatedText('conversion-failed', '转换失败'));
                });
            }
            return response.json().then(data => showSuccessResponse(data, file, startTime, type));
        })
        .catch(error => {
            console.error('API测试错误:', error);
            
            // 隐藏加载指示器
            apiTestLoadingIndicator.style.display = 'none';
            
            // 显示错误响应
            apiTestResponseContainer.style.display = 'block';
            apiTestResponseContainer.classList.add('error');
            apiTestResponseTitle.textContent = getTranslatedText('api-response-error', 'API响应: 错误');
            apiTestResponseTitle.style.color = '#e74c3c';
            apiTestResponseStats.textContent = '';
            apiTestResponseContent.textContent = `${getTranslatedText('request-failed', '请求失败')}: ${error.message}`;
        });
    }
    
    // 显示成功响应
    function showSuccessResponse(data, file, startTime, type) {
        // 保存响应数据
        currentResponseData = data;
        
        // 计算请求时间
        const requestTime = ((Date.now() - startTime) / 1000).toFixed(2);
        
        // 设置响应类型
        apiTestResponseContainer.classList.remove('error');
        apiTestResponseContainer.classList.add('success');
        
        // 设置响应标题
        apiTestResponseTitle.textContent = getTranslatedText('api-response-success', 'API响应: 成功');
        apiTestResponseTitle.style.color = '#2ecc71';
        
        // 显示统计信息
        const stats = [
            `${getTranslatedText('filename', '文件名')}: ${file.name}`,
            `${getTranslatedText('file-size', '文件大小')}: ${(file.size / 1024).toFixed(2)} KB`,
            `${getTranslatedText('processing-time', '处理时间')}: ${data.processing_time || requestTime}${getTranslatedText('seconds', '秒')}`,
            `${getTranslatedText('text-length', '文本长度')}: ${data.text.length} ${getTranslatedText('characters', '字符')}`
        ];
        apiTestResponseStats.textContent = stats.join(' | ');
        
        // 显示部分转换结果
        apiTestResponseContent.textContent = data.text;
        
        // 如果是Markdown类型，启用预览功能
        if (type === 'markdown') {
            originalMarkdown = data.text;
            apiMdControls.style.display = 'flex';
            // 默认显示源码视图
            document.querySelector('.api-md-controls .view-btn[data-view="raw"]').classList.add('active');
            document.querySelector('.api-md-controls .view-btn[data-view="preview"]').classList.remove('active');
            apiTestResponseContent.style.display = 'block';
            apiMdPreview.style.display = 'none';
        } else {
            apiMdControls.style.display = 'none';
            apiMdPreview.style.display = 'none';
        }
    }
    
    // 显示错误响应
    function showErrorResponse(data, file, status) {
        apiTestResponseContainer.classList.remove('success');
        apiTestResponseContainer.classList.add('error');
        apiTestResponseTitle.textContent = `${getTranslatedText('api-response-error', 'API响应: 错误')} (${status})`;
        apiTestResponseTitle.style.color = '#e74c3c';
        
        const stats = [
            `${getTranslatedText('filename', '文件名')}: ${file.name}`,
            `${getTranslatedText('file-size', '文件大小')}: ${(file.size / 1024).toFixed(2)} KB`
        ];
        apiTestResponseStats.textContent = stats.join(' | ');
        
        apiTestResponseContent.textContent = JSON.stringify(data, null, 2);
    }
    
    // 复制到剪贴板
    function copyToClipboard(text) {
        // 创建一个临时的文本区域来复制
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';  // 避免滚动
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            
            if (successful) {
                // 显示复制成功提示
                const originalText = copyResponseBtn.textContent;
                copyResponseBtn.textContent = getTranslatedText('copied', '已复制!');
                copyResponseBtn.disabled = true;
                
                setTimeout(() => {
                    copyResponseBtn.textContent = originalText;
                    copyResponseBtn.disabled = false;
                }, 2000);
            } else {
                throw new Error(getTranslatedText('copy-failed', '复制失败'));
            }
        } catch (err) {
            console.error('复制失败: ', err);
            
            // 尝试使用新API
            navigator.clipboard.writeText(text)
                .then(() => {
                    // 显示复制成功提示
                    const originalText = copyResponseBtn.textContent;
                    copyResponseBtn.textContent = getTranslatedText('copied', '已复制!');
                    copyResponseBtn.disabled = true;
                    
                    setTimeout(() => {
                        copyResponseBtn.textContent = originalText;
                        copyResponseBtn.disabled = false;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Clipboard API失败: ', err);
                    alert(getTranslatedText('copy-failed-manual', '复制失败，请手动选择文本并复制'));
                });
        } finally {
            document.body.removeChild(textArea);
        }
    }
    
    // 下载文本
    function downloadText(text, filename) {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // 显示下载成功提示
        const originalText = downloadResponseBtn.textContent;
        downloadResponseBtn.textContent = getTranslatedText('downloaded', '已下载!');
        downloadResponseBtn.disabled = true;
        
        setTimeout(() => {
            downloadResponseBtn.textContent = originalText;
            downloadResponseBtn.disabled = false;
        }, 2000);
    }
    
    // 渲染Markdown预览
    function renderMarkdown(markdown) {
        if (!markdown) return;
        
        try {
            // 使用marked库渲染Markdown
            if (typeof marked !== 'undefined') {
                apiMdPreview.innerHTML = marked.parse(markdown);
                
                // 添加图片点击事件
                const images = apiMdPreview.querySelectorAll('img.md-image');
                images.forEach(img => {
                    img.addEventListener('click', function() {
                        this.classList.toggle('md-image-fullscreen');
                    });
                });
                
                // 代码高亮
                if (typeof hljs !== 'undefined') {
                    apiMdPreview.querySelectorAll('pre code').forEach(block => {
                        hljs.highlightElement(block);
                    });
                }
                
                return;
            }
        } catch (error) {
            console.error('使用marked.js渲染Markdown出错:', error);
            // 如果marked库不可用或出错，回退到原始渲染方法
        }
        
        // 以下是原始渲染逻辑，作为备选方案
        
        // 预处理表格数据
        let processedMarkdown = markdown;
        const tableRegex = /(\|.+\|\r?\n)((?:\|[-:]+[-| :]*\|\r?\n))((?:\|.+\|\r?\n)+)/g;
        
        processedMarkdown = processedMarkdown.replace(tableRegex, function(match, headerRow, separatorRow, bodyRows) {
            // 处理表头
            const headers = headerRow.trim().split('|').filter(col => col.trim() !== '').map(col => col.trim());
            let tableHTML = '<table class="md-table"><thead><tr>';
            headers.forEach(header => {
                tableHTML += `<th>${header}</th>`;
            });
            tableHTML += '</tr></thead><tbody>';
            
            // 处理表格内容
            const rows = bodyRows.trim().split('\n');
            rows.forEach(row => {
                if (row.trim() !== '') {
                    const cells = row.trim().split('|').filter(col => col.trim() !== '').map(col => col.trim());
                    tableHTML += '<tr>';
                    cells.forEach(cell => {
                        tableHTML += `<td>${cell}</td>`;
                    });
                    tableHTML += '</tr>';
                }
            });
            
            tableHTML += '</tbody></table>';
            return tableHTML;
        });
        
        // 处理图片
        processedMarkdown = processedMarkdown.replace(/!\[(.*?)\]\((.*?)\)/gim, '<img src="$2" alt="$1" title="$1" class="md-image">');
        
        // 使用增强的正则表达式替换Markdown语法
        let html = processedMarkdown
            // 处理标题
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // 处理加粗
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            // 处理斜体
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            // 处理链接
            .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank">$1</a>')
            // 处理无序列表项
            .replace(/^\- (.*$)/gim, '<li>$1</li>')
            .replace(/^\* (.*$)/gim, '<li>$1</li>')
            // 处理有序列表项
            .replace(/^(\d+)\. (.*$)/gim, '<li>$2</li>')
            // 处理代码块
            .replace(/```([\s\S]*?)```/gm, '<pre><code class="md-code-block">$1</code></pre>')
            // 处理行内代码
            .replace(/`(.*?)`/gim, '<code>$1</code>')
            // 处理水平线
            .replace(/^\-\-\-/gim, '<hr>')
            // 处理引用
            .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
            // 处理换行(保留已有的<br>标签)
            .replace(/(?<!\<br\>)\n/gim, '<br>');
        
        // 把列表项包裹在ul/ol中
        let inList = false;
        let listType = '';
        let listHtml = '';
        const lines = html.split('<br>');
        
        html = '';
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            if (line.startsWith('<li>')) {
                if (!inList) {
                    inList = true;
                    listType = 'ul';
                    listHtml = '<ul>' + line;
                } else {
                    listHtml += line;
                }
            } else {
                if (inList) {
                    inList = false;
                    listHtml += '</ul>';
                    html += listHtml + '<br>' + line;
                    listHtml = '';
                } else {
                    html += (i > 0 ? '<br>' : '') + line;
                }
            }
        }
        
        // 处理列表结束
        if (inList) {
            html += listHtml + '</ul>';
        }
        
        // 替换连续的blockquote标签
        html = html.replace(/<\/blockquote><br><blockquote>/g, '<br>');
        
        apiMdPreview.innerHTML = html;
        
        // 添加图片点击处理
        const images = apiMdPreview.querySelectorAll('.md-image');
        images.forEach(img => {
            img.addEventListener('click', function() {
                this.classList.toggle('md-image-fullscreen');
            });
        });
    }
    
    // 获取翻译文本（如果i18n可用）
    function getTranslatedText(key, fallback) {
        // 检查是否有窗口级的翻译函数 
        if (window.translations && window.currentLang) {
            const translations = window.translations[window.currentLang];
            if (translations && translations[key]) {
                return translations[key];
            }
        }
        
        // 否则使用后备文本
        return fallback;
    }
    
    // 扩展i18n.js中的语言数据
    if (window.translations) {
        // 中文
        if (window.translations.zh) {
            Object.assign(window.translations.zh, {
                // API文档页面
                'api-doc-title': '文档转换工具 - API文档',
                'api-doc-subtitle': 'REST API接口使用说明',
                'back-to-home': '返回首页',
                'api-docs-anchor': 'API文档',
                'api-docs-heading': 'API文档',
                'api-docs-intro': '本工具提供了REST API接口，可以通过程序调用实现文档转换功能。',
                'api-tab-text': '转为文本API',
                'api-tab-markdown': '转为Markdown API',
                'text-api-title': '文档转文本API',
                'md-api-title': '文档转Markdown API',
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
                'downloaded': '已下载!'
            });
        }
        
        // 英文
        if (window.translations.en) {
            Object.assign(window.translations.en, {
                // API Documentation Page
                'api-doc-title': 'Document Conversion Tool - API Documentation',
                'api-doc-subtitle': 'REST API Interface Guide and Online Testing',
                'back-to-home': 'Back to Home',
                'api-docs-anchor': 'API Documentation',
                'api-test-anchor': 'Online Testing',
                'api-docs-heading': 'API Documentation',
                'api-docs-intro': 'This tool provides REST API interfaces for programmatic document conversion.',
                'api-tab-text': 'Convert to Text API',
                'api-tab-markdown': 'Convert to Markdown API',
                'text-api-title': 'Document to Text API',
                'md-api-title': 'Document to Markdown API',
                'content-type': 'Content Type: multipart/form-data',
                'request-params': 'Request Parameters',
                'param-name': 'Parameter',
                'param-type': 'Type',
                'param-required': 'Required',
                'param-desc': 'Description',
                'file-type': 'File',
                'yes': 'Yes',
                'file-desc': 'Document file to convert',
                'supported-file-types': 'Supported File Types',
                'response-format': 'Response Format',
                'success-response': 'Success Response (HTTP 200):',
                'error-response': 'Error Response (HTTP 4xx/5xx):',
                'audio-files': 'Audio Files (.mp3, .wav)',
                'new-tag': 'NEW',
                'md-features': 'Features',
                'md-features-intro': 'Unlike plain text conversion, Markdown conversion preserves more of the original document structure:',
                'code-examples': 'Code Examples',
                'python-text-example': 'Python Example - Convert to Text',
                'python-md-example': 'Python Example - Convert to Markdown',
                
                // API Testing Page
                'api-test-title': 'API Online Testing',
                'api-test-intro': 'You can test the API functionality here by uploading a file and viewing the conversion results.',
                'test-tab-text': 'Convert to Text',
                'test-tab-markdown': 'Convert to Markdown',
                'test-select-file': 'Select File',
                'test-convert': 'Convert',
                'api-response': 'API Response',
                'api-response-success': 'API Response: Success',
                'api-response-error': 'API Response: Error',
                'copy-response': 'Copy Response',
                'download-response': 'Download Result',
                'view-raw': 'View Source',
                'view-preview': 'Preview',
                
                // Notifications and Errors
                'select-file-alert': 'Please select a file first',
                'file-type-not-supported': 'File type not supported! Please upload a supported file format.',
                'file-too-large': 'File too large! Maximum size is 50MB',
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
                'copy-failed-manual': 'Copy failed, please manually select and copy the text',
                'downloaded': 'Downloaded!'
            });
        }
    }
}); 