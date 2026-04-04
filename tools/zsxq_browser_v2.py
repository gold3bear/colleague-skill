#!/usr/bin/env python3
"""
知识星球浏览器抓取器 v2

改进版：
1. 滚动到"展开全部"按钮位置后再点击
2. 等待内容展开后再继续
3. 全量提取帖子内容
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
        # 降低自动化检测
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-first-run",
        ],
    )


def expand_all_posts(page, group_id):
    """展开所有折叠的帖子内容"""
    expanded_count = 0

    while True:
        # 查找所有"展开全部"按钮
        try:
            buttons = page.query_selector_all("text=展开全部")
            if not buttons:
                print(f"  没有更多需要展开的按钮")
                break

            print(f"  找到 {len(buttons)} 个\"展开全部\"按钮")

            # 只处理当前可见的前几个（避免一次性太多）
            for i, btn in enumerate(buttons[:5]):  # 每次最多展开5个
                try:
                    # 滚动到按钮位置
                    btn.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    btn.click()
                    time.sleep(0.5)
                    expanded_count += 1
                    print(f"    已展开 {expanded_count}: {btn.inner_text()[:30]}...")
                except Exception as e:
                    print(f"    展开失败: {e}")
                    continue

            # 滚动一下页面，加载更多按钮
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(0.5)

        except Exception as e:
            print(f"  查找按钮出错: {e}")
            break

    print(f"  总共展开: {expanded_count} 处")
    return expanded_count


def parse_full_posts(page, group_id):
    """解析当前页面的完整帖子列表"""
    posts = []

    try:
        # 等待帖子加载
        page.wait_for_selector(".posts-item", timeout=10000)
        items = page.query_selector_all(".posts-item")
    except Exception as e:
        print(f"  等待帖子加载失败: {e}")
        return posts

    for item in items:
        try:
            post = {}

            # 提取标题/内容（querySelector 返回的是 ElementHandle）
            content_el = item.query_selector(".content")
            if content_el:
                post["content"] = content_el.inner_text()

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
            print(f"  解析帖子失败: {e}")
            continue

    return posts


def scroll_and_collect(page, group_id, limit=200):
    """滚动页面、展开内容并收集帖子"""
    all_posts = []
    seen_contents = set()

    last_height = 0
    scroll_attempts = 0
    max_scroll_attempts = 30

    while len(all_posts) < limit and scroll_attempts < max_scroll_attempts:
        # 展开当前可见的折叠内容
        expand_all_posts(page, group_id)

        # 解析当前可见帖子
        posts = parse_full_posts(page, group_id)
        for post in posts:
            content_preview = post.get("content", "")[:100]
            if content_preview and content_preview not in seen_contents:
                seen_contents.add(content_preview)
                all_posts.append(post)
                author = post.get('author', '未知')
                content_short = post.get('content', '')[:50].replace('\n', ' ')
                print(f"  [{len(all_posts)}] {author}: {content_short}...")

        if len(all_posts) >= limit:
            break

        # 滚动页面
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2.0)

        # 检查是否到底
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
            last_height = new_height

        print(f"  滚动加载... 当前 {len(all_posts)} 条，已到底 {scroll_attempts}/{max_scroll_attempts}")

    return all_posts[:limit]


def main():
    parser = argparse.ArgumentParser(description="知识星球浏览器抓取器 v2")
    parser.add_argument("--group-id", required=True, help="知识星球 Group ID")
    parser.add_argument("--limit", type=int, default=200, help="采集数量")
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

        # 访问知识星球主页（必须先访问主页才能访问子页面）
        print("访问知识星球主页...")
        page.goto("https://wx.zsxq.com", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep(3)

        # 点击对应的星球链接
        print(f"跳转到星球 {args.group_id}...")
        try:
            group_link = page.wait_for_selector(f'a[href="/group/{args.group_id}"]', timeout=5000)
            group_link.click()
            time.sleep(3)
        except Exception as e:
            print(f"点击链接失败，尝试直接访问: {e}")
            page.goto(f"https://wx.zsxq.com/group/{args.group_id}/topics", timeout=30000)
            time.sleep(5)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                page.goto(f"https://wx.zsxq.com/group/{args.group_id}/topics", timeout=30000)
                break
            except Exception as e:
                print(f"  访问失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    print("  5秒后重试...")
                    time.sleep(5)
                else:
                    print("  无法访问，退出")
                    context.close()
                    return

        # 等待页面加载
        print("等待页面加载...")
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep(5)
        print(f"当前页面: {page.url}")
        page.wait_for_timeout(5000)

        # 采集数据
        print(f"开始采集 {args.limit} 条帖子（展开所有折叠内容）...")
        posts = scroll_and_collect(page, args.group_id, args.limit)

        # 保存数据
        os.makedirs(args.output, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存为 JSON
        json_path = os.path.join(args.output, f"zsxq_full_v2_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

        # 保存为纯文本
        txt_path = os.path.join(args.output, f"zsxq_full_v2_{timestamp}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            for i, post in enumerate(posts):
                f.write(f"{'='*60}\n")
                f.write(f"帖子 #{i+1}\n")
                f.write(f"作者: {post.get('author', '未知')}\n")
                f.write(f"时间: {post.get('time', '未知')}\n")
                f.write(f"评论: {post.get('comments', '0')} | 点赞: {post.get('likes', '0')}\n")
                f.write(f"{'='*60}\n")
                f.write(post.get('content', ''))
                f.write(f"\n\n")

        print(f"\n采集完成!")
        print(f"JSON: {json_path} ({len(posts)} 条)")
        print(f"TXT: {txt_path}")

        context.close()


if __name__ == "__main__":
    main()