import json
import sys
from datetime import datetime


def extract_text(message):
    """提取 message 中的文本内容"""
    if not message:
        return ""

    content = message.get("content")
    if not content:
        return ""

    parts = content.get("parts")
    if not parts:
        return ""

    return "\n".join(parts)


def find_root(mapping):
    """找到 root 节点"""
    for node_id, node in mapping.items():
        if node.get("parent") is None:
            return node_id
    return None


def traverse(mapping, node_id, output_lines):
    """递归遍历对话树"""
    node = mapping[node_id]
    message = node.get("message")

    if message:
        role = message.get("author", {}).get("role", "unknown")
        text = extract_text(message)

        if text.strip():
            if role == "user":
                output_lines.append("## 🧑 User\n")
            elif role == "assistant":
                output_lines.append("## 🤖 Assistant\n")
            else:
                output_lines.append(f"## {role}\n")

            output_lines.append(text.strip())
            output_lines.append("\n---\n")

    for child_id in node.get("children", []):
        traverse(mapping, child_id, output_lines)


def convert(json_path, output_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title", "ChatGPT Conversation")
    create_time = data.get("create_time")

    mapping = data["mapping"]
    root_id = find_root(mapping)

    if not root_id:
        print("❌ 未找到 root 节点")
        return

    output_lines = []

    output_lines.append(f"# {title}\n")

    if create_time:
        dt = datetime.fromtimestamp(create_time)
        output_lines.append(f"> Created at: {dt}\n")

    output_lines.append("\n---\n")

    traverse(mapping, root_id, output_lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"✅ 转换完成: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python chat_to_md.py input.json output.md")
    else:
        convert(sys.argv[1], sys.argv[2])
