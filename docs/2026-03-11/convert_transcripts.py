import json
import os
import sys

def convert_jsonl_to_md(jsonl_path, md_path):
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Session Transcript: {os.path.basename(jsonl_path)}\n\n")
        
        for line in lines:
            try:
                data = json.loads(line)
                
                if data['type'] == 'session':
                    f.write(f"**Session ID**: `{data['id']}`  \n")
                    f.write(f"**Start Time**: {data['timestamp']}  \n")
                    f.write(f"**CWD**: `{data['cwd']}`\n\n---\n\n")
                
                elif data['type'] == 'message':
                    role = data['message']['role']
                    content_list = data['message']['content']
                    
                    f.write(f"### {role.upper()} ({data['timestamp']})\n\n")
                    
                    for part in content_list:
                        if part['type'] == 'text':
                            f.write(part['text'] + "\n\n")
                        elif part['type'] == 'thinking':
                            f.write("> **Thinking**:\n> " + part['thinking'].replace('\n', '\n> ') + "\n\n")
                        elif part['type'] == 'toolCall':
                            f.write(f"🛠️ **Tool Call**: `{part['name']}`\n")
                            f.write("```json\n" + json.dumps(part['arguments'], indent=2, ensure_ascii=False) + "\n```\n\n")
                        elif part['type'] == 'toolResult':
                            f.write("✅ **Tool Result**:\n")
                            for res in part['content']:
                                if res['type'] == 'text':
                                    f.write(res['text'] + "\n\n")
                                else:
                                    f.write("*(Binary or complex output)*\n\n")
                
            except Exception as e:
                f.write(f"\n> [!ERROR] Failed to parse line: {e}\n\n")

def batch_convert(source_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for filename in os.listdir(source_dir):
        if filename.endswith(".jsonl") or ".jsonl" in filename:
            source_path = os.path.join(source_dir, filename)
            output_filename = filename.replace(".jsonl", ".md")
            output_path = os.path.join(output_dir, output_filename)
            
            print(f"Converting {filename}...")
            convert_jsonl_to_md(source_path, output_path)

if __name__ == "__main__":
    src = r"d:\GM-SkillForge\docs\2026-03-11\orphan_transcripts"
    out = r"d:\GM-SkillForge\docs\2026-03-11\orphan_transcripts_md"
    batch_convert(src, out)
    print("Done!")
