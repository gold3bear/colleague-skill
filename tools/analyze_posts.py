#!/usr/bin/env python3
"""分析知识星球帖子数据质量"""

import re

with open('zsxq_data/xiongshu_full.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Find posts with 展开全部 and see what comes after
parts = content.split('展开全部')
print(f'Total 展开全部 occurrences: {len(parts)-1}')

# Check last 100 chars before 展开全部 to see if content is cut off
truncated_count = 0
complete_count = 0
truncation_indicators = ['在', '的', '了', '是', '和', '也', '就', '都', '而', '着', '但', '这']

for i, part in enumerate(parts[:-1]):  # skip last part (after last 展开全部)
    last_chars = part[-100:].strip()
    # Check if it looks like a complete thought (ends with punctuation) or cut off
    if last_chars.endswith(('。', '！', '？', '»', '"', '」', '』', '.', '!', '?')):
        complete_count += 1
    else:
        # Check if the last word/character suggests it was cut mid-sentence
        last_word = last_chars.split()[-1] if last_chars.split() else ''
        if last_word in truncation_indicators:
            truncated_count += 1
            if truncated_count <= 5:
                print(f'\n[Possibly truncated sample {truncated_count}]:')
                print(f'...{part[-120:]}')
        else:
            complete_count += 1

print(f'\nPosts ending with complete sentence: {complete_count}')
print(f'Posts that appear possibly truncated: {truncated_count}')

# Let's also check a few posts that DON'T have 展开全部 to compare
print('\n\n=== Sample posts WITHOUT 展开全部 ===')
posts_no_expand = re.findall(
    r'PM熊叔\n(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\n阅读人数 (\d+)\n(.*?)(?=\nPM熊叔|$)',
    content,
    re.DOTALL
)
for p in posts_no_expand[:3]:
    print(f'\nDate: {p[0]}, Readers: {p[1]}')
    print(f'Content: {p[2][:300]}...' if len(p[2]) > 300 else f'Content: {p[2]}')