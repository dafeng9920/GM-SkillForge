#!/usr/bin/env python3
"""
Convert ChatGPT conversation JSON to Markdown format.
Usage: python scripts/chatgpt_json_to_md.py <json_file_path>
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def find_root_node(mapping):
    """Find the root node (node with no parent)."""
    for node_id, node in mapping.items():
        if node.get("parent") is None:
            return node_id
    return None


def traverse_conversation(mapping, start_id=None):
    """
    Traverse the conversation tree and return messages in order.
    """
    if start_id is None:
        start_id = find_root_node(mapping)

    if start_id is None:
        return []

    messages = []
    visited = set()

    def dfs(node_id):
        if node_id in visited or node_id not in mapping:
            return

        visited.add(node_id)
        node = mapping[node_id]

        # Get message content if exists
        if node.get("message") and node["message"].get("author"):
            msg = node["message"]
            author = msg["author"]

            # Skip hidden system messages
            metadata = msg.get("metadata", {})
            if metadata.get("is_visually_hidden_from_conversation"):
                # Still traverse children
                for child_id in node.get("children", []):
                    dfs(child_id)
                return

            content = msg.get("content", {})
            parts = content.get("parts", [])
            text_content = "\n".join(str(p) for p in parts if p).strip()

            # Only include non-empty messages
            if text_content:
                role = author.get("role", "unknown")
                role_display = {
                    "user": "User",
                    "assistant": "Assistant",
                    "system": "System",
                    "tool": "Tool"
                }.get(role, role.capitalize())

                create_time = msg.get("create_time")
                time_str = ""
                if create_time:
                    time_str = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")

                messages.append({
                    "role": role_display,
                    "content": text_content,
                    "time": time_str
                })

        # Traverse children
        for child_id in node.get("children", []):
            dfs(child_id)

    dfs(start_id)
    return messages


def is_tool_json_content(text):
    """Check if content is tool output (large JSON blocks)."""
    # Skip content that starts with large JSON or specific tool patterns
    text = text.strip()
    if text.startswith('{') or text.startswith('['):
        # If it's a large JSON block (>500 chars), it's likely tool output
        if len(text) > 500:
            return True
    return False


def json_to_markdown(json_data, skip_tool=True, skip_json_blocks=True):
    """Convert ChatGPT JSON to Markdown format."""
    title = json_data.get("title", "ChatGPT Conversation")
    create_time = json_data.get("create_time")
    update_time = json_data.get("update_time")

    md_lines = []
    md_lines.append(f"# {title}\n")

    if create_time:
        create_dt = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")
        md_lines.append(f"**Created:** {create_dt}")

    if update_time:
        update_dt = datetime.fromtimestamp(update_time).strftime("%Y-%m-%d %H:%M:%S")
        md_lines.append(f"**Updated:** {update_dt}")

    md_lines.append("\n---\n")

    mapping = json_data.get("mapping", {})
    messages = traverse_conversation(mapping)

    for msg in messages:
        # Filter messages based on options
        if skip_tool and msg['role'] == 'Tool':
            continue
        if skip_json_blocks and is_tool_json_content(msg['content']):
            continue

        md_lines.append(f"## {msg['role']}")
        if msg['time']:
            md_lines.append(f"*{msg['time']}*")
        md_lines.append("")
        md_lines.append(msg['content'])
        md_lines.append("\n---\n")

    return "\n".join(md_lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python chatgpt_json_to_md.py <json_file_path>")
        sys.exit(1)

    json_path = Path(sys.argv[1])

    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    print(f"Reading JSON file: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    print("Converting to Markdown...")
    markdown_content = json_to_markdown(json_data)

    # Generate output path
    md_path = json_path.with_suffix('.md')

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Markdown file saved to: {md_path}")
    print(f"Original size: {len(json.dumps(json_data)):,} bytes")
    print(f"Markdown size: {len(markdown_content):,} bytes")


if __name__ == '__main__':
    main()
