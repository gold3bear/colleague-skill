#!/usr/bin/env python3
"""从知识星球帖子中提取核心观点和产品方法论"""

import re
import json
from collections import defaultdict

with open('zsxq_data/xiongshu_full.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Parse all posts
posts = re.findall(
    r'PM熊叔\n(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\n阅读人数 (\d+)\n(.*?)(?=\nPM熊叔|$)',
    content,
    re.DOTALL
)

print(f"Total posts parsed: {len(posts)}\n")

# Extract topics/themes from post titles (usually first line after date)
topics = []
for p in posts:
    first_line = p[2].strip().split('\n')[0]
    if len(first_line) < 50:  # Likely a title
        topics.append(first_line)

# Group posts by year-month
posts_by_month = defaultdict(list)
for p in posts:
    date = p[0][:7]  # YYYY-MM
    posts_by_month[date].append(p)

print("=== Posts by Month ===")
for month in sorted(posts_by_month.keys(), reverse=True)[:12]:
    print(f"{month}: {len(posts_by_month[month])} posts")

# Extract key phrases and patterns
print("\n=== Content Analysis ===")

# Common keywords
all_text = '\n'.join(p[2] for p in posts)

# Count important terms
terms = {
    'AI': all_text.count('AI') + all_text.count('人工智能'),
    '产品': all_text.count('产品'),
    '用户': all_text.count('用户'),
    '数据': all_text.count('数据'),
    '增长': all_text.count('增长'),
    '变现': all_text.count('变现'),
    '社区': all_text.count('社区'),
    '创作者': all_text.count('创作者'),
    'AIGC': all_text.count('AIGC'),
    'ComfyUI': all_text.count('ComfyUI'),
    '投资': all_text.count('投资'),
    '变现': all_text.count('变现'),
}

print("Keyword frequency:")
for term, count in sorted(terms.items(), key=lambda x: -x[1]):
    print(f"  {term}: {count}")

# Extract potential frameworks/principles
print("\n=== Potential Frameworks/Principles ===")

# Look for numbered lists (1. 2. 3. or 第一 第二 第三)
numbered_patterns = re.findall(r'(\d+[.、]\s*[^\n]+)', all_text)
print(f"Numbered items found: {len(numbered_patterns)}")

# Look for section headers (## or 【】)
headers = re.findall(r'(#{1,3}\s+[^\n]+|【[^】]+】)', all_text)
print(f"Section headers found: {len(headers)}")
for h in headers[:20]:
    print(f"  {h}")

# Extract quotes (things that look like principles)
print("\n=== Key Insights (first 20 posts) ===")
for i, p in enumerate(posts[:20]):
    content = p[2][:300].strip()
    print(f"\n[{p[0]}] ({p[1]} readers)")
    print(f"  {content[:200]}...")