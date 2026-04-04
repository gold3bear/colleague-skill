#!/usr/bin/env python3
"""
知识星球浏览器抓取器（Playwright 方案）

复用本机 Chrome 登录态，自动采集知识星球帖子数据。

用法：
  python3 zsxq_browser.py --group-id 141415518852 --limit 100 --output ./zsxq_data
"""

import sys
import time
import json
import argparse
import platform
import os
from pathlib import Path
from datetime import datetime


def get_default_chrome_profile():
    """根据操作系统返回 Chrome 默认 Profile 路径"""
    system = platform.system()
    if system == "Darwin":
        return str(Path.home() / "Library/Application Support/Google/Chrome/Default")
    elif system == "Linux":
        return str(Path.home() / ".config/google-chrome/Default")
    elif system == "Windows":
        return str(Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/User Data/Default")
    return str(Path.home() / ".config/google-chrome/Default")


def make_context(playwright, chrome_profile, headless=False):
    """创建复用登录态的浏览器上下文"""
    return playwright.chromium.launch_persistent_context(
        chrome_profile,
        headless=headless,
        viewport={"width": 1280, "height": 720},
    )


def parse_posts(page, group_id):
    """解析当前页面的帖子列表"""
    posts = []

    # 等待帖子加载
    page.wait_for_selector(".posts-item", timeout=10000)

    items = page.query_selector_all(".posts-item")
    for item in items:
        try:
            post = {}

            # 提取标题/内容
            content_el = item.query_selector(".content")
            if content_el:
                post["content"] = content_el.inner_text()[:500]

            # 提取作者
            author_el = item.query_selector(".author-name")
            if author_el:
                post["author"] = author_el.inner_text()

            # 提取时间
            time_el = item.query_selector(".time")
            if time_el:
                post["time"] = time_el.inner_text()

            # 提取评论数
            comment_el = item.query_selector(".comment-count")
            if comment_el:
                post["comments"] = comment_el.inner_text()

            # 提取点赞数
            like_el = item.query_selector(".like-count")
            if like_el:
                post["likes"] = like_el.inner_text()

            if post.get("content"):
                posts.append(post)
        except Exception as e:
            print(f"解析帖子失败: {e}")
            continue

    return posts


def scroll_and_collect(page, group_id, limit=100):
    """滚动页面并收集帖子"""
    all_posts = []
    seen_contents = set()

    last_height = 0
    scroll_attempts = 0
    max_scroll_attempts = 50

    while len(all_posts) < limit and scroll_attempts < max_scroll_attempts:
        # 解析当前可见帖子
        posts = parse_posts(page, group_id)
        for post in posts:
            content_preview = post.get("content", "")[:100]
            if content_preview and content_preview not in seen_contents:
                seen_contents.add(content_preview)
                all_posts.append(post)
                print(f"  已采集: {post.get('author', '未知')} - {post.get('content', '')[:50]}...")

        if len(all_posts) >= limit:
            break

        # 滚动页面
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.5)

        # 检查是否到底
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
            last_height = new_height

        print(f"  滚动加载... 当前 {len(all_posts)} 条")

    return all_posts[:limit]


def main():
    parser = argparse.ArgumentParser(description="知识星球浏览器抓取器")
    parser.add_argument("--group-id", required=True, help="知识星球 Group ID")
    parser.add_argument("--limit", type=int, default=100, help="采集数量")
    parser.add_argument("--output", default="./zsxq_data", help="输出目录")
    parser.add_argument("--headless", action="store_true", help="无头模式")
    args = parser.parse_args()

    # 启动浏览器
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        chrome_profile = get_default_chrome_profile()
        print(f"使用 Chrome Profile: {chrome_profile}")

        context = make_context(p, chrome_profile, headless=args.headless)
        page = context.new_page()

        # 访问知识星球
        url = f"https://wx.zsxq.com/group/{args.group_id}/topics"
        print(f"访问: {url}")
        page.goto(url)

        # 等待登录
        print("请确保已登录知识星球...")
        page.wait_for_timeout(5000)

        # 采集数据
        print(f"开始采集 {args.limit} 条帖子...")
        posts = scroll_and_collect(page, args.group_id, args.limit)

        # 保存数据
        os.makedirs(args.output, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存为 JSON
        json_path = os.path.join(args.output, f"zsxq_posts_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

        # 保存为 Markdown
        md_path = os.path.join(args.output, f"zsxq_posts_{timestamp}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# 知识星球采集\n\n")
            f.write(f"Group ID: {args.group_id}\n")
            f.write(f"采集时间: {timestamp}\n")
            f.write(f"帖子数量: {len(posts)}\n\n---\n\n")

            for i, post in enumerate(posts):
                f.write(f"## {i+1}. {post.get('author', '未知')}\n\n")
                f.write(f"时间: {post.get('time', '未知')}\n\n")
                f.write(f"内容:\n{post.get('content', '')}\n\n")
                f.write(f"评论: {post.get('comments', '0')} | 点赞: {post.get('likes', '0')}\n\n")
                f.write("---\n\n")

        print(f"\n采集完成!")
        print(f"JSON: {json_path}")
        print(f"Markdown: {md_path}")

        context.close()


if __name__ == "__main__":
    main()
