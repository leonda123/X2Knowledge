document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const dropAreaText = document.getElementById('dropAreaText');
    const dropAreaMarkdown = document.getElementById('dropAreaMarkdown');
    const dropAreaEmbedding = document.getElementById('dropAreaEmbedding'); // 新增Embedding拖放区域
    const fileInputText = document.getElementById('fileInputText');
    const fileInputMarkdown = document.getElementById('fileInputMarkdown');
    const fileInputEmbedding = document.getElementById('fileInputEmbedding'); // 新增Embedding文件输入
    const resultContainer = document.getElementById('resultContainer');
    const resultText = document.getElementById('resultText');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const newConvertBtn = document.getElementById('newConvertBtn');
    const fullscreenBtn = document.getElementById('fullscreenBtn'); // 全屏按钮
    
    // URL转Markdown元素
    const urlInput = document.getElementById('urlInput');
    const removeHeaderFooter = document.getElementById('removeHeaderFooter');
    const urlSelector = document.getElementById('urlSelector');
    const convertUrlBtn = document.getElementById('convertUrlBtn');
    
    // Tab切换功能
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 移除所有active类
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 添加active类到当前tab
            this.classList.add('active');
            const tabId = `tab-${this.dataset.tab}`;
            document.getElementById(tabId).classList.add('active');
            
            // 更新activeTab变量，以跟踪当前活动的标签页
            activeTab = this.dataset.tab;
            
            // 如果结果容器隐藏（正在上传状态），则显示对应的上传区域
            if (resultContainer.style.display === 'none' && loadingIndicator.style.display === 'none') {
                if (activeTab === 'text') {
                    dropAreaText.style.display = 'block';
                    dropAreaMarkdown.style.display = 'none';
                    document.querySelector('#tab-url').style.display = 'none';
                    document.querySelector('#tab-embedding').style.display = 'none';
                } else if (activeTab === 'markdown') {
                    dropAreaText.style.display = 'none';
                    dropAreaMarkdown.style.display = 'block';
                    document.querySelector('#tab-url').style.display = 'none';
                    document.querySelector('#tab-embedding').style.display = 'none';
                } else if (activeTab === 'url') {
                    dropAreaText.style.display = 'none';
                    dropAreaMarkdown.style.display = 'none';
                    document.querySelector('#tab-url').style.display = 'block';
                    document.querySelector('#tab-embedding').style.display = 'none';
                } else if (activeTab === 'embedding') {
                    dropAreaText.style.display = 'none';
                    dropAreaMarkdown.style.display = 'none';
                    document.querySelector('#tab-url').style.display = 'none';
                    document.querySelector('#tab-embedding').style.display = 'block';
                }
            }
        });
    });
    
    // API文档页面的Tab切换
    const apiTabButtons = document.querySelectorAll('.api-tab-button');
    const apiTabContents = document.querySelectorAll('.api-tab-content');
    
    if (apiTabButtons.length > 0 && apiTabContents.length > 0) {
        apiTabButtons.forEach(button => {
            button.addEventListener('click', function() {
                // 移除所有active类
                apiTabButtons.forEach(btn => btn.classList.remove('active'));
                apiTabContents.forEach(content => content.classList.remove('active'));
                
                // 添加active类到当前tab
                this.classList.add('active');
                const tabId = this.dataset.tab;
                document.getElementById(tabId).classList.add('active');
            });
        });
    }
    
    let currentFileName = '';
    let conversionStartTime = 0;
    let activeTab = 'markdown'; // 默认为Markdown转换
    let originalMarkdown = ''; // 保存原始的Markdown文本
    
    // 创建错误提示元素
    const errorContainer = document.createElement('div');
    errorContainer.className = 'error-container';
    errorContainer.style.display = 'none';
    errorContainer.innerHTML = `
        <div class="error-content">
            <h3>转换出错</h3>
            <p id="errorMessage"></p>
            <button id="dismissErrorBtn" class="btn">关闭</button>
        </div>
    `;
    document.querySelector('.container').appendChild(errorContainer);
    
    const errorMessage = document.getElementById('errorMessage');
    const dismissErrorBtn = document.getElementById('dismissErrorBtn');
    
    dismissErrorBtn.addEventListener('click', function() {
        errorContainer.style.display = 'none';
    });
    
    // 创建Markdown切换控件
    const markdownViewControls = document.createElement('div');
    markdownViewControls.className = 'markdown-view-controls';
    markdownViewControls.style.display = 'none';
    markdownViewControls.innerHTML = `
        <button class="view-btn active" data-view="raw" data-i18n="source-view">源码视图</button>
        <button class="view-btn" data-view="preview" data-i18n="preview-view">预览视图</button>
    `;
    
    // 创建Markdown预览元素
    const markdownPreview = document.createElement('div');
    markdownPreview.className = 'markdown-preview';
    markdownPreview.style.display = 'none';
    
    // 将这些元素添加到结果容器中
    const resultContent = document.querySelector('.result-content');
    resultContent.parentNode.insertBefore(markdownViewControls, resultContent);
    resultContent.parentNode.appendChild(markdownPreview);
    
    // 添加Markdown视图切换事件
    const viewButtons = markdownViewControls.querySelectorAll('.view-btn');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            viewButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            if (view === 'raw') {
                resultContent.style.display = 'block';
                markdownPreview.style.display = 'none';
                fullscreenBtn.style.display = 'none'; // 隐藏全屏按钮
            } else {
                resultContent.style.display = 'none';
                markdownPreview.style.display = 'block';
                fullscreenBtn.style.display = 'inline-block'; // 显示全屏按钮
                renderMarkdown(originalMarkdown);
            }
        });
    });
    
    // 渲染Markdown函数
    function renderMarkdown(markdown) {
        if (!markdown) return;
        
        try {
            // 使用marked库渲染Markdown
            if (typeof marked !== 'undefined') {
                markdownPreview.innerHTML = marked.parse(markdown);
                
                // 添加图片点击事件
                const images = markdownPreview.querySelectorAll('img.md-image');
                images.forEach(img => {
                    img.addEventListener('click', function() {
                        this.classList.toggle('md-image-fullscreen');
                    });
                });
                
                // 代码高亮
                if (typeof hljs !== 'undefined') {
                    markdownPreview.querySelectorAll('pre code').forEach(block => {
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
            .replace(/```([\s\S]*?)```/gm, '<pre><code>$1</code></pre>')
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
        
        markdownPreview.innerHTML = html;
        
        // 添加图片点击处理
        const images = markdownPreview.querySelectorAll('.md-image');
        images.forEach(img => {
            img.addEventListener('click', function() {
                this.classList.toggle('md-image-fullscreen');
            });
        });
    }
    
    // 显示错误信息
    function showError(message) {
        errorMessage.textContent = message;
        errorContainer.style.display = 'block';
        loadingIndicator.style.display = 'none';
        
        // 根据当前活动tab显示对应的上传区域
        if (activeTab === 'text') {
            dropAreaText.style.display = 'block';
            dropAreaMarkdown.style.display = 'none';
            document.querySelector('#tab-url').style.display = 'none';
            document.querySelector('#tab-embedding').style.display = 'none';
        } else if (activeTab === 'markdown') {
            dropAreaText.style.display = 'none';
            dropAreaMarkdown.style.display = 'block';
            document.querySelector('#tab-url').style.display = 'none';
            document.querySelector('#tab-embedding').style.display = 'none';
        } else if (activeTab === 'url') {
            dropAreaText.style.display = 'none';
            dropAreaMarkdown.style.display = 'none';
            document.querySelector('#tab-url').style.display = 'block';
            document.querySelector('#tab-embedding').style.display = 'none';
        } else if (activeTab === 'embedding') {
            dropAreaText.style.display = 'none';
            dropAreaMarkdown.style.display = 'none';
            document.querySelector('#tab-url').style.display = 'none';
            document.querySelector('#tab-embedding').style.display = 'block';
        }
    }
    
    // 拖拽事件处理 - 文本转换
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropAreaText.addEventListener(eventName, preventDefaults, false);
    });
    
    // 拖拽事件处理 - Markdown转换
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropAreaMarkdown.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropAreaText.addEventListener(eventName, () => highlight(dropAreaText), false);
        dropAreaMarkdown.addEventListener(eventName, () => highlight(dropAreaMarkdown), false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropAreaText.addEventListener(eventName, () => unhighlight(dropAreaText), false);
        dropAreaMarkdown.addEventListener(eventName, () => unhighlight(dropAreaMarkdown), false);
    });
    
    function highlight(element) {
        element.classList.add('dragover');
    }
    
    function unhighlight(element) {
        element.classList.remove('dragover');
    }
    
    // 处理拖放文件
    dropAreaText.addEventListener('drop', function(e) {
        activeTab = 'text';
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFiles(files[0], 'text');
        }
    }, false);
    
    dropAreaMarkdown.addEventListener('drop', function(e) {
        activeTab = 'markdown';
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFiles(files[0], 'markdown');
        }
    }, false);
    
    // 处理文件选择
    fileInputText.addEventListener('change', function() {
        activeTab = 'text';
        if (this.files.length > 0) {
            handleFiles(this.files[0], 'text');
        }
    });
    
    fileInputMarkdown.addEventListener('change', function() {
        activeTab = 'markdown';
        if (this.files.length > 0) {
            handleFiles(this.files[0], 'markdown');
        }
    });
    
    // 添加转换器选择变化的事件处理
    const markitdownConverter = document.getElementById('markitdown-converter');
    const doclingConverter = document.getElementById('docling-converter');
    const doclingImagesConverter = document.getElementById('docling-images-converter');
    const supportedFileTypes = document.getElementById('supportedFileTypes');
    
    if (markitdownConverter && doclingConverter && doclingImagesConverter) {
        // 初始更新文件类型信息
        updateSupportedFormats();
        
        // 添加转换器切换事件
        markitdownConverter.addEventListener('change', updateSupportedFormats);
        doclingConverter.addEventListener('change', updateSupportedFormats);
        doclingImagesConverter.addEventListener('change', updateSupportedFormats);
    }
    
    // 更新支持的文件格式显示
    function updateSupportedFormats() {
        if (!supportedFileTypes) return;
        
        // 根据当前选择的转换器更新显示的支持格式
        const isDocling = doclingConverter && doclingConverter.checked;
        const isDoclingImages = doclingImagesConverter && doclingImagesConverter.checked;
        
        let formatKey = 'markitdown-supported-formats';
        if (isDocling) {
            formatKey = 'docling-supported-formats';
        } else if (isDoclingImages) {
            formatKey = 'docling-images-supported-formats';
        }
        
        const formatText = getTranslatedText('supported-types-md') || '支持的文件类型:';
        
        // 获取对应的格式列表
        const formats = getTranslatedText(formatKey);
        supportedFileTypes.textContent = `${formatText.split(':')[0]}: ${formats}`;
        
        // 同时更新文件输入的accept属性
        if (fileInputMarkdown) {
            // 提取格式列表，转换为accept属性所需的格式
            const acceptFormats = formats.split(',').map(fmt => fmt.trim()).join(',');
            fileInputMarkdown.setAttribute('accept', acceptFormats);
        }
    }
    
    // 处理文件上传和转换
    function handleFiles(file, type) {
        // 重置错误状态
        errorContainer.style.display = 'none';
        
        currentFileName = file.name.split('.')[0]; // 保存文件名（不含扩展名）
        
        // 显示加载指示器
        loadingIndicator.style.display = 'block';
        
        // 隐藏上传区域
        dropAreaText.style.display = 'none';
        dropAreaMarkdown.style.display = 'none';
        
        // 清空预览区域
        if (type === 'text') {
            resultText.textContent = '';
        } else {
            markdownPreview.innerHTML = '';
            markdownPreview.style.display = 'none';
        }
        
        // 创建FormData对象
        const formData = new FormData();
        formData.append('file', file);
        
        // 确定API端点
        let apiEndpoint = '';
        
        if (type === 'text') {
            apiEndpoint = '/convert';  // 使用现有文本转换路径
        } else {
            // 根据选择的转换器确定API端点
            const isDoclingSelected = doclingConverter && doclingConverter.checked;
            const isDoclingImagesSelected = doclingImagesConverter && doclingImagesConverter.checked;
            
            if (isDoclingImagesSelected) {
                apiEndpoint = '/convert-to-md-images-file-docling';  // 新增带图片的Docling路径
            } else if (isDoclingSelected) {
                apiEndpoint = '/convert-to-md-docling';  // 使用现有docling路径
            } else {
                apiEndpoint = '/convert-to-md';          // 使用现有markitdown路径
            }
        }
        
        // 记录开始时间
        conversionStartTime = Date.now();
        
        // 发送文件到服务器
        fetch(apiEndpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || '转换失败');
                });
            }
            return response.json();
        })
        .then(data => {
            // 计算转换时间
            const conversionTime = ((Date.now() - conversionStartTime) / 1000).toFixed(2);
            
            // 取得文本内容 - 兼容旧接口和新接口
            let textContent = '';
            if (data.text) {
                textContent = data.text;
            } else if (data.markdown) {
                textContent = data.markdown;
            } else if (typeof data === 'string') {
                textContent = data;
            }
            
            // 显示转换结果
            resultText.textContent = textContent;
            loadingIndicator.style.display = 'none';
            resultContainer.style.display = 'block';
            
            // 添加转换信息
            const resultHeader = document.querySelector('.result-header h2');
            let resultType = type === 'text' ? '文本' : 'Markdown';
            
            // 添加使用的转换器信息（如果是Markdown）
            if (type === 'markdown') {
                const useDocling = doclingConverter && doclingConverter.checked;
                const useDoclingImages = doclingImagesConverter && doclingImagesConverter.checked;
                
                if (useDocling) {
                    resultType += ' (使用Docling)';
                } else if (useDoclingImages) {
                    resultType += ' (使用带图片的Docling)';
                } else {
                    resultType += ' (使用MarkItDown)';
                }
            }
            
            resultHeader.textContent = `转换结果 (${resultType}, 用时: ${conversionTime}秒, 字符数: ${textContent.length})`;
            
            // 如果文本为空，显示提示
            if (!textContent || textContent.trim() === '') {
                resultText.textContent = '[文件中未找到内容]';
            }
            
            // 如果是Markdown类型，显示Markdown视图控件并保存原始Markdown
            if (type === 'markdown') {
                originalMarkdown = textContent;
                markdownViewControls.style.display = 'flex';
                // 默认显示源码视图
                viewButtons[0].click();
            }
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            
            console.error('转换错误:', error);
            showError(`转换失败: ${error.message}`);
        });
    }
    
    // 复制文本按钮
    copyBtn.addEventListener('click', function() {
        // 获取当前视图下的文本
        let text;
        if (markdownViewControls.style.display !== 'none' && 
            markdownPreview.style.display !== 'none') {
            // 如果在预览模式下，复制原始Markdown
            text = originalMarkdown;
        } else {
            text = resultText.textContent;
        }
        
        if (!text || text.trim() === '') {
            showError('没有可复制的文本内容');
            return;
        }
        
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
                const originalText = copyBtn.textContent;
                copyBtn.textContent = '已复制!';
                copyBtn.disabled = true;
                
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                    copyBtn.disabled = false;
                }, 2000);
            } else {
                throw new Error('复制失败');
            }
        } catch (err) {
            console.error('复制失败: ', err);
            
            // 尝试使用新API
            navigator.clipboard.writeText(text)
                .then(() => {
                    // 显示复制成功提示
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = '已复制!';
                    copyBtn.disabled = true;
                    
                    setTimeout(() => {
                        copyBtn.textContent = originalText;
                        copyBtn.disabled = false;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Clipboard API失败: ', err);
                    showError('复制失败，请手动选择文本并复制');
                });
        } finally {
            document.body.removeChild(textArea);
        }
    });
    
    // 下载文本按钮
    downloadBtn.addEventListener('click', function() {
        // 获取当前视图下的文本
        let text;
        if (markdownViewControls.style.display !== 'none') {
            // 如果是Markdown模式，使用原始Markdown
            text = originalMarkdown;
        } else {
            text = resultText.textContent;
        }
        
        if (!text || text.trim() === '') {
            showError('没有可下载的文本内容');
            return;
        }
        
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // 根据当前活动的Tab决定下载的文件扩展名
        const extension = activeTab === 'markdown' ? '.md' : '.txt';
        a.download = `${currentFileName || 'converted'}${extension}`;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // 显示下载成功提示
        const originalText = downloadBtn.textContent;
        downloadBtn.textContent = '已下载!';
        downloadBtn.disabled = true;
        
        setTimeout(() => {
            downloadBtn.textContent = originalText;
            downloadBtn.disabled = false;
        }, 2000);
    });
    
    // 新的转换按钮
    newConvertBtn.addEventListener('click', function() {
        // 刷新页面
        window.location.reload();
    });

    // 添加URL转换事件监听
    if (convertUrlBtn) {
        convertUrlBtn.addEventListener('click', function() {
            // 获取URL和选项
            const url = urlInput.value.trim();
            const shouldRemoveHeaderFooter = removeHeaderFooter.checked;
            const selector = urlSelector ? urlSelector.value.trim() : '';
            
            // 验证URL
            if (!url) {
                showError('请输入有效的URL');
                return;
            }
            
            // 显示加载指示器
            loadingIndicator.style.display = 'block';
            
            // 隐藏URL输入区域
            const urlInputContainer = document.querySelector('.url-input-container');
            if (urlInputContainer) {
                urlInputContainer.style.display = 'none';
            }
            
            // 记录开始时间
            conversionStartTime = Date.now();
            
            // 创建FormData对象
            const formData = new FormData();
            formData.append('url', url);
            formData.append('remove_header_footer', shouldRemoveHeaderFooter);
            if (selector) {
                formData.append('selector', selector);
            }
            
            // 发送请求到API
            fetch('/api/convert-url-to-md', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'URL转换失败');
                    });
                }
                return response.json();
            })
            .then(data => {
                // 计算转换时间
                const conversionTime = ((Date.now() - conversionStartTime) / 1000).toFixed(2);
                
                // 获取Markdown内容
                const markdown = data.text || '';
                
                // 显示转换结果
                resultText.textContent = markdown;
                loadingIndicator.style.display = 'none';
                resultContainer.style.display = 'block';
                
                // 添加转换信息
                const resultHeader = document.querySelector('.result-header h2');
                resultHeader.textContent = `转换结果 (URL转Markdown, 用时: ${conversionTime}秒, 字符数: ${markdown.length})`;
                
                // 如果文本为空，显示提示
                if (!markdown || markdown.trim() === '') {
                    resultText.textContent = '[URL中未找到内容]';
                }
                
                // 保存原始Markdown并显示视图控件
                originalMarkdown = markdown;
                markdownViewControls.style.display = 'flex';
                
                // 默认显示预览视图
                const previewButton = document.querySelector('.view-btn[data-view="preview"]');
                if (previewButton) {
                    previewButton.click();
                }
                
                // 设置文件名为URL的域名部分（用于下载）
                try {
                    const urlObj = new URL(url);
                    currentFileName = urlObj.hostname.replace(/\./g, '_');
                } catch (e) {
                    currentFileName = 'url_content';
                }
            })
            .catch(error => {
                loadingIndicator.style.display = 'none';
                
                // 显示错误并恢复URL输入区域
                if (urlInputContainer) {
                    urlInputContainer.style.display = 'block';
                }
                
                console.error('URL转换错误:', error);
                showError(`URL转换失败: ${error.message}`);
            });
        });
    }
    
    // 添加Enter键触发URL转换
    if (urlInput) {
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                convertUrlBtn.click();
            }
        });
    }

    // 模态框相关
    // Swagger模态框
    const swaggerBtn = document.getElementById('swagger-btn');
    const swaggerModal = document.getElementById('swagger-modal');
    const closeSwaggerBtn = document.getElementById('close-swagger-modal');
    
    // CSS选择器帮助模态框
    const selectorHelpBtn = document.getElementById('selectorHelpBtn');
    const selectorHelpModal = document.getElementById('selectorHelpModal');
    const closeSelectorHelpBtn = document.getElementById('closeSelectorHelpBtn');
    const selectorTabs = document.querySelectorAll('.selector-tab');
    const selectorTabContents = document.querySelectorAll('.selector-tab-content');
    
    // 打开Swagger模态框
    swaggerBtn.addEventListener('click', function(e) {
        e.preventDefault();
        swaggerModal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // 防止背景滚动
    });
    
    // 关闭Swagger模态框
    closeSwaggerBtn.addEventListener('click', function() {
        swaggerModal.style.display = 'none';
        document.body.style.overflow = 'auto'; // 恢复背景滚动
    });
    
    // 点击模态框背景关闭模态框
    swaggerModal.addEventListener('click', function(e) {
        if (e.target === swaggerModal) {
            swaggerModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
    
    // 选择器帮助模态框事件
    if (selectorHelpBtn && selectorHelpModal) {
        // 打开选择器帮助模态框
        selectorHelpBtn.addEventListener('click', function() {
            selectorHelpModal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        });
        
        // 关闭选择器帮助模态框
        closeSelectorHelpBtn.addEventListener('click', function() {
            selectorHelpModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
        
        // 点击模态框背景关闭模态框
        selectorHelpModal.addEventListener('click', function(e) {
            if (e.target === selectorHelpModal) {
                selectorHelpModal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
        
        // 选择器教程标签页切换
        selectorTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // 移除所有标签页的active类
                selectorTabs.forEach(t => t.classList.remove('active'));
                // 添加当前标签页的active类
                this.classList.add('active');
                
                // 获取当前标签页对应的内容
                const tabId = this.getAttribute('data-tab');
                
                // 隐藏所有内容
                selectorTabContents.forEach(content => {
                    content.classList.remove('active');
                });
                
                // 显示当前内容
                document.getElementById(tabId + '-selectors').classList.add('active');
            });
        });
    }

    // Embedding预处理文件拖放功能
    if (dropAreaEmbedding) {
        // 阻止默认行为
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropAreaEmbedding.addEventListener(eventName, preventDefaults, false);
        });
        
        // 拖拽高亮
        ['dragenter', 'dragover'].forEach(eventName => {
            dropAreaEmbedding.addEventListener(eventName, function() {
                highlight(dropAreaEmbedding);
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropAreaEmbedding.addEventListener(eventName, function() {
                unhighlight(dropAreaEmbedding);
            }, false);
        });
        
        // 处理文件拖放
        dropAreaEmbedding.addEventListener('drop', function(e) {
            let dt = e.dataTransfer;
            let file = dt.files[0];
            
            if (file && file.name.toLowerCase().endsWith('.md')) {
                handleEmbeddingFile(file);
            } else {
                showError('请上传Markdown (.md) 文件');
            }
        }, false);
        
        // 处理文件选择
        fileInputEmbedding.addEventListener('change', function() {
            if (this.files.length) {
                let file = this.files[0];
                if (file.name.toLowerCase().endsWith('.md')) {
                    handleEmbeddingFile(file);
                } else {
                    showError('请上传Markdown (.md) 文件');
                }
            }
        });
    }
    
    // 处理Embedding预处理按钮点击
    if (processEmbeddingBtn) {
        processEmbeddingBtn.addEventListener('click', function() {
            processEmbeddingData();
        });
    }
    
    // 处理Embedding文件
    function handleEmbeddingFile(file) {
        // 显示加载指示器
        tabContents.forEach(content => content.style.display = 'none');
        loadingIndicator.style.display = 'flex';
        
        // 清除文本区域内容
        embeddingTextarea.value = '';
        
        // 设置默认文件名为文件名（不含扩展名）
        const fileName = file.name.replace(/\.[^/.]+$/, "");
        outputFilename.value = fileName;
        
        // 读取文件内容
        const reader = new FileReader();
        reader.onload = function(e) {
            // 将文件内容填充到文本区域
            embeddingTextarea.value = e.target.result;
            
            // 隐藏加载指示器并显示预处理表单
            loadingIndicator.style.display = 'none';
            document.getElementById('tab-embedding').style.display = 'block';
            
            // 自动处理
            //processEmbeddingData();
        };
        reader.onerror = function() {
            loadingIndicator.style.display = 'none';
            document.getElementById('tab-embedding').style.display = 'block';
            showError('文件读取失败');
        };
        reader.readAsText(file);
    }
    
    // 处理Embedding预处理数据
    function processEmbeddingData() {
        // 获取用户输入
        const markdownText = embeddingTextarea.value.trim();
        const format = outputFormat.value;
        const filename = outputFilename.value.trim();
        
        // 验证输入
        if (!markdownText) {
            showError('请提供Markdown文本内容');
            return;
        }
        
        // 显示加载指示器
        tabContents.forEach(content => content.style.display = 'none');
        loadingIndicator.style.display = 'flex';
        
        // 准备表单数据
        const formData = new FormData();
        formData.append('text', markdownText);
        formData.append('format', format);
        if (filename) {
            formData.append('filename', filename);
        }
        
        // 发送请求
        fetch('/preprocess-for-storage', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP错误! 状态: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // 处理成功响应
            loadingIndicator.style.display = 'none';
            
            // 显示结果
            let resultString = '';
            
            // 显示处理统计
            resultString += `# 预处理完成\n\n`;
            resultString += `- 生成的问答对数量: ${data.qa_count}\n`;
            
            // 显示文件路径
            if (data.json_path) {
                resultString += `- JSON文件路径: ${data.json_path}\n`;
            }
            if (data.csv_path) {
                resultString += `- CSV文件路径: ${data.csv_path}\n`;
            }
            
            resultString += `\n## 处理说明\n\n`;
            resultString += `问答对已按照规则从Markdown文本中提取：\n\n`;
            resultString += `1. 标题作为问题(question)\n`;
            resultString += `2. 标题下内容作为答案(answer)\n`;
            resultString += `3. 多级标题使用逗号连接\n`;
            
            // 显示结果
            resultText.textContent = resultString;
            originalMarkdown = resultString;
            
            // 显示Markdown控件并设置为预览模式
            markdownViewControls.style.display = 'flex';
            resultContainer.style.display = 'block';
            resultContent.style.display = 'none';
            markdownPreview.style.display = 'block';
            
            // 更新视图按钮状态
            viewButtons.forEach(btn => btn.classList.remove('active'));
            viewButtons[1].classList.add('active'); // 启用预览视图
            
            // 显示全屏按钮
            fullscreenBtn.style.display = 'inline-block';
            
            // 渲染Markdown
            renderMarkdown(resultString);
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            document.getElementById('tab-embedding').style.display = 'block';
            showError(`预处理失败: ${error.message}`);
        });
    }
});