#!/usr/bin/env python3
"""深度提取知识星球帖子中的核心观点和方法论"""

import re

with open('zsxq_data/xiongshu_full.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Parse all posts with full content
posts = re.findall(
    r'PM熊叔\n(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\n阅读人数 (\d+)\n(.*?)(?=\nPM熊叔|$)',
    content,
    re.DOTALL
)

print(f"Total posts: {len(posts)}\n")

# Categorize posts by topic
categories = {
    'AI产品方法论': [],
    'AIGC创作': [],
    '产品增长/运营': [],
    '投资理财': [],
    '技术教程': [],
    '出海/商业化': [],
    '职场/管理': [],
    '独立开发': [],
}

for p in posts:
    date, readers, text = p
    text_lower = text.lower()

    # Categorization based on keywords
    if any(k in text for k in ['产品经理', '产品设计', '用户需求', '需求文档', '产品方法']):
        categories['AI产品方法论'].append(p)
    elif any(k in text for k in ['ComfyUI', 'Stable Diffusion', 'AIGC', 'AI生成', 'AI视频']):
        categories['AIGC创作'].append(p)
    elif any(k in text for k in ['增长', '拉新', '留存', '转化', '运营', '裂变']):
        categories['产品增长/运营'].append(p)
    elif any(k in text for k in ['投资', '股票', '美股', '理财', '赚钱', '收益']):
        categories['投资理财'].append(p)
    elif any(k in text for k in ['教程', '如何', '步骤', 'llama', '微调', '训练', '模型']):
        categories['技术教程'].append(p)
    elif any(k in text for k in ['出海', 'Stripe', 'OCBC', '变现', '付费', '商业模式']):
        categories['出海/商业化'].append(p)
    elif any(k in text for k in ['职场', '工作', '团队', '管理', '创业', '合伙人']):
        categories['职场/管理'].append(p)
    elif any(k in text for k in ['独立开发', 'SaaS', '开发者']):
        categories['独立开发'].append(p)

# Print categorized posts with content preview
for cat, cat_posts in sorted(categories.items(), key=lambda x: -len(x[1])):
    if cat_posts:
        print(f"\n{'='*60}")
        print(f"【{cat}】({len(cat_posts)} posts)")
        print('='*60)

        for i, p in enumerate(cat_posts[:5]):  # Show top 5 per category
            date, readers, text = p
            # Clean text - remove UI elements
            lines = [l for l in text.split('\n') if l.strip() and '收进专栏' not in l and '阅读人数' not in l and '查看详情' not in l]
            preview = '\n'.join(lines)[:400]
            print(f"\n--- {date} ({readers} readers) ---")
            print(preview[:300] + "..." if len(preview) > 300 else preview)