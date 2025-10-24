/**
 * Virtual Scrolling for Tool Results
 * 为大量工具结果实现虚拟滚动，大幅提升Safari性能
 */

(function() {
    'use strict';
    
    let virtualScrollInstance = null;
    
    document.addEventListener('DOMContentLoaded', function() {
        initializeVirtualScroll();
    });
    
    function initializeVirtualScroll() {
        const toolContainer = document.querySelector('.tools-container');
        if (!toolContainer) return;
        
        const toolResults = Array.from(document.querySelectorAll('.result-box, .error-box, .overlong-box'));
        
        // 如果工具结果数量超过阈值，启用虚拟滚动
        const VIRTUAL_SCROLL_THRESHOLD = 20;
        if (toolResults.length > VIRTUAL_SCROLL_THRESHOLD) {
            enableVirtualScroll(toolContainer, toolResults);
        }
    }
    
    function enableVirtualScroll(container, toolResults) {
        // 创建虚拟滚动容器
        const virtualContainer = document.createElement('div');
        virtualContainer.className = 'virtual-scroll-container';
        virtualContainer.style.height = '600px';
        virtualContainer.style.overflow = 'auto';
        virtualContainer.style.position = 'relative';
        
        // 计算每个工具结果的高度（估算）
        const ITEM_HEIGHT = 80; // 每个工具结果的大概高度
        const VISIBLE_ITEMS = Math.ceil(600 / ITEM_HEIGHT) + 2; // 可见项目数 + 缓冲区
        
        // 创建视口
        const viewport = document.createElement('div');
        viewport.className = 'virtual-scroll-viewport';
        viewport.style.height = '100%';
        viewport.style.position = 'relative';
        
        // 创建内容容器
        const contentContainer = document.createElement('div');
        contentContainer.className = 'virtual-scroll-content';
        contentContainer.style.position = 'relative';
        contentContainer.style.height = `${toolResults.length * ITEM_HEIGHT}px`;
        
        // 将原始工具结果移动到虚拟容器中
        toolResults.forEach(function(result, index) {
            result.style.position = 'absolute';
            result.style.top = `${index * ITEM_HEIGHT}px`;
            result.style.width = '100%';
            result.style.height = `${ITEM_HEIGHT}px`;
            result.style.overflow = 'hidden';
            result.style.display = 'none'; // 初始隐藏
            contentContainer.appendChild(result);
        });
        
        viewport.appendChild(contentContainer);
        virtualContainer.appendChild(viewport);
        
        // 替换原始容器
        container.parentNode.replaceChild(virtualContainer, container);
        
        // 实现滚动逻辑
        let scrollTop = 0;
        let startIndex = 0;
        let endIndex = VISIBLE_ITEMS;
        
        function updateVisibleItems() {
            const newStartIndex = Math.floor(scrollTop / ITEM_HEIGHT);
            const newEndIndex = Math.min(newStartIndex + VISIBLE_ITEMS, toolResults.length);
            
            // 隐藏不在视口中的项目
            toolResults.forEach(function(result, index) {
                if (index < newStartIndex || index >= newEndIndex) {
                    result.style.display = 'none';
                } else {
                    result.style.display = 'block';
                }
            });
            
            startIndex = newStartIndex;
            endIndex = newEndIndex;
        }
        
        // 监听滚动事件
        virtualContainer.addEventListener('scroll', function() {
            scrollTop = virtualContainer.scrollTop;
            updateVisibleItems();
        });
        
        // 初始显示
        updateVisibleItems();
        
        // 保存实例引用
        virtualScrollInstance = {
            container: virtualContainer,
            updateVisibleItems: updateVisibleItems
        };
    }
    
    // 暴露API供外部调用
    window.VirtualScroll = {
        getInstance: function() {
            return virtualScrollInstance;
        },
        
        refresh: function() {
            if (virtualScrollInstance) {
                virtualScrollInstance.updateVisibleItems();
            }
        }
    };
    
})();
