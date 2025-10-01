import argparse
from ast import arguments, literal_eval
import os
from tqdm import tqdm
import json
import re
from icon import icon_map

icon_cnt = len(icon_map)

if "web_search" in icon_map:
    icon_map["googlesearch"] = icon_map["web_search"]
if "playwright_with_chunk" in icon_map:
    icon_map["playwright"] = icon_map["playwright_with_chunk"]


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
        34, 37, 10, 38, 39, 49, 125, 149, 161, 162, 165, 183, 188, 189, 190, 196, 197, 306, 404,
        16, 78, 133, 155, 156, 159, 169, 181, 182, 201, 209, 210, 313, 316, 319, 351, 371,
        126, 141, 143, 179, 223, 267, 275, 284, 345, 352,
        23, 24, 108, 109, 116, 127, 131, 142, 144, 147, 150, 163, 235, 237, 292, 327, 331, 368
    }

    task_dir = args.task_dir

    clear(task_dir)

    mdx_files = find_mdx_files_with_underscore(task_dir)
    for f in tqdm(mdx_files):
        f_prefix = f.replace("_.mdx", "")
        task_id = int(f_prefix.split("/")[-1])
        
        target_md = f_prefix + ".mdx"

        with open(f, "r", encoding="utf-8") as src, open(target_md, "w", encoding="utf-8") as dst:
            dst.write(src.read())

            log_dir = f_prefix + "/"

            if os.path.exists(log_dir) and len(os.listdir(log_dir)) > 0 and task_id in checked_tasks:
            # if os.path.exists(log_dir) and len(os.listdir(log_dir)) > 0:
                dst.write(f"\n<AccordionGroup>\n")

                for log_file in sorted(os.listdir(log_dir)):
                    if log_file.endswith(".json"):
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

                            for msg in msgs:
                                if msg["role"] == "user":
                                    continue
                                elif msg["role"] == "assistant":
                                    if "tool_calls" in msg:
                                        if not (msg["content"] == "" or msg["content"] is None or msg["content"] == "null"):
                                            dst.write(f"<div className=\"thinking-box\">\n")
                                            dst.write(f"🧐`Agent`\n\n{msg['content'].strip().replace("$", "")}\n</div>\n\n")

                                        for msg_tool_call in msg["tool_calls"]:
                                            if msg_tool_call['type'] == "function":
                                                if msg_tool_call['function']['name'] == "local-python-execute":
                                                    dst.write(f"<div className=\"tool-call-box\">\n")
                                                    dst.write(f"{icon_map["python-execute"]} `python-execute`\n\n")
                                                    # dst.write(f"🛠 `python-execute`\n\n")
                                                    try:
                                                        arg_s = json.loads(msg_tool_call['function']['arguments'])
                                                    except:
                                                        print("aaa")
                                                        arg_s = msg_tool_call['function']['arguments']
                                                    dst.write(f"```python {arg_s['filename'] if 'filename' in arg_s else ''}\n")
                                                    try:
                                                        code = arg_s['code']
                                                    except:
                                                        code = arg_s
                                                    dst.write(f"{code if 'code' in arg_s else ''}\n")
                                                    dst.write(f"```\n")
                                                    dst.write(f"</div>\n\n")
                                                elif "overlong" in msg_tool_call['function']['name']:
                                                    dst.write(f"<div className=\"tool-call-box\">\n")
                                                    dst.write(f"{icon_map['overlong_tool_output']} `{msg_tool_call['function']['name'].replace("local-", "").replace("tooloutput", "tool_output")}`\n\n")
                                                    dst.write(f"```json\n")
                                                    argu_s = msg_tool_call['function']['arguments'].strip()[1:-1].split(",")
                                                    dst.write("{\n")
                                                    for i, arg in enumerate(argu_s):
                                                        if i == 0:
                                                            dst.write(f"\t{arg}")
                                                        else:
                                                            dst.write(f",\n\t{arg}")
                                                    dst.write("\n}\n")
                                                    dst.write(f"```\n")
                                                    dst.write(f"</div>\n\n")
                                                elif msg_tool_call['function']['name'] == "filesystem-write_file":
                                                    arg_s = json.loads(msg_tool_call['function']['arguments'])
                                                    dst.write(f"<div className=\"tool-call-box\">\n")
                                                    dst.write(f"{icon_map['filesystem']} `{msg_tool_call['function']['name']}`\n\n")
                                                    # dst.write(f"🛠 `{msg_tool_call['function']['name']}`\n\n")
                                                    dst.write(f"```text workspace/{arg_s['path'].split('/')[-1].replace("@", "@")}\n")
                                                    dst.write(f"{arg_s['content'].replace("```", "`*3")}\n")
                                                    dst.write(f"```\n")
                                                    dst.write(f"</div>\n\n")
                                                else:
                                                    dst.write(f"<div className=\"tool-call-box\">\n")
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
                                                    dst.write(f"{icon_map[server_name]} `{server_name} {function_name}`\n\n" if server_name in icon_map else f"🛠 `{server_name} {function_name}`\n\n")
                                                    # dst.write(f"🛠 `{server_name} {function_name}`\n\n")
                                                    dst.write(f"```json\n")
                                                    argu_s = msg_tool_call['function']['arguments'].strip()[1:-1].split(",")
                                                    if len(argu_s) == 1 and argu_s[0] == "":
                                                        dst.write("{}\n")
                                                    else:
                                                        dst.write("{\n")
                                                        for i, arg in enumerate(argu_s):
                                                            if i == 0:
                                                                dst.write(f"\t{arg.replace("@", "@")}")
                                                            else:
                                                                dst.write(f",\n\t{arg.replace("@", "@")}")
                                                        dst.write("\n}\n")
                                                    dst.write(f"```\n")
                                                    dst.write(f"</div>\n\n")
                                            else:
                                                raise NotImplementedError(f"Unsupported tool call type: {msg_tool_call['type']}")
                                    else:
                                        dst.write(f"<div className=\"thinking-box\">\n")
                                        dst.write(f"🧐`Agent`\n\n{msg['content'].strip()}\n</div>\n\n")
                                elif msg["role"] == "tool":
                                    if msg['content'] is not None:
                                        try:
                                            # tool_res.replace(r'\"', r'"')
                                            # tool_res.replace(r'\\n', r'\n')
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

                                        # def replace_angle_brackets(s):
                                        #     return re.sub(r'<(.*?)>', r'《\1》', s)
                                        # tool_res = replace_angle_brackets(tool_res)
                                        # tool_res = tool_res.replace('@', '@')
                                        # tool_res = tool_res.replace('{', r'\{')
                                        # tool_res = tool_res.replace('}', r'\}')
                                        # tool_res = tool_res.replace('<', r'\<')
                                        # tool_res = tool_res.replace('>', r'\>')
                                        dst.write(f"<div className=\"result-box\">\n")
                                        dst.write(f"🔍`tool result`\n```json\n{tool_res.replace("$", "")}\n```\n</div>\n\n")
                                    else:
                                        raise NotImplementedError("tool result doesn't have content")
                                        # dst.write(f"<div className=\"result-box\">\n")
                                        # dst.write("🔍`tool result`\n```json\n{}\n```\n</div>\n\n")
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