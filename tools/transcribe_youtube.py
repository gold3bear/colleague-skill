#!/usr/bin/env python
"""批量将 YouTube 音频转录为文本"""

import whisper
import json
import os
from pathlib import Path

def transcribe_audio(audio_path, model, language='zh'):
    """转录单个音频文件"""
    try:
        result = model.transcribe(audio_path, language=language)
        return result['text']
    except Exception as e:
        print(f"转录错误: {e}")
        return ""

def main():
    base_dir = "D:/projects/colleague-skill/zsxq_data/youtube_henren778"
    audio_dir = f"{base_dir}/audio"
    transcript_dir = f"{base_dir}/transcripts"
    os.makedirs(transcript_dir, exist_ok=True)

    # 读取视频列表
    with open(f"{base_dir}/videos.json", 'r', encoding='utf-8') as f:
        videos = json.load(f)

    video_map = {v['id']: v for v in videos['videos']}

    # 加载 Whisper 模型 (使用 medium 模型 + GPU)
    print("加载 Whisper 模型 (medium)...")
    model = whisper.load_model('medium', device='cuda')

    # 获取所有 mp3 文件
    mp3_files = list(Path(audio_dir).glob("*.mp3"))
    print(f"共 {len(mp3_files)} 个音频文件，开始转录...")

    success = 0
    failed = 0

    for i, audio_file in enumerate(mp3_files):
        video_id = audio_file.stem  # 文件名（不含扩展名）
        title = video_map.get(video_id, {}).get('title', '')[:40]

        # 检查是否已转录
        transcript_file = f"{transcript_dir}/{video_id}.txt"
        if os.path.exists(transcript_file):
            print(f"[{i+1}/{len(mp3_files)}] 已存在: {title}...")
            success += 1
            continue

        print(f"[{i+1}/{len(mp3_files)}] 转录: {title}...")

        text = transcribe_audio(str(audio_file), model)

        if text:
            # 保存转录
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"  ✓ 完成 ({len(text)} 字)")
            success += 1
        else:
            print(f"  ✗ 失败")
            failed += 1

    print(f"\n完成！成功: {success}, 失败: {failed}")
    print(f"转录目录: {transcript_dir}")

if __name__ == '__main__':
    main()
