import json
import argparse
import os
import csv
import sys

def list_groups(file_path, show_left=False, output_format='table', output_file=None):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"Loading {file_path} (this may take a few seconds)...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Helper to check if a chat is a group
    def is_group(chat):
        chat_type = str(chat.get('type', '')).lower()
        # Usually Telegram types: private_group, private_supergroup, public_group, public_supergroup.
        # We check if 'group' is in the type and it's not a personal chat/saved messages
        return 'group' in chat_type or chat_type in ['supergroup', 'group']

    groups = []

    # Get active chats
    active_chats = data.get('chats', {}).get('list', [])
    for chat in active_chats:
        if is_group(chat):
            groups.append({
                'name': chat.get('name') or '<Unnamed Group>',
                'type': chat.get('type'),
                'id': chat.get('id'),
                'messages_count': len(chat.get('messages', [])),
                'status': 'active'
            })

    # Get left chats if requested or by default include them with a tag
    left_chats = data.get('left_chats', {}).get('list', [])
    for chat in left_chats:
        if is_group(chat):
            groups.append({
                'name': chat.get('name') or '<Unnamed Group>',
                'type': chat.get('type'),
                'id': chat.get('id'),
                'messages_count': len(chat.get('messages', [])),
                'status': 'left'
            })

    # Filter out left chats if show_left is False
    if not show_left:
        groups = [g for g in groups if g['status'] == 'active']

    print(f"Found {len(groups)} group chats.")

    if output_format == 'csv':
        if output_file:
            write_csv(groups, output_file)
        else:
            # Print as CSV to stdout
            writer = csv.writer(sys.stdout)
            writer.writerow(['Name', 'ID', 'Type', 'Status', 'Messages Count'])
            for g in groups:
                writer.writerow([g['name'], g['id'], g['type'], g['status'], g['messages_count']])
    elif output_format == 'json':
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as out:
                json.dump(groups, out, indent=2, ensure_ascii=False)
            print(f"Saved JSON to {output_file}")
        else:
            print(json.dumps(groups, indent=2, ensure_ascii=False))
    else:
        # Table format
        header = f"{'Group Name':<50} | {'Type':<20} | {'ID':<15} | {'Status':<8} | {'Messages':<8}"
        separator = "-" * len(header)
        
        print("\n" + header)
        print(separator)
        for g in groups:
            name = g['name']
            if len(name) > 47:
                name = name[:44] + "..."
            print(f"{name:<50} | {g['type']:<20} | {str(g['id']):<15} | {g['status']:<8} | {g['messages_count']:<8}")
        print(separator)

        if output_file:
            # If output file specified for table format, write it
            with open(output_file, 'w', encoding='utf-8') as out:
                out.write(header + "\n" + separator + "\n")
                for g in groups:
                    name = g['name']
                    out.write(f"{name:<50} | {g['type']:<20} | {str(g['id']):<15} | {g['status']:<8} | {g['messages_count']:<8}\n")
                out.write(separator + "\n")
            print(f"Saved table to {output_file}")

def write_csv(groups, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'ID', 'Type', 'Status', 'Messages Count'])
        for g in groups:
            writer.writerow([g['name'], g['id'], g['type'], g['status'], g['messages_count']])
    print(f"Saved CSV to {file_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="List groups in Telegram export JSON.")
    parser.add_argument('--file', default='inbox/result.json', help="Path to result.json")
    parser.add_argument('--show-left', action='store_true', help="Include groups you have left")
    parser.add_argument('--format', choices=['table', 'csv', 'json'], default='table', help="Output format")
    parser.add_argument('--output', help="File to save output to")

    args = parser.parse_args()
    list_groups(args.file, args.show_left, args.format, args.output)
