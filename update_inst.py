import re

with open("map.txt") as f:
    for line in f:
        name, task_id, task_cat = line.split()
        
        print(name, task_id, task_cat)

        with open(f"docs/tasks/{task_cat}/{task_id}_.mdx", encoding="utf-8") as mdx:
            content = mdx.read()

        with open(f"../mcpbench_dev/tasks/finalpool/{name}/docs/task.md", encoding="utf-8") as ins:
            inst = ins.read()

        # 使用正则表达式匹配 ## Instruction 到下一个 ## 标题或文件结尾之间的内容
        new_content = re.sub(
            r'(## Instruction\s*\n).*?(?=\n## |\Z)',
            r'\1' + inst + '\n',
            content,
            flags=re.DOTALL
        )

        # 写回文件
        with open(f"docs/tasks/{task_cat}/{task_id}_.mdx", "w", encoding="utf-8") as mdx:
            mdx.write(new_content)
            
        break
