#!/usr/bin/env python
"""下载 YouTube 视频音频"""

import subprocess
import json
import os
from pathlib import Path

def download_audio(video_id, url, output_dir, cookies_file):
    """下载单个视频音频"""
    output_path = f"{output_dir}/{video_id}.%(ext)s"
    cmd = [
        'yt-dlp',
        '--js-runtimes', 'node',
        '--cookies', cookies_file,
        '--extractor-args', 'youtube:player_client=web',
        '--remote-components', 'ejs:github',
        '-f', '18',
        '--extract-audio',
        '--audio-format', 'mp3',
        '--output', output_path,
        '--no-playlist',
        url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True, "成功"
        else:
            return False, result.stderr[:100] if result.stderr else "未知错误"
    except Exception as e:
        return False, str(e)

def main():
    base_dir = "D:/projects/colleague-skill/zsxq_data/youtube_henren778"
    audio_dir = f"{base_dir}/audio"
    cookies_file = f"{base_dir}/cookies_fixed.txt"
    os.makedirs(audio_dir, exist_ok=True)

    # 读取视频列表
    with open(f"{base_dir}/videos.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    videos = data['videos']
    print(f"共 {len(videos)} 个视频，开始下载...")

    success = 0
    failed = 0

    for i, video in enumerate(videos):
        video_id = video.get('id')
        url = video.get('url')
        title = video.get('title', '')[:40]

        if not video_id or not url:
            print(f"[{i+1}/{len(videos)}] 跳过（无URL）: {title}...")
            continue

        # 检查是否已下载
        if os.path.exists(f"{audio_dir}/{video_id}.mp3"):
            print(f"[{i+1}/{len(videos)}] 已存在: {title}...")
            success += 1
            continue

        print(f"[{i+1}/{len(videos)}] 下载: {title}...")

        ok, msg = download_audio(video_id, url, audio_dir, cookies_file)
        if ok:
            print(f"  ✓ 成功")
            success += 1
        else:
            print(f"  ✗ 失败: {msg}")
            failed += 1

    print(f"\n完成！成功: {success}, 失败: {failed}")
    print(f"音频目录: {audio_dir}")

if __name__ == '__main__':
    main()
