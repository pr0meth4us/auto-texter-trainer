import argparse
import json
import os
import sys
from pathlib import Path

# Add chat-analysis to Python path dynamically
CHAT_ANALYSIS_PATH = "/Users/nicksng/code/chat-analysis"
if CHAT_ANALYSIS_PATH not in sys.path:
    sys.path.append(CHAT_ANALYSIS_PATH)

try:
    from api.parsers.main_parser import process_single_file, deduplicate_and_sort_messages
except ImportError as e:
    print(f"Error importing from chat-analysis: {e}")
    sys.exit(1)


def custom_json_extract(file_path):
    """
    Fallback extractor for Telegram result.json, Instagram message_1.json,
    and custom data.js format. Returns a list of chats, where each chat is a list of chronological messages.
    """
    try:
        content = None
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if str(file_path).endswith('.js'):
            # Strip variable assignment like `const CHAT_DATA = `
            if '=' in content:
                content = content[content.index('=')+1:].strip()
                if content.endswith(';'):
                    content = content[:-1]
                    
        data = json.loads(content)
        chats = []
        
        # Telegram format
        if isinstance(data, dict) and 'chats' in data and 'list' in data['chats']:
            for chat in data['chats']['list']:
                chat_messages = []
                for msg in chat.get('messages', []):
                    if msg.get('type') == 'message' and isinstance(msg.get('text'), str) and msg.get('text') and msg.get('from'):
                        chat_messages.append({'timestamp': msg.get('date', ''), 'sender': msg['from'], 'message': msg['text']})
                if chat_messages:
                    chats.append(chat_messages)
            return chats
        
        # Instagram format
        if isinstance(data, dict) and 'messages' in data:
            chat_messages = []
            for msg in data['messages']:
                sender = msg.get('sender_name')
                text = msg.get('content')
                if sender and text:
                    chat_messages.append({'timestamp': str(msg.get('timestamp_ms', '')), 'sender': sender, 'message': text})
            if chat_messages:
                chats.append(chat_messages[::-1])
            return chats
            
        # JS Array format
        if isinstance(data, list):
            chat_messages = []
            for msg in data:
                sender = msg.get('sender')
                text = msg.get('message')
                if sender and text:
                    chat_messages.append({'timestamp': msg.get('timestamp', ''), 'sender': sender, 'message': text})
            if chat_messages:
                chats.append(chat_messages)
            return chats
            
    except Exception as e:
        pass
    return None


def generate_training_data(messages: list, assistant_username: str = None, context_window: int = 2):
    """
    Converts a chronological list of parsed messages into User/Assistant pairs.
    If assistant_username is None, everyone's text is treated as training data!
    """
    dataset = []
    
    for i, msg in enumerate(messages):
        sender = msg.get('sender')
        text = msg.get('message')
        
        if not sender or not text:
            continue
            
        # If a specific username is provided, only learn from them. 
        # Otherwise, learn from EVERYONE.
        if assistant_username is None or sender.lower() == assistant_username.lower():
            start_idx = max(0, i - context_window)
            context_msgs = messages[start_idx:i]
            
            # Avoid using their own previous message as context
            if context_msgs and context_msgs[-1].get('sender') == sender:
                continue
                
            context_str = " | ".join([
                f"{m.get('message')}" 
                for m in context_msgs if m.get('message')
            ])
            
            if not context_str:
                continue
                
            dataset.append({
                "messages": [
                    {"role": "system", "content": "You are a casual, bilingual Gen-Z Cambodian (Khmer) automated texting assistant. You are completely fluent in English, but you frequently mix in \"Latinized Khmer\". ALWAYS use all lowercase letters. Do not use punctuation like periods. Output ONLY the raw text of your reply."},
                    {"role": "user", "content": f"Context: {context_str}"},
                    {"role": "assistant", "content": text.lower()}
                ]
            })
            
    return dataset


def main():
    parser = argparse.ArgumentParser(description="Generate Auto-Texter Training Data from raw chats")
    parser.add_argument("--input", type=str, required=True, help="Path to raw chat HTML/JSON/JS export or directory")
    parser.add_argument("--output", type=str, default="dataset.jsonl", help="Output JSONL file")
    parser.add_argument("--username", type=str, default=None, help="Specific sender name. If omitted, uses everyone's messages.")
    parser.add_argument("--context", type=int, default=2, help="Number of previous messages to include as context")
    
    args = parser.parse_args()
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Path {input_path} does not exist.")
        sys.exit(1)
        
    files_to_process = []
    if input_path.is_file():
        files_to_process.append(input_path)
    elif input_path.is_dir():
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.endswith('.json') or file.endswith('.js') or file.endswith('.html'):
                    files_to_process.append(Path(root) / file)
                    
    all_chats = []
    for fp in files_to_process:
        print(f"Processing {fp}...")
        parsed_chats = custom_json_extract(fp)
        
        if not parsed_chats:
            seen_hashes = set()
            try:
                with open(fp, 'rb') as f:
                    parsed_msgs = process_single_file(f, seen_hashes)
                    if parsed_msgs:
                        all_chats.append(parsed_msgs)
            except Exception as e:
                pass
        else:
            all_chats.extend(parsed_chats)
            
    if not all_chats:
        print("No messages extracted. Ensure it's a supported chat export format.")
        sys.exit(1)
        
    total_messages = sum(len(chat) for chat in all_chats)
    print(f"Extracted {total_messages} messages across {len(all_chats)} chats. Formatting...")
    
    if args.username:
        print(f"Learning only from '{args.username}'...")
    else:
        print("Learning from EVERYONE in the chat log...")
        
    dataset = []
    for chat in all_chats:
        dataset.extend(generate_training_data(chat, args.username, args.context))
    
    out_path = Path(args.output)
    with open(out_path, 'w', encoding='utf-8') as out_f:
        for item in dataset:
            out_f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"Done! Generated {len(dataset)} training examples and saved to {out_path}.")
    if dataset:
        print("Example generated row:")
        print(json.dumps(dataset[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
