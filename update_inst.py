import re
import json
import icon
from icon2 import icon_map

icon_map["handle_overlong_tool_outputs"] = icon_map["overlong_tool_output"]
icon_map["python_execute"] = icon_map["python-execute"]

with open("map.txt") as f:
    for line in f:
        name, task_id, task_cat = line.split()
        name = name.lower()
        with open(f"docs/tasks/{task_cat}/{task_id}_.mdx", encoding="utf-8") as mdx:
            content = mdx.read()
        with open(f"../mcpbench_dev/tasks/finalpool/{name}/docs/task.md", encoding="utf-8") as ins:
            inst = ins.read()
        inst = inst.replace("\\", "\\\\")
        inst = inst.replace("{", r"\{")
        inst = inst.replace("}", r"\}")
        new_content = re.sub(
            r'(## Instruction\s*\n).*?(?=\n## |\Z)',
            r'\1' + inst + '\n',
            content,
            flags=re.DOTALL
        )
        with open(f"docs/tasks/{task_cat}/{task_id}_.mdx", "w", encoding="utf-8") as mdx:
            mdx.write(new_content)


        with open(f"../mcpbench_dev/tasks/finalpool/{name}/task_config.json", "r", encoding="utf-8") as json_file:
            config_data = json.load(json_file)
            servers = config_data['needed_mcp_servers']
            local_tools = config_data['needed_local_tools']

            # Sort by string length (shortest to longest)
            servers = sorted(servers, key=len)
            local_tools = sorted(local_tools, key=len)

            card_str = '<Card>\n<div className="tools-container">\n<div className="mcp-servers-container">\n<div className="mcp-servers-title">\nMCP Servers\n</div>\n<div className="mcp-servers-grid">\n'
            
            for server in servers:
                card_str += '<div className="mcp-server-item">\n'
                card_str += f"{icon_map[server]}\n"
                card_str += '<span className="mcp-server-name">' + server + '</span>\n'
                card_str += '</div>\n'
            
            card_str += '</div>\n</div>\n'

            card_str += '<div className="local-tools-container">\n<div className="mcp-servers-title">\nLocal Tools\n</div>\n<div className="local-tools-grid">\n'

            for tool in local_tools:
                card_str += '<div className="local-tool-item">\n'
                card_str += f"{icon_map[tool]}\n"
                card_str += '<span className="local-tool-name">' + tool + '</span>\n'
                card_str += '</div>\n'

            card_str += '</div>\n</div>\n</div>\n</Card>\n'

        with open(f"docs/tasks/{task_cat}/{task_id}_.mdx", "r", encoding="utf-8") as mdx:
            content = mdx.read()

        # Replace the first <Columns cols={2}>...</Columns> with card_str
        new_content = re.sub(
            r'<Card>.*?</Card>',
            card_str,
            content,
            count=1,
            flags=re.DOTALL
        )

        with open(f"docs/tasks/{task_cat}/{task_id}_.mdx", "w", encoding="utf-8") as mdx:
            mdx.write(new_content)
