import json
import os
from pathlib import Path

def main():
    input_path = "/Users/nicksng/code/chat-analysis/data/texts/special/message_1.json"
    output_path = "/Users/nicksng/code/auto-texter-trainer/data/dataset_smt_vertex.jsonl"
    
    print(f"Loading {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    messages = data.get("messages", [])
    # Instagram messages are usually newest-first, we need chronological
    messages.reverse()
    
    dataset = []
    context_window = 2
    
    system_instruction = {
        "role": "system",
        "parts": [{"text": "You are a casual, bilingual Gen-Z Cambodian (Khmer) automated texting assistant. You are completely fluent in English, but you frequently mix in \"Latinized Khmer\". ALWAYS use all lowercase letters. Do not use punctuation like periods. Output ONLY the raw text of your reply."}]
    }

    for i, msg in enumerate(messages):
        sender = msg.get('sender_name')
        text = msg.get('content')
        
        if not sender or not text or len(text.strip()) == 0:
            continue
            
        if sender == "smt":
            start_idx = max(0, i - context_window)
            context_msgs = messages[start_idx:i]
            
            if context_msgs and context_msgs[-1].get('sender_name') == sender:
                continue # Skip if she's just replying to herself in a burst
                
            context_str = " | ".join([
                f"{m.get('content')}" 
                for m in context_msgs if m.get('content')
            ])
            
            if not context_str:
                continue
                
            dataset_row = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"Context: {context_str}"}]
                    },
                    {
                        "role": "model",
                        "parts": [{"text": text.lower()}]
                    }
                ],
                "systemInstruction": system_instruction
            }
            dataset.append(dataset_row)
            
    print(f"Extracted {len(dataset)} examples for 'smt'.")
    
    # Cap to 10k messages max for time and cost
    if len(dataset) > 10000:
        dataset = dataset[:10000]
        print(f"Capped to 10000 examples.")

    with open(output_path, 'w', encoding='utf-8') as out_f:
        for item in dataset:
            out_f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"Dataset saved to {output_path}")

if __name__ == "__main__":
    main()
