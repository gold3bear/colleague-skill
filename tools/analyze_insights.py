#!/usr/bin/env python
"""分析油管视频转录，提取核心观点和思维模式"""

import json
import os
import re
from pathlib import Path
from collections import Counter, defaultdict

# 视频元数据
with open("D:/projects/colleague-skill/zsxq_data/youtube_henren778/videos.json", 'r', encoding='utf-8') as f:
    videos_data = json.load(f)

video_map = {v['id']: v for v in videos_data['videos']}

def read_transcript(video_id):
    """读取转录文件"""
    path = f"D:/projects/colleague-skill/zsxq_data/youtube_henren778/transcripts/{video_id}.txt"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def extract_key_points(text, video_id):
    """从文本中提取关键论点和数据点"""
    video = video_map.get(video_id, {})
    title = video.get('title', '')[:60]

    # 提取百分比数据
    percentages = re.findall(r'([0-9]+(?:\.[0-9]+)?%)', text)
    # 提取金额数据
    amounts = re.findall(r'([0-9,]+(?:億|万|億美元|万美元|美元|元|桶|天|年|个月|周)', text)

    return {
        'video_id': video_id,
        'title': title,
        'text_len': len(text),
        'percentages': percentages[:20],  # 限制数量
        'amounts': amounts[:20],
    }

def main():
    transcripts_dir = "D:/projects/colleague-skill/zsxq_data/youtube_henren778/transcripts"
    output = []

    print("=" * 80)
    print("油管视频核心观点分析")
    print("=" * 80)
    print(f"频道: {videos_data['channel']}")
    print(f"视频数量: {len(videos_data['videos'])}")
    print("=" * 80)

    all_keywords = []
    all_topics = Counter()

    # 定义主题关键词映射
    topic_keywords = {
        '地缘政治/战争': ['伊朗', '美军', '川普', '特朗普', '海峽', '台海', '中美', '霍爾木茲', '原油', '油价', '石油', '制裁', '军事', '航母', '战争'],
        '宏观经济': ['利率', '国债', '收益率', 'CPI', '通胀', '通缩', 'GDP', '赤字', '债务', '美联储', '央行', '降息', '加息', '宽松', '紧缩'],
        '金融/投资': ['黄金', '股市', '指数', '期权', '期货', '量化', '算法', 'CTA', '对冲', '做空', '做多', '买入', '卖出', '收益率'],
        '中国/政治': ['中共', '习近平', '两会', '政策', '政府', '债务', '房地产', '土地', '财政', '银行', '城投'],
        '企业/财报': ['小米', '利润', '毛利率', '营收', '负债', '现金流', '财报', '降级', '估值', '股价'],
        '社会/人口': ['失业', '就业', '人口', '老龄化', '社保', '养老金', '房价', '消费', '内卷'],
    }

    for video in videos_data['videos']:
        video_id = video['id']
        title = video['title'][:80]
        text = read_transcript(video_id)

        if not text:
            continue

        # 统计主题分布
        for topic, keywords in topic_keywords.items():
            count = sum(1 for kw in keywords if kw in text)
            if count > 0:
                all_topics[topic] += count

        print(f"\n{'='*80}")
        print(f"📺 {title}")
        print(f"   观看: {video.get('views', 'N/A')} | 日期: {video.get('date', 'N/A')}")
        print(f"{'='*80}")

        # 分析主要内容方向
        text_lower = text[:5000]  # 分析前5000字

        # 提取核心结论（寻找"结论"、"意味着"、"这说明"等关键词后面的句子）
        conclusions = []
        for pattern in [r'结论[是为]?([^。]+)', r'意味着([^。]+)', r'这说明([^。]+)',
                       r'核心是([^。]+)', r'本质上([^。]+)', r'所以([^。]+)']:
            matches = re.findall(pattern, text)
            conclusions.extend(matches[:2])

        if conclusions:
            print("🔍 核心结论:")
            for c in conclusions[:3]:
                c = c.strip()[:100]
                if len(c) > 20:
                    print(f"   • {c}...")

        # 提取关键数据
        percentages = re.findall(r'([0-9]+(?:\.[0-9]+)?%)', text)
        if percentages:
            unique_pcts = list(set(percentages))[:8]
            print(f"\n📊 关键数据: {', '.join(unique_pcts[:8])}")

        # 预测/判断
        predictions = re.findall(r'(概率|预测|判断|可能|预计|估计)([^。]+)', text)
        if predictions:
            print(f"\n🎯 预测判断:")
            for p in predictions[:2]:
                pred = (p[0] + p[1]).strip()[:80]
                if len(pred) > 15:
                    print(f"   • {pred}...")

    # 主题分布统计
    print("\n" + "=" * 80)
    print("📈 主题分布统计")
    print("=" * 80)
    for topic, count in all_topics.most_common(10):
        bar = "█" * (count // 20) + "░" * (10 - count // 20)
        print(f"  {topic:20s} {bar} {count}")

if __name__ == '__main__':
    main()
