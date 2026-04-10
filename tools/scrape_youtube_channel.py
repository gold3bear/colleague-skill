#!/usr/bin/env python3
"""YouTube频道采集器

使用用户Chrome浏览器（已登录）采集频道视频、社区帖子等内容
"""

import os
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright


def get_chrome_context():
    """获取用户Chrome浏览器上下文（已登录状态）"""
    pw = sync_playwright().start()
    context = pw.chromium.launch_persistent_context(
        'C:/Users/gold3/AppData/Local/Google/Chrome/User Data/Default',
        headless=False,
        viewport={'width': 1280, 'height': 720},
    )
    return context, pw


def scrape_channel_videos(channel_url, output_dir, max_videos=50):
    """抓取频道视频列表（标题+描述）"""
    videos = []

    context, pw = get_chrome_context()
    page = context.new_page()

    print(f"访问频道: {channel_url}")
    page.goto(channel_url, timeout=60000)
    page.wait_for_timeout(3000)

    scroll_count = 0
    last_height = 0

    while scroll_count < 15 and len(videos) < max_videos:
        # 通过JavaScript提取数据 - 使用for循环避免filter问题
        video_data = page.evaluate('''() => {
            const items = Array.from(document.querySelectorAll("ytd-rich-item-renderer"));
            const results = [];
            for (const item of items) {
                const titleEl = item.querySelector("#video-title");
                const metaEl = item.querySelector("#metadata-line");
                if (titleEl && titleEl.innerText.trim()) {
                    results.push({
                        title: titleEl.innerText.trim(),
                        url: titleEl.href,
                        meta: metaEl ? metaEl.innerText.trim() : ""
                    });
                }
            }
            return results;
        }''')

        for v in video_data:
            # 解析观看数和日期
            views = ''
            date = ''
            parts = v['meta'].split('·')
            for part in parts:
                part = part.strip()
                if '观看' in part:
                    views = part.replace('次观看', '').strip()
                elif '前' in part:
                    date = part.strip()

            videos.append({
                'title': v['title'],
                'url': v['url'],
                'views': views,
                'date': date,
                'views_count': extract_views(views),
                'description': ''
            })
            print(f"  [{len(videos)}] {v['title'][:50]}... ({views})")

        # 滚动加载
        page.evaluate('window.scrollBy(0, 1000)')
        page.wait_for_timeout(800)

        new_height = page.evaluate('document.documentElement.scrollHeight')
        if new_height == last_height:
            scroll_count += 1
        else:
            last_height = new_height
            scroll_count = 0

        if len(videos) >= max_videos:
            break

    context.close()
    pw.stop()
    return videos


def get_video_description(page, video_url):
    """获取视频描述"""
    try:
        page.goto(video_url, timeout=30000)
        page.wait_for_timeout(1500)

        # 提取描述
        desc = page.evaluate('''
            () => {
                const descEl = document.querySelector('#description-inline-expander');
                if (descEl) {
                    // 点击展开全部描述
                    const moreBtn = descEl.querySelector('#expand');
                    if (moreBtn) moreBtn.click();
                    return descEl.innerText.trim();
                }
                return '';
            }
        ''')
        return desc.strip()
    except:
        return ''


def scrape_community_posts(channel_url, output_dir, max_posts=50):
    """抓取社区帖子"""
    posts = []

    context, pw = get_chrome_context()
    page = context.new_page()

    # 访问社区页面
    if '/community' in channel_url:
        community_url = channel_url
    else:
        community_url = channel_url.replace('/videos', '/community')

    print(f"访问社区: {community_url}")
    page.goto(community_url, timeout=60000)
    page.wait_for_timeout(3000)

    scroll_count = 0
    last_height = 0

    while scroll_count < 15 and len(posts) < max_posts:
        # 通过JavaScript提取帖子数据 - 使用for循环
        post_data = page.evaluate('''() => {
            const items = Array.from(document.querySelectorAll("ytd-backstage-post-renderer"));
            const results = [];
            for (const item of items) {
                const authorEl = item.querySelector("#author-text");
                const timeEl = item.querySelector("#publish-time");
                const contentEl = item.querySelector("#content-text");
                const voteEl = item.querySelector("#vote-count-left");
                const commentEl = item.querySelector("#comments-count");
                if (contentEl && contentEl.innerText.trim()) {
                    results.push({
                        id: item.dataset.postId || Math.random().toString(),
                        author: authorEl ? authorEl.innerText.trim() : "",
                        time: timeEl ? timeEl.innerText.trim() : "",
                        content: contentEl ? contentEl.innerText.trim().slice(0, 2000) : "",
                        votes: voteEl ? voteEl.innerText.trim() : "",
                        comments: commentEl ? commentEl.innerText.trim() : ""
                    });
                }
            }
            return results;
        }''')

        for p in post_data:
            posts.append(p)
            content_preview = p['content'][:80].replace('\n', ' ')
            print(f"  [{len(posts)}] {content_preview}...")

        # 滚动加载
        page.evaluate('window.scrollBy(0, 800)')
        page.wait_for_timeout(800)

        new_height = page.evaluate('document.documentElement.scrollHeight')
        if new_height == last_height:
            scroll_count += 1
        else:
            last_height = new_height
            scroll_count = 0

    context.close()
    pw.stop()
    return posts


