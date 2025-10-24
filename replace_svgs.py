#!/usr/bin/env python3
"""
批量替换selected.mdx中的SVG为PNG
"""

import re

# 读取文件
with open('/mnt/haozewu/docs/docs/selected.mdx', 'r', encoding='utf-8') as f:
    content = f.read()

# SVG到PNG的映射
svg_to_png = {
    'excel': 'excel.png',
    'google_sheet': 'google_sheet.png', 
    'google_cloud': 'google_cloud.png',
    'google_search': 'google_search.png',
    'google_map': 'google_map.png',
    'google_calendar': 'calendar.png',
    'google_forms': 'google_forms.png',
    'github': 'github.png',
    'git': 'git.png',
    'huggingface': 'hf.png',
    'k8s': 'k8s.png',
    'snowflake': 'snowflake.png',
    'word': 'word.png',
    'pptx': 'pptx.png',
    'pdf': 'pdf.png',
    'python': 'python.png',
    'terminal': 'terminal.png',
    'memory': 'memory.png',
    'filesystem': 'filesystem.png',
    'web_search': 'google_search.png',
    'yahoo-finance': 'yahoo.png',
    'howtocook': 'cook.png',
    'arxiv_local': 'arxiv.png',
    'scholarly': 'scholar.png',
    'claim_done': 'claim_done.png',
    'playwright_with_chunk': 'playwright.png',
    'pdf-tools': 'pdf.png',
    'python-execute': 'python.png',
    'history': 'history.png',
    'emails': 'mail.png',
    'notion': 'notion.png',
    'wandb': 'wandb.png',
    'canvas': 'canvas.png',
    'fetch': 'fetch.png',
    'rail_12306': '12306.png',
    'youtube-transcript': 'youtube_transcript.png',
    'youtube': 'youtube.png',
    'arxiv-latex': 'latex.png',
    'sleep': 'sleep.png',
    'woocommerce': 'woo.png'
}

# 替换SVG为PNG
def replace_svg_with_png(content):
    # 查找所有SVG标签
    svg_pattern = r'<svg[^>]*>.*?</svg>'
    svgs = re.findall(svg_pattern, content, re.DOTALL)
    
    for svg in svgs:
        # 根据注释确定图标类型
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if svg in line:
                # 查找前面的注释
                for j in range(max(0, i-3), i):
                    if '/*' in lines[j] and '*/' in lines[j]:
                        comment = lines[j].strip()
                        # 提取图标名称
                        for icon_name, png_name in svg_to_png.items():
                            if icon_name in comment:
                                # 替换SVG为PNG
                                png_tag = f'<img src="/icons/{png_name}" style={{height: "64px", width: "64px", margin: 0, padding: 0, display: \'inline-block\'}} />'
                                content = content.replace(svg, png_tag)
                                print(f"替换 {icon_name} SVG 为 {png_name}")
                                break
                        break
                break
    
    return content

# 执行替换
new_content = replace_svg_with_png(content)

# 写回文件
with open('/mnt/haozewu/docs/docs/selected.mdx', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SVG替换完成！")
