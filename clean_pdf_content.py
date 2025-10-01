#!/usr/bin/env python3
"""
PDF内容净化脚本
清理PDF提取内容中的多余空格、转义字符和格式化问题
"""

import re
import json
import sys
from pathlib import Path

def clean_pdf_text(text):
    """
    清理PDF提取的文本内容
    """
    if not text:
        return text
    
    # 1. 移除JSON转义字符
    text = text.replace('\\n', '\n')
    text = text.replace('\\t', '\t')
    text = text.replace('\\"', '"')
    text = text.replace('\\u0000', '')
    text = text.replace('\\u2013', '–')
    
    # 2. 清理多余的空格分隔字符
    # 将 "P a g e  1  o f  1" 转换为 "Page 1 of 1"
    text = re.sub(r'([A-Za-z])\s+([A-Za-z])', r'\1\2', text)
    
    # 3. 清理数字间的多余空格
    # 将 "6 6 F 9 9 4 5 C" 转换为 "66F9945C"
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    text = re.sub(r'([A-Za-z])\s+(\d)', r'\1\2', text)
    text = re.sub(r'(\d)\s+([A-Za-z])', r'\1\2', text)
    
    # 4. 清理货币符号和数字间的空格
    text = re.sub(r'(\$)\s+(\d)', r'\1\2', text)
    text = re.sub(r'(\d)\s+([A-Z]{3})', r'\1 \2', text)  # 保留货币代码前的空格
    
    # 5. 清理日期格式
    text = re.sub(r'([A-Za-z]{3})\s+(\d{1,2})\s+,\s+(\d{4})', r'\1 \2, \3', text)
    
    # 6. 清理邮箱地址
    text = re.sub(r'([a-zA-Z0-9._%+-]+)\s+@\s+([a-zA-Z0-9.-]+)\s+\.\s+([a-zA-Z]{2,})', 
                  r'\1@\2.\3', text)
    
    # 7. 清理地址中的多余空格
    text = re.sub(r'([A-Za-z])\s+([A-Za-z])\s+([A-Za-z])', r'\1\2\3', text)
    
    # 8. 清理多余的空行
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    # 9. 清理行首行尾空格
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    
    return text

def clean_json_content(json_str):
    """
    清理JSON字符串中的PDF内容
    """
    try:
        # 解析JSON
        data = json.loads(json_str)
        
        # 如果是包含text字段的对象
        if isinstance(data, dict) and 'text' in data:
            data['text'] = clean_pdf_text(data['text'])
        # 如果是字符串
        elif isinstance(data, str):
            data = clean_pdf_text(data)
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        # 如果不是有效JSON，直接清理文本
        return clean_pdf_text(json_str)

def clean_mdx_file(file_path):
    """
    清理MDX文件中的PDF内容
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并清理JSON代码块中的PDF内容
    def replace_json_block(match):
        json_content = match.group(1)
        cleaned_json = clean_json_content(json_content)
        return f"```json\n{cleaned_json}\n```"
    
    # 匹配 ```json ... ``` 代码块
    pattern = r'```json\n(.*?)\n```'
    cleaned_content = re.sub(pattern, replace_json_block, content, flags=re.DOTALL)
    
    # 查找并清理文本代码块中的PDF内容
    def replace_text_block(match):
        text_content = match.group(1)
        cleaned_text = clean_pdf_text(text_content)
        return f"```text\n{cleaned_text}\n```"
    
    # 匹配 ```text ... ``` 代码块
    pattern = r'```text\n(.*?)\n```'
    cleaned_content = re.sub(pattern, replace_text_block, cleaned_content, flags=re.DOTALL)
    
    return cleaned_content

def main():
    if len(sys.argv) != 2:
        print("用法: python clean_pdf_content.py <file_path>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    print(f"正在清理文件: {file_path}")
    
    # 备份原文件
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"已创建备份文件: {backup_path}")
    
    # 清理内容
    cleaned_content = clean_mdx_file(file_path)
    
    # 写入清理后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"文件已清理完成: {file_path}")
    print("清理内容包括:")
    print("- 移除JSON转义字符")
    print("- 清理多余的空格分隔")
    print("- 格式化日期和货币")
    print("- 清理邮箱地址")
    print("- 移除多余空行")

if __name__ == "__main__":
    main()