def extract_views(views_str):
    """提取观看数数值"""
    if not views_str:
        return 0
    views_str = views_str.replace(',', '').replace('万', '0000')
    match = re.search(r'([\d.]+)', views_str)
    if match:
        return int(float(match.group(1)))
    return 0


def scrape_full(channel_url, output_dir, max_videos=50, max_posts=50):
    """完整采集：视频+描述+社区帖子"""
    os.makedirs(output_dir, exist_ok=True)

    # 1. 采集视频列表
    print("\n=== 采集视频列表 ===")
    videos = scrape_channel_videos(channel_url, output_dir, max_videos)

    # 2. 获取视频描述（取前20个）
    print("\n=== 获取视频描述 ===")
    context, pw = get_chrome_context()
    page = context.new_page()

    top_videos = sorted(videos, key=lambda x: x['views_count'], reverse=True)[:20]
    for i, video in enumerate(top_videos):
        print(f"[{i+1}/{len(top_videos)}] {video['title'][:40]}...")
        desc = get_video_description(page, video['url'])
        video['description'] = desc[:3000] if desc else '(无描述)'
        if desc:
            print(f"    描述长度: {len(desc)}")

    context.close()
    pw.stop()

    # 3. 采集社区帖子
    print("\n=== 采集社区帖子 ===")
    posts = scrape_community_posts(channel_url, output_dir, max_posts)

    # 保存结果
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # videos.json
    with open(f'{output_dir}/videos.json', 'w', encoding='utf-8') as f:
        json.dump({
            'channel': '一个狠人 @henren778',
            'scrape_time': timestamp,
            'count': len(videos),
            'videos': videos
        }, f, ensure_ascii=False, indent=2)

    # posts.json
    with open(f'{output_dir}/posts.json', 'w', encoding='utf-8') as f:
        json.dump({
            'channel': '一个狠人 @henren778',
            'scrape_time': timestamp,
            'count': len(posts),
            'posts': posts
        }, f, ensure_ascii=False, indent=2)

    # videos.md 摘要
    with open(f'{output_dir}/videos.md', 'w', encoding='utf-8') as f:
        f.write(f'# YouTube频道：一个狠人 (@henren778)\n\n')
        f.write(f'采集时间: {timestamp}\n')
        f.write(f'视频数量: {len(videos)}\n\n---\n\n')

        for i, v in enumerate(videos):
            f.write(f'## {i+1}. {v["title"]}\n\n')
            f.write(f'- 链接: {v["url"]}\n')
            f.write(f'- 观看: {v["views"]} | 日期: {v["date"]}\n')
            if v.get('description') and v['description'] != '(无描述)':
                f.write(f'- 描述: {v["description"][:300]}...\n')
            f.write('\n')

    # posts.md 摘要
    with open(f'{output_dir}/posts.md', 'w', encoding='utf-8') as f:
        f.write(f'# YouTube社区帖子：一个狠人 (@henren778)\n\n')
        f.write(f'采集时间: {timestamp}\n')
        f.write(f'帖子数量: {len(posts)}\n\n---\n\n')

        for i, p in enumerate(posts):
            f.write(f'## {i+1}. {p["time"]}\n\n')
            f.write(f'{p["content"]}\n\n')
            f.write(f'- 点赞: {p["votes"]} | 评论: {p["comments"]}\n\n')

    print(f"\n完成！")
    print(f"  视频: {len(videos)} 个 → {output_dir}/videos.json, videos.md")
    print(f"  帖子: {len(posts)} 个 → {output_dir}/posts.json, posts.md")

    return videos, posts


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='YouTube频道采集器')
    parser.add_argument('--channel', default='@henren778', help='频道名或URL')
    parser.add_argument('--output-dir', default='zsxq_data/youtube_henren778', help='输出目录')
    parser.add_argument('--max-videos', type=int, default=50, help='最大视频数')
    parser.add_argument('--max-posts', type=int, default=50, help='最大帖子数')

    args = parser.parse_args()

    if args.channel.startswith('http'):
        channel_url = args.channel
    else:
        channel_url = f'https://www.youtube.com/{args.channel}/videos'

    scrape_full(channel_url, args.output_dir, args.max_videos, args.max_posts)
