import json
import os
import sys

log_path = r"C:\Users\Jahanzaib Ahmad CS06\.gemini\antigravity-ide\brain\131ef5d4-273d-4f16-98b2-cd997ad1ebed\.system_generated\logs\transcript.jsonl"
out_dir = r"f:\.Hackathon\0.GeoFarmer\backend"

if not os.path.exists(log_path):
    print("Log file not found.")
    exit(1)

target_steps = [4305, 4518, 4524, 4530, 4536, 4548, 4745, 4833, 4998, 5000]

extracted = {}

with open(log_path, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        try:
            data = json.loads(line)
            step_idx = data.get("step_index")
            if step_idx in target_steps:
                tool_calls = data.get("tool_calls", [])
                for tc in tool_calls:
                    name = tc.get("name")
                    args = tc.get("args", {})
                    # Save to file
                    out_file = os.path.join(out_dir, f"step_{step_idx}_{name}.txt")
                    with open(out_file, 'w', encoding='utf-8') as out_f:
                        out_f.write(json.dumps(args, indent=2))
                    print(f"Extracted Step {step_idx} | Tool {name} to {out_file}")
        except Exception as e:
            pass
