import sys
sys.path.append('scripts')
from delete_all_my_messages import scan_local_export

def main():
    groups = scan_local_export('inbox/result.json')
    class_groups = [g for g in groups if g['category'] == 'class']
    
    # Sort by message count descending
    class_groups.sort(key=lambda x: len(x['message_ids']), reverse=True)
    
    print(f"\n=================== CLASS GROUPS LIST ({len(class_groups)} groups) ===================")
    print(f"{'#':<4} | {'Group Name':<50} | {'Messages':<8} | {'Group ID':<12}")
    print("-" * 80)
    for idx, g in enumerate(class_groups):
        name = g['name']
        if len(name) > 47:
            name = name[:44] + "..."
        print(f"{idx+1:<4} | {name:<50} | {len(g['message_ids']):<8} | {g['id']:<12}")
    print("-" * 80)

if __name__ == '__main__':
    main()
