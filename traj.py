import argparse
from ast import arguments, literal_eval
import os
# from tqdm import tqdm
import json
import re
from icon import icon_map

icon_cnt = len(icon_map)

if "web_search" in icon_map:
    icon_map["googlesearch"] = icon_map["web_search"]
if "playwright_with_chunk" in icon_map:
    icon_map["playwright"] = icon_map["playwright_with_chunk"]

def categorize_tool_output(tool_output_str):
    tooloutput_type = None
    if tool_output_str.strip().startswith("Error running tool"):
        tooloutput_type = "error_in_tool_call"
    if tool_output_str.strip().endswith("Please check this file carefully, as it may be very long!)"):
        tooloutput_type = "overlong_tool_output"
    if "not found in agent" in tool_output_str.strip():
        tooloutput_type = "tool_name_not_found"
    if tooloutput_type is None:
        tooloutput_type = "normal_tool_output"
    return tooloutput_type


def find_mdx_files_with_underscore(dir_path):
    mdx_files = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith("_.mdx"):
                mdx_files.append(os.path.join(root, file))
    return mdx_files


def clear(task_dir):
    for root, dirs, files in os.walk(task_dir):
        for file in files:
            if file.endswith("__.mdx"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")


def raw_json_str_to_python(obj: str) -> dict:
    """
    把控制台里打印出来的“伪 JSON 字符串”还原成 Python 对象。
    1. 去掉首尾的引号（如果有）
    2. 把真正的 JSON 需要的转义补回去
    3. json.loads 解析
    """
    # 1. 去掉首尾可能被人手工包上的双引号
    obj = obj.strip()
    if (obj.startswith('"') and obj.endswith('"')) or \
       (obj.startswith("'") and obj.endswith("'")):
        obj = obj[1:-1]

    # 2. 把“用户眼里”的反斜杠变成“JSON 眼里”的反斜杠
    #    即：\n  -> \\n
    #        \" -> \\\"
    #        \\ -> \\\\
    obj = obj.encode('utf-8').decode('unicode_escape')   # 先解开 \n \t \"
    obj = obj.replace('\\', r'\\')                       # 再整体把反斜杠翻倍
    obj = obj.replace(r'\"', r'\"')                      # 把已经翻倍的 \" 还原

    # 3. 现在它是合法 JSON 字符串了
    return json.loads(obj)


def main(args):
    checked_tasks = {
        34, 37, 38, 39, 49, 125, 149, 161, 162, 165, 183, 188, 189, 190, 196, 197, 306, 404,
        16, 78, 133, 155, 156, 159, 169, 181, 182, 201, 209, 210, 313, 316, 319, 351, 371,
        126, 141, 143, 179, 223, 267, 275, 284, 345, 352,
        23, 24, 108, 109, 116, 127, 131, 142, 144, 147, 150, 163, 235, 237, 292, 327, 331, 368,
        2, 3, 4, 5, 9, 10, 30, 32, 66, 88, 152, 158, 229, 290, 372,
        95, 113, 266, 279, 285, 299, 300, 301, 303, 304, 305,
        17, 18, 19, 42, 47, 93, 94, 146, 160, 173, 241,  242, 244, 245, 248, 280, 286, 294, 295,
    }
    # checked_tasks = set()
    print(len(checked_tasks))

    tool_calls = dict()
    tool_result_counter = [0]  # Use list to make it mutable

    task_dir = args.task_dir

    parallel_tool_call_num = 0

    clear(task_dir)

    mdx_files = find_mdx_files_with_underscore(task_dir)
    for f in mdx_files:
        f_prefix = f.replace("_.mdx", "")
        task_id = int(f_prefix.split("/")[-1])
        
        target_md = f_prefix + ".mdx"

        with open(f, "r", encoding="utf-8") as src, open(target_md, "w", encoding="utf-8") as dst:
            content = src.read()
            
            # # 检查是否已经有 frontmatter
            # if content.startswith("---"):
            #     # 找到 frontmatter 的结束位置
            #     end_frontmatter = content.find("---", 3)
            #     if end_frontmatter != -1:
            #         # 在 frontmatter 中添加 hideTableOfContents
            #         frontmatter = content[3:end_frontmatter]
            #         if "hideTableOfContents" not in frontmatter:
            #             frontmatter += "mode: wide"
            #         dst.write("---" + frontmatter + "\n---" + content[end_frontmatter + 3:])
            #     else:
            #         # 如果 frontmatter 格式不正确，直接添加
            #         dst.write(content)
            # else:
            #     # 如果没有 frontmatter，添加一个
            #     dst.write("---\nmode: wide\n---\n\n" + content)

            dst.write(f"{content}\n")

            log_dir = f_prefix + "/"

            if os.path.exists(log_dir) and len(os.listdir(log_dir)) > 0 and task_id in checked_tasks:
            # if os.path.exists(log_dir) and len(os.listdir(log_dir)) > 0:

                dst.write("We use superscripts to indicate which turn a message belongs to. Since the model may invoke multiple tools in parallel, adjacent tool calls may belong to the same turn.\n")

                dst.write(f"\n<AccordionGroup>\n")

                for log_file in sorted(os.listdir(log_dir)):
                    if log_file.endswith(".json") and ("claude" in log_file.lower() or "deepseek" in log_file.lower()):
                        log_path = os.path.join(log_dir, log_file)
                        with open(log_path, "r", encoding="utf-8") as lf:
                            log_data = json.load(lf)
                            msgs = log_data["messages"]
                            
                            model_name = log_path.split("/")[-1].replace(".json", "")
                            dst.write(f"<Accordion title=\"{model_name}\">\n\n")

                            dst.write("<Columns cols={3}>\n")
                            if log_data["pass"]:
                                dst.write(f"<Card title=\"Task Completion\" icon=\"check\">\n")
                                dst.write(f"Completed\n")
                            else:
                                dst.write(f"<Card title=\"Task Completion\" icon=\"x\">\n")
                                dst.write(f"Failed\n")
                            dst.write(f"</Card>\n")
                            dst.write(f"<Card title=\"Tool Calls\" icon=\"wrench\">\n")
                            tool_call_num = 0
                            for msg in msgs:
                                if msg["role"] == "assistant" and "tool_calls" in msg:
                                    tool_call_num += len(msg["tool_calls"])
                            dst.write(f"{tool_call_num}\n")
                            dst.write(f"</Card>\n")
                            dst.write(f"<Card title=\"Turns\" icon=\"arrows-rotate\">\n")
                            assit_msgs = [msg for msg in msgs if msg["role"] == "assistant"]
                            dst.write(f"{len(assit_msgs)}\n")
                            dst.write(f"</Card>\n")
                            dst.write(f"</Columns>\n\n")

                            turn_num = 0

                            for i, msg in enumerate(msgs):
                                if msg["role"] == "user":
                                    continue
                                elif msg["role"] == "assistant":

                                    turn_num += 1

                                    if "tool_calls" in msg:
                                        if not (msg["content"] == "" or msg["content"] is None or msg["content"] == "null"):
                                            dst.write(f"<div className=\"thinking-box\">\n")
                                            dst.write(f"🧐`Agent`<sup>{turn_num}</sup>&nbsp;\n\n{msg['content'].strip().replace("{", r"\{").replace("}", r"\}")}\n</div>\n\n")

                                        parallel_tool_call_num = len(msg["tool_calls"])
                                        for msg_tool_call in msg["tool_calls"]:
                                            if msg_tool_call['type'] == "function":
                                                if msg_tool_call['function']['name'] == "local-python-execute":
                                                    # dst.write(f"<div className=\"tool-call-box\">\n")
                                                    # dst.write(f"{icon_map["python-execute"]} `python-execute`\n\n")
                                                    # dst.write(f"🛠 `python-execute`\n\n")
                                                    try:
                                                        arg_s = json.loads(msg_tool_call['function']['arguments'])
                                                    except:
                                                        print("aaa")
                                                        arg_s = msg_tool_call['function']['arguments']
                                                    # dst.write(f"```python {arg_s['filename'] if 'filename' in arg_s else ''}\n")
                                                    try:
                                                        code = arg_s['code']
                                                    except:
                                                        code = arg_s
                                                    # dst.write(f"{code if 'code' in arg_s else ''}\n")
                                                    # dst.write(f"```\n")
                                                    # dst.write(f"</div>\n\n")
                                                    tool_call_id = msg_tool_call['id']
                                                    tool_calls[tool_call_id] = {
                                                        "server_name": "python-execute",
                                                        "function_name": "",
                                                        "code": code,
                                                    }
                                                    # print(msg_tool_call)
                                                    # exit()
                                                elif "overlong" in msg_tool_call['function']['name']:
                                                    # dst.write(f"<div className=\"tool-call-box\">\n")
                                                    # dst.write(f"{icon_map['overlong_tool_output']} `{msg_tool_call['function']['name'].replace("local-", "").replace("tooloutput", "tool_output")}`\n\n")
                                                    # dst.write(f"```json\n")
                                                    argu_s = msg_tool_call['function']['arguments'].strip()[1:-1].split(",")
                                                    arg_str = "{\n"
                                                    # dst.write("{\n")
                                                    for i, arg in enumerate(argu_s):
                                                        if i == 0:
                                                            # dst.write(f"\t{arg}")
                                                            arg_str += f"\t{arg}"
                                                        else:
                                                            # dst.write(f",\n\t{arg}")
                                                            arg_str += f",\n\t{arg}"
                                                    arg_str += "\n}\n"
                                                    tool_call_id = msg_tool_call['id']
                                                    tool_calls[tool_call_id] = {
                                                        "server_name": msg_tool_call['function']['name'].replace("local-", "").replace("tooloutput", "tool_output"),
                                                        "function_name": "",
                                                        "arguments": arg_str,
                                                    }
                                                    # dst.write(f"```\n")
                                                    # dst.write(f"</div>\n\n")
                                                elif msg_tool_call['function']['name'] == "filesystem-write_file":
                                                    try:
                                                        arg_s = json.loads(msg_tool_call['function']['arguments'])
                                                        arg_str = f"workspace/{arg_s['path'].split('/')[-1].replace("@", "@")}\n{arg_s['content'].replace("```", "`*3")}\n"
                                                    except:
                                                        print("bbb")
                                                        arg_s = msg_tool_call['function']['arguments']
                                                        arg_str = arg_s
                                                    # dst.write(f"<div className=\"tool-call-box\">\n")
                                                    # dst.write(f"{icon_map['filesystem']} `{msg_tool_call['function']['name']}`\n\n")
                                                    # dst.write(f"🛠 `{msg_tool_call['function']['name']}`\n\n")
                                                    
                                                    tool_call_id = msg_tool_call['id']
                                                    tool_calls[tool_call_id] = {
                                                        "server_name": "filesystem",
                                                        "function_name": "write_file",
                                                        "arguments": arg_str,
                                                    }
                                                    # dst.write(f"```\n")
                                                    # dst.write(f"</div>\n\n")
                                                else:
                                                    server_function_name = msg_tool_call['function']['name']

                                                    if server_function_name.startswith("local"):
                                                        server_name = ''.join(server_function_name.split("-")[1:])
                                                        function_name = ""
                                                    elif server_function_name.startswith("google-cloud"):
                                                        server_name = "google-cloud"
                                                        function_name = "".join(server_function_name.split("-")[2:])
                                                    elif server_function_name.startswith("yahoo-finance"):
                                                        server_name = "yahoo-finance"
                                                        function_name = "".join(server_function_name.split("-")[2:])
                                                    elif server_function_name.startswith("pdf-tools"):
                                                        server_name = "pdf-tools"
                                                        function_name = "".join(server_function_name.split("-")[2:])
                                                    else:
                                                        server_name, *function_name = server_function_name.split("-")
                                                        if len(function_name) == 1:
                                                            function_name = function_name[0]
                                                        else:
                                                            function_name = "-".join(function_name)
                                                    # dst.write(f"{icon_map[server_name]} `{server_name} {function_name}`\n\n" if server_name in icon_map else f"🛠 `{server_name} {function_name}`\n\n")
                                                    # dst.write(f"🛠 `{server_name} {function_name}`\n\n")
                                                    # dst.write(f"```json\n")
                                                    argu_s = msg_tool_call['function']['arguments'].strip()[1:-1].split(",")

                                                    if len(argu_s) == 1 and argu_s[0] == "":
                                                        # dst.write("{}\n")
                                                        arg_str = "{}\n"
                                                    else:
                                                        arg_str = "{\n"
                                                        # dst.write("{\n")
                                                        for i, arg in enumerate(argu_s):
                                                            if i == 0:
                                                                # dst.write(f"\t{arg.replace("@", "@")}")
                                                                arg_str += f"\t{arg.strip()}"
                                                            else:
                                                                arg_str += f",\n\t{arg.strip()}"
                                                                # dst.write(f",\n\t{arg.replace("@", "@")}")
                                                        # dst.write("\n}\n")
                                                        arg_str += "\n}\n"
                                                    # dst.write(f"```\n")
                                                    # dst.write(f"</div>\n\n")
                                                    tool_call_id = msg_tool_call['id']
                                                    tool_calls[tool_call_id] = {
                                                        "server_name": server_name,
                                                        "function_name": function_name,
                                                        "arguments": arg_str
                                                    }
                                            else:
                                                raise NotImplementedError(f"Unsupported tool call type: {msg_tool_call['type']}")
                                    else:
                                        dst.write(f"<div className=\"thinking-box\">\n")
                                        dst.write(f"🧐`Agent`<sup>{turn_num}</sup>\n\n{msg['content'].strip().replace("{", r"\{").replace("}", r"\}").replace("<", "[").replace(">", ']')}\n</div>\n\n")
                                elif msg["role"] == "tool":
                                    tooloutput_type = categorize_tool_output(msg['content'])
                                    tool_call_id = msg["tool_call_id"]
                                    tool_call = tool_calls[tool_call_id]

                                    # dst.write(f"<div className=\"result-box\">\n" if tooloutput_type == "normal_tool_output" else f"<div className=\"error-box\">\n")

                                    # Generate unique ID for this tool result using counter
                                    tool_result_counter[0] += 1
                                    tool_result_id = f"tool-result-{task_id}-{tool_result_counter[0]}"
                                    
                                    dst.write(f"<div className=\"result-box\" id=\"{tool_result_id}\">\n" if tooloutput_type == "normal_tool_output" else f"<div className=\"error-box\" id=\"{tool_result_id}\">\n")

                                    if tooloutput_type == "normal_tool_output":
                                        try:
                                            with open("_tmp", "w", encoding="utf-8") as f:
                                                print(msg['content'], file=f)
                                            tool_res = json.load(open("_tmp", "r", encoding="utf-8"))
                                            tool_res = tool_res["text"]
                                            tool_res = tool_res.replace('```', '')
                                        except:
                                            tool_res = msg['content']
                                            if tool_res.startswith('[') and tool_res.endswith(']'):
                                                tool_res = tool_res.replace('[{', '[\n{')
                                                tool_res = tool_res.replace('}]', '}\n]')
                                                tool_res = tool_res.replace('}, {', '},\n{')
                                                tool_res = tool_res.replace(r'\n', ' ')

                                        server_name = tool_call["server_name"]
                                        function_name = tool_call["function_name"]
                                        server_function_name = f"{server_name} {function_name}" if function_name != "" else server_name

                                        # dst.write(f"🔍`tool result`\n")
                                        dst.write(f"<div className=\"tool-header\">\n")
                                        dst.write(f"  <div className=\"tool-name\">{icon_map[server_name]} `{server_function_name}`<sup>{turn_num}</sup></div>\n" if server_name in icon_map else f"  <div className=\"tool-name\">🛠 `{server_function_name}`</div>\n")
                                        dst.write(f"  <label for=\"{tool_result_id}-checkbox\" className=\"tool-details-toggle\"></label>\n")
                                        dst.write(f"</div>\n")
                                        dst.write(f"<input type=\"checkbox\" id=\"{tool_result_id}-checkbox\" className=\"tool-details-checkbox\" />\n")
                                        dst.write(f"<div className=\"tool-details\">\n")
                                        if server_name == "python-execute":
                                            dst.write(f"```python\n{tool_call["code"]} code\n```\n\n")
                                        else:
                                            dst.write(f"```json arguments\n{tool_call["arguments"]}\n```\n\n")

                                        dst.write(f"```json output_result\n{tool_res}\n```\n\n")
                                        dst.write(f"</div>\n")
                                    elif tooloutput_type == "error_in_tool_call":
                                        server_name = tool_call["server_name"]
                                        function_name = tool_call["function_name"]
                                        server_function_name = f"{server_name} {function_name}" if function_name != "" else server_name
                                        dst.write(f"<div className=\"tool-header\">\n")
                                        dst.write(f"  <div className=\"tool-name\">❌ `{server_function_name}`<sup>{turn_num}</sup></div>\n")
                                        dst.write(f"  <label for=\"{tool_result_id}-checkbox\" className=\"tool-details-toggle\"></label>\n")
                                        dst.write(f"</div>\n")
                                        dst.write(f"<input type=\"checkbox\" id=\"{tool_result_id}-checkbox\" className=\"tool-details-checkbox\" />\n")
                                        dst.write(f"<div className=\"tool-details\">\n")
                                        if server_name == "python-execute":
                                            dst.write(f"```python\n{tool_call["code"]} code\n```\n")
                                        else:
                                            dst.write(f"```json arguments\n{tool_call["arguments"]}\n```\n")
                                        dst.write(f"```json error_message\n{msg['content'].split(":")[0]}\n```\n\n")
                                        dst.write(f"</div>\n")
                                    elif tooloutput_type == "overlong_tool_output":
                                        server_name = tool_call["server_name"]
                                        function_name = tool_call["function_name"]
                                        server_function_name = f"{server_name} {function_name}" if function_name != "" else server_name
                                        dst.write(f"<div className=\"tool-header\">\n")
                                        dst.write(f"  <div className=\"tool-name\">⚠️ `{server_function_name}`<sup>{turn_num}</sup></div>\n")
                                        dst.write(f"  <label for=\"{tool_result_id}-checkbox\" className=\"tool-details-toggle\"></label>\n")
                                        dst.write(f"</div>\n")
                                        dst.write(f"<input type=\"checkbox\" id=\"{tool_result_id}-checkbox\" className=\"tool-details-checkbox\" />\n")
                                        dst.write(f"<div className=\"tool-details\">\n")
                                        if server_name == "python-execute":
                                            dst.write(f"```python\n{tool_call["code"]} code\n```\n")
                                        else:
                                            dst.write(f"```json arguments\n{tool_call["arguments"]}\n```\n")
                                        dst.write(f"```json error_message\n{msg['content']}\n```\n\n")
                                        dst.write(f"</div>\n")
                                    elif tooloutput_type == "tool_name_not_found":
                                        server_name = tool_call["server_name"]
                                        function_name = tool_call["function_name"]
                                        server_function_name = f"{server_name} {function_name}" if function_name != "" else server_name
                                        dst.write(f"<div className=\"tool-header\">\n")
                                        dst.write(f"  <div className=\"tool-name\">❓ `{server_function_name}`<sup>{turn_num}</sup></div>\n")
                                        dst.write(f"  <label for=\"{tool_result_id}-checkbox\" className=\"tool-details-toggle\"></label>\n")
                                        dst.write(f"</div>\n")
                                        dst.write(f"<input type=\"checkbox\" id=\"{tool_result_id}-checkbox\" className=\"tool-details-checkbox\" />\n")
                                        dst.write(f"<div className=\"tool-details\">\n")
                                        if server_name == "python-execute":
                                            dst.write(f"```python\n{tool_call["code"]} code\n```\n")
                                        else:
                                            dst.write(f"```json arguments\n{tool_call["arguments"]}\n```\n")
                                        dst.write(f"```json error_message\n{msg['content']}\n```\n\n")
                                        dst.write(f"</div>\n")
                                    else:
                                        raise NotImplementedError(f"Unsupported tool output type: {tooloutput_type}")
                                    dst.write(f"</div>\n\n")
                                    del tool_calls[tool_call_id]
                                else:
                                    raise NotImplementedError(f"Unsupported message role: {msg['role']}")

                            dst.write(f"</Accordion>\n\n")
            
                dst.write(f"</AccordionGroup>\n")

    _tmp_path = os.path.join(os.path.dirname(__file__), "_tmp")
    try:
        os.remove(_tmp_path)
    except FileNotFoundError:
        print(f"File {_tmp_path} not found, don't need to remove")
    else:
        print(f"Removed file {_tmp_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task_dir", type=str, default="docs/tasks")
    args = parser.parse_args()
    main(args)

    print("icon_cnt", icon_cnt)