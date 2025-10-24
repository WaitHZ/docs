/**
 * Lazy Loading for Tool Details
 * 实现工具详细信息的懒加载，提升Safari性能
 */

(function() {
    'use strict';
    
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        initializeLazyLoading();
    });
    
    function initializeLazyLoading() {
        // 查找所有工具详情复选框
        const checkboxes = document.querySelectorAll('.tool-details-checkbox');
        
        checkboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                if (this.checked) {
                    lazyLoadToolDetails(this);
                } else {
                    hideToolDetails(this);
                }
            });
        });
    }
    
    function lazyLoadToolDetails(checkbox) {
        const toolResultId = checkbox.id.replace('-checkbox', '');
        const placeholder = document.querySelector(`#${toolResultId} .tool-details-placeholder`);
        const details = document.querySelector(`#${toolResultId} .tool-details`);
        
        if (!placeholder || !details) return;
        
        // 显示加载占位符
        showPlaceholder(placeholder);
        
        // 使用requestAnimationFrame确保动画流畅
        requestAnimationFrame(function() {
            // 模拟加载延迟（实际项目中可以移除）
            setTimeout(function() {
                // 隐藏占位符，显示实际内容
                hidePlaceholder(placeholder);
                showDetails(details);
            }, 300); // 300ms延迟，让用户看到加载效果
        });
    }
    
    function showPlaceholder(placeholder) {
        placeholder.style.maxHeight = '60px';
        placeholder.style.opacity = '1';
        placeholder.style.visibility = 'visible';
    }
    
    function hidePlaceholder(placeholder) {
        placeholder.style.maxHeight = '0';
        placeholder.style.opacity = '0';
        placeholder.style.visibility = 'hidden';
    }
    
    function showDetails(details) {
        details.style.maxHeight = '1000px';
        details.style.opacity = '1';
        details.style.visibility = 'visible';
    }
    
    function hideToolDetails(checkbox) {
        const toolResultId = checkbox.id.replace('-checkbox', '');
        const placeholder = document.querySelector(`#${toolResultId} .tool-details-placeholder`);
        const details = document.querySelector(`#${toolResultId} .tool-details`);
        
        if (placeholder) {
            hidePlaceholder(placeholder);
        }
        
        if (details) {
            details.style.maxHeight = '0';
            details.style.opacity = '0';
            details.style.visibility = 'hidden';
        }
    }
    
    // Safari性能优化
    if (navigator.userAgent.includes('Safari') && !navigator.userAgent.includes('Chrome')) {
        // 为Safari添加额外的性能优化
        document.addEventListener('DOMContentLoaded', function() {
            // 使用Intersection Observer来延迟加载不在视口中的内容
            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver(function(entries) {
                    entries.forEach(function(entry) {
                        if (entry.isIntersecting) {
                            // 当工具结果进入视口时，预加载一些内容
                            preloadToolContent(entry.target);
                        }
                    });
                }, {
                    rootMargin: '50px 0px',
                    threshold: 0.1
                });
                
                // 观察所有工具结果
                const toolResults = document.querySelectorAll('.result-box, .error-box, .overlong-box');
                toolResults.forEach(function(result) {
                    observer.observe(result);
                });
            }
        });
    }
    
    function preloadToolContent(element) {
        // 预加载工具内容，但不显示
        const details = element.querySelector('.tool-details');
        if (details && !details.dataset.preloaded) {
            details.dataset.preloaded = 'true';
            // 这里可以添加预加载逻辑
        }
    }
    
})();
