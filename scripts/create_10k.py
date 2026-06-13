with open('../data/raw_history.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Each conversation is exactly 3 lines (Context, Reply, ---)
# So 10,000 conversations is 30,000 lines.
subset_lines = lines[:30000]

with open('../data/subset_10k.txt', 'w', encoding='utf-8') as f:
    f.writelines(subset_lines)

print(f"Created subset_10k.txt with {len(subset_lines)//3} conversations.")
