#!/usr/bin/env python3
"""批量采集简书文章"""

import json
import time
import re
import os
from datetime import datetime

# All 18 article URLs
ARTICLE_URLS = [
    "https://www.jianshu.com/p/beeeceb21afd",
    "https://www.jianshu.com/p/2dcf7fb04a85",
    "https://www.jianshu.com/p/2ebc018fe5a9",
    "https://www.jianshu.com/p/c383bfc700a2",
    "https://www.jianshu.com/p/ae3ce66a31cb",
    "https://www.jianshu.com/p/d56e71fd6106",
    "https://www.jianshu.com/p/1515e0bfb8b6",
    "https://www.jianshu.com/p/c5c636e6b1e2",
    "https://www.jianshu.com/p/e783a5b8ea4f",
    "https://www.jianshu.com/p/79660a483037",
    "https://www.jianshu.com/p/668c3cf93e78",
    "https://www.jianshu.com/p/4ba4e794c8c3",
    "https://www.jianshu.com/p/f42a1dd08649",
    "https://www.jianshu.com/p/a89b77c41d14",
    "https://www.jianshu.com/p/25de2036fcfe",
    "https://www.jianshu.com/p/9f695468358e",
    "https://www.jianshu.com/p/0423da87d52c",
    "https://www.jianshu.com/p/0dda86859812",
]

def extract_article_content(html, url):
    """从HTML中提取文章内容"""
    # 提取标题
    title_match = re.search(r'<h1[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<title>(.*?)</title>', html)
    title = title_match.group(1).strip() if title_match else url

    # 提取日期
    date_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', html)
    date = date_match.group(1) if date_match else ""

    # 提取正文内容
    content_match = re.search(r'<div[^>]*class="[^"]*show-content[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    if content_match:
        content_html = content_match.group(1)
        # 去除HTML标签
        content = re.sub(r'<[^>]+>', '', content_html)
        content = re.sub(r'\s+', '\n', content).strip()
    else:
        content = ""

    return {
        "title": title,
        "url": url,
        "date": date,
        "content": content
    }

def save_articles(articles):
    """保存文章"""
    os.makedirs('zsxq_data/jianshu', exist_ok=True)

    with open('zsxq_data/jianshu/articles_full.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    with open('zsxq_data/jianshu/articles_full.md', 'w', encoding='utf-8') as f:
        f.write("# 简书文章集 - PM熊叔（完整版）\n\n")
        f.write(f"来源: https://www.jianshu.com/u/eb4f5b877526\n")
        f.write(f"采集时间: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"文章数量: {len(articles)}\n\n")
        f.write("---\n\n")
        for i, a in enumerate(articles):
            f.write(f"## {i+1}. {a['title']}\n\n")
            f.write(f"日期: {a['date']}\n\n")
            f.write(f"链接: {a['url']}\n\n")
            f.write(f"内容:\n{a['content']}\n\n")
            f.write("---\n\n")

    print(f"已保存 {len(articles)} 篇文章")

if __name__ == "__main__":
    # 需要手动使用Playwright采集HTML
    print("请使用 Playwright 访问每篇文章并复制HTML内容")
    print("或使用 batch_scrape_jianshu.js 在浏览器控制台执行")
