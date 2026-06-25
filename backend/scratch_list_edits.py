import json
import os

log_path = r"C:\Users\Jahanzaib Ahmad CS06\.gemini\antigravity-ide\brain\131ef5d4-273d-4f16-98b2-cd997ad1ebed\.system_generated\logs\transcript.jsonl"

if not os.path.exists(log_path):
    print("Log file not found.")
    exit(1)

with open(log_path, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        try:
            data = json.loads(line)
            step_idx = data.get("step_index")
            source = data.get("source")
            step_type = data.get("type")
            
            # Check if this is a tool call modifying main.dart
            tool_calls = data.get("tool_calls", [])
            for tc in tool_calls:
                name = tc.get("name")
                args = tc.get("args", {})
                if name in ["write_to_file", "replace_file_content", "multi_replace_file_content"]:
                    target = args.get("TargetFile", "")
                    if "main.dart" in target:
                        desc = args.get("Description", "") or tc.get("toolAction", "")
                        print(f"Line {line_num} | Step {step_idx} | Tool {name} | Desc: {desc[:80]}")
        except Exception as e:
            pass
