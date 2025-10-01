import os
import json


trajs = {
    "claude4-sonnet": "trajs/claude-4-sonnet-0514_09210140_1/finalpool",
    # "gemini-2.5-pro": "trajs/gemini-2.5-pro_09210140_1/finalpool",
    # "grok-4": "trajs/grok-4_09210140_1/finalpool",
}


with open("map.txt", "r") as f:
    for line in f:
        task_name, task_id, category = line.strip().split()

        os.makedirs(os.path.join("docs", "tasks", category, task_id), exist_ok=True)
        target_log_path = os.path.join("docs", "tasks", category, task_id)
        for filename in os.listdir(target_log_path):
            file_path = os.path.join(target_log_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        

        for k, v in trajs.items():
            traj_log_path = os.path.join(v, task_name, "traj_log.json")
            traj_eval_res_path = os.path.join(v, task_name, "eval_res.json")
            try:
                with open(traj_log_path, "r") as f_log:
                    traj_log = json.load(f_log)
                with open(traj_eval_res_path, "r") as f_eval:
                    traj_eval_res = json.load(f_eval)
                traj_log["pass"] = traj_eval_res["pass"]
                with open(os.path.join(target_log_path, f"{k}.json"), "w") as f_log:
                    json.dump(traj_log, f_log)
            except FileNotFoundError:
                print(f"File not found: {traj_log_path}")
