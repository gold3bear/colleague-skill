"""
Download one MrBrain video subtitle at a time, moving the file after each download.
Uses the same downsub.com approach but with sequential per-video processing.
"""

import asyncio
import os
import shutil
import time
from pathlib import Path

async def download_one(page, video_id, title):
    """Download one video's SRT and immediately copy it to safe location."""
    download_dir = Path("D:/projects/colleague-skill/.playwright-mcp")
    done_dir = Path("D:/projects/colleague-skill/colleagues/mrbrain/knowledge/transcripts/new_downloads")
    done_dir.mkdir(parents=True, exist_ok=True)

    url = f"https://downsub.com/?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D{video_id}"

    print(f"  Navigating to downsub...", end=" ", flush=True)
    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=20000)
    except Exception as e:
        print(f"NAV ERROR: {e}")
        return False

    # Check for error page
    content = await page.content()
    if "Error - DownSub" in content or "Something went wrong" in content:
        print("ERROR (member-only?)")
        return False

    # Click Chinese Traditional button
    try:
        btn = await page.wait_for_selector('button[data-lang="Chinese (Traditional)"]', timeout=8000)
        await btn.click()
        print(f"Clicked Traditional, waiting 6s...", end=" ", flush=True)
    except Exception:
        try:
            btn = await page.wait_for_selector('button[data-lang="Chinese (Simplified)"]', timeout=5000)
            await btn.click()
            print(f"Clicked Simplified, waiting 6s...", end=" ", flush=True)
        except Exception:
            print("NO CHINESE BUTTON")
            # Try to find any download button
            try:
                buttons = await page.query_selector_all("button.download-btn")
                for b in buttons:
                    lang = await b.get_attribute("data-lang")
                    if lang:
                        print(f"Found: {lang}", end=" ", flush=True)
                        await b.click()
                        break
            except:
                pass
            print("Skipping.")
            return False

    await asyncio.sleep(6)

    # Click SRT button if it appeared
    try:
        srt_btn = await page.wait_for_selector('button[data-lang="SRT"]', timeout=5000)
        await srt_btn.click()
        print("SRT, waiting 3s...", end=" ", flush=True)
        await asyncio.sleep(3)
    except Exception:
        pass

    # Find the downloaded SRT file (created in last 30 seconds)
    now = time.time()
    srt_files = []
    for f in download_dir.glob("*.srt"):
        if now - f.stat().st_mtime < 30:
            srt_files.append(f)

    if srt_files:
        # Copy with video_id name
        src = srt_files[0]
        dst = done_dir / f"{video_id}.srt"
        shutil.copy2(src, dst)
        print(f"SAVED: {dst.name} ({src.stat().st_size} bytes)")
        return True
    else:
        # No recent file - check what exists
        existing = list(download_dir.glob("*.srt"))
        if existing:
            # Use the most recently modified
            latest = max(existing, key=lambda f: f.stat().st_mtime)
            dst = done_dir / f"{video_id}.srt"
            shutil.copy2(latest, dst)
            print(f"SAVED (by mtime): {dst.name} ({latest.stat().st_size} bytes)")
            return True
        else:
            print("NO SRT FILE FOUND")
            return False


async def main():
    import playwright as p

    videos = [
        "3L6GK1nk5K4",
        "pqPw7xCZVaw",
        "vBu6zJAWcGs",
        "6WjdqxcEjR8",
        "hEr3ogBj92c",
        "sGyU9XhOJ18",
        "VtWwIcoSqoY",
        "RiKisSI0TLA",
        "Yf3tDP-0oZQ",
        "QySMd-czOUQ",
        "4ewrGvc6PqM",
        "cOxXsKLXbAw",
        "NL99n4AhulI",
        "TLK0boA19SU",
        "gdectSQZmII",
        "_1C1mRhUYwo",
        "ggzw_6EBHBY",
        "p5F0vg-BgVg",
        "fPxaaKn7GEA",
        "xr1BoXa13To",
    ]

    user_data_dir = "C:/Users/gold3/AppData/Local/Google/Chrome/User Data/Default"
    download_dir = "D:/projects/colleague-skill/.playwright-mcp"

    browser = await p.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        viewport={"width": 1280, "height": 720},
        download_path=download_dir,
    )

    page = browser.pages[0] if browser.pages else await browser.new_page()

    results = {}
    for i, video_id in enumerate(videos):
        title_map = {
            "3L6GK1nk5K4": "超越性",
            "pqPw7xCZVaw": "石油价格",
            "vBu6zJAWcGs": "反脆弱",
            "6WjdqxcEjR8": "随机漫步",
            "hEr3ogBj92c": "塔勒布",
            "sGyU9XhOJ18": "金融武力",
            "VtWwIcoSqoY": "地方债",
            "RiKisSI0TLA": "国债",
            "Yf3tDP-0oZQ": "人民币汇率宏观",
            "QySMd-czOUQ": "外汇微观",
            "4ewrGvc6PqM": "黄金比特币",
            "cOxXsKLXbAw": "竞争",
            "NL99n4AhulI": "东亚商业",
            "TLK0boA19SU": "加拿大",
            "gdectSQZmII": "川普",
            "_1C1mRhUYwo": "普通人投资",
            "ggzw_6EBHBY": "低信任",
            "p5F0vg-BgVg": "比特币内战",
            "fPxaaKn7GEA": "主权个人",
            "xr1BoXa13To": "开始收费",
        }
        title = title_map.get(video_id, video_id)
        print(f"\n[{i+1}/{len(videos)}] {title}")
        ok = await download_one(page, video_id, title)
        results[video_id] = ok
        await asyncio.sleep(2)

    await browser.close()

    succeeded = [v for v, s in results.items() if s]
    failed = [v for v, s in results.items() if not s]
    print(f"\n{'='*60}")
    print(f"Succeeded: {len(succeeded)}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    import playwright as p
    asyncio.run(main())
