"""
Batch download SRT subtitles for MrBrain channel videos via downsub.com
Uses Playwright with user's persistent Chrome profile (logged-in state for member videos)
"""

import asyncio
import re
import os
from pathlib import Path

async def download_single_video(page, video_id, title, download_dir, browser):
    """Download SRT for a single video. Returns True if successful."""
    try:
        url = f"https://downsub.com/?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D{video_id}"
        print(f"  Navigating to downsub for {video_id}...", end=" ", flush=True)
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=20000)

        # Check if error page (member-only)
        content = await page.content()
        if "Error - DownSub" in content or "Something went wrong" in content:
            print("ERROR (member-only?)")
            return False

        # Wait for the download button to appear
        try:
            # Look for the download button - downsub shows multiple language options
            # Chinese Traditional first, then Simplified
            btn = await page.wait_for_selector(
                'button[data-lang="Chinese (Traditional)"]',
                timeout=8000
            )
            print(f"Found Traditional button, clicking...", end=" ", flush=True)
            await btn.click()
        except Exception:
            try:
                btn = await page.wait_for_selector(
                    'button[data-lang="Chinese (Simplified)"]',
                    timeout=5000
                )
                print(f"Found Simplified button, clicking...", end=" ", flush=True)
                await btn.click()
            except Exception:
                # Fallback: look for any download button with Chinese
                print("Trying fallback selector...", end=" ", flush=True)
                try:
                    buttons = await page.query_selector_all("button.download-btn")
                    for b in buttons:
                        lang = await b.get_attribute("data-lang")
                        if lang and "Chinese" in lang:
                            await b.click()
                            break
                    else:
                        # Last resort: click the first visible download button
                        btn = await page.query_selector("button.download-btn")
                        if btn:
                            await btn.click()
                        else:
                            print("NO BUTTON FOUND")
                            return False
                except Exception as e:
                    print(f"BUTTON ERROR: {e}")
                    return False

        # Wait for SRT generation and download
        print("Waiting for SRT...", end=" ", flush=True)
        await asyncio.sleep(6)  # downsub processing time

        # Click download/SRT button if it appeared
        try:
            srt_btn = await page.wait_for_selector(
                'button[data-lang="SRT"]',
                timeout=5000
            )
            await srt_btn.click()
            print("SRT clicked, waiting...", end=" ", flush=True)
            await asyncio.sleep(3)
        except Exception:
            pass  # May have auto-downloaded

        print(f"Done: {video_id}")
        return True

    except Exception as e:
        print(f"FAILED: {e}")
        return False


async def main():
    # Videos still needing SRT (excluding the 13 we already have)
    existing_ids = {
        "nMEOcS8hzgg", "KXian", "DuanYongping", "PeterThiel", "PangDonglai",
        "CongMingRuoZhe", "EP01", "EP02VC",
        "5B4605EnmD4", "wvTHsJ7UjZs", "7HWATO98rwY", "t0BbQV2EAo4", "VP09PAKYUq4",
        # Also already downloaded (converted to new names):
        "cYyJ1QyFpPM",  # EP02VC - same
        "mVfknXFlj0w",  # PangDonglai - same
        "c7qJzG_swUE",  # EP01 - same
    }

    videos_to_download = [
        # High value videos first
        ("3L6GK1nk5K4", "识别下一个万亿机会的关键：超越性"),
        ("pqPw7xCZVaw", "一口气讲透石油价格"),
        ("vBu6zJAWcGs", "右派投资者的自我修养：反脆弱"),
        ("6WjdqxcEjR8", "概率的傲慢与赔率的智慧：随机漫步"),
        ("hEr3ogBj92c", "大灭绝时代的生存指南"),
        ("sGyU9XhOJ18", "金融的底层是武力"),
        ("VtWwIcoSqoY", "一口气讲透地方债"),
        ("RiKisSI0TLA", "一口气讲透国债"),
        ("Yf3tDP-0oZQ", "一口气讲透人民币汇率宏观篇"),
        ("QySMd-czOUQ", "一口气讲透外汇微观篇"),
        ("4ewrGvc6PqM", "黄金和比特币"),
        ("cOxXsKLXbAw", "为什么竞争一文不值"),
        ("NL99n4AhulI", "为什么东亚没能诞生沃尔玛"),
        ("TLK0boA19SU", "加拿大底层逻辑"),
        ("gdectSQZmII", "万字复盘川普商业生涯"),
        ("_1C1mRhUYwo", "普通人别学投资"),
        ("nT8GGAkhwz0", "定投标普500黄金时代结束"),
        ("enU1--8gK3s", "穷人存钱富人敢负债"),
        ("ggzw_6EBHBY", "低信任式防御"),
        # Gilded Age series - check if already done
        # 40KGev30ss8 - 镀金时代下 (may not have subtitles)
        # Lower priority
        ("p5F0vg-BgVg", "比特币内战"),
        ("fPxaaKn7GEA", "主权个人"),
        ("xr1BoXa13To", "开始收费"),
    ]

    # Remove any that we already have SRT for
    videos_to_download = [(vid, title) for vid, title in videos_to_download
                          if vid not in existing_ids]

    print(f"Total videos to attempt: {len(videos_to_download)}")
    print("=" * 60)

    # Launch browser with user's profile
    download_dir = Path("D:/projects/colleague-skill/.playwright-mcp")
    user_data_dir = "C:/Users/gold3/AppData/Local/Google/Chrome/User Data/Default"

    browser = await p.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        viewport={"width": 1280, "height": 720},
        download_path=str(download_dir),
    )

    page = browser.pages[0] if browser.pages else await browser.new_page()

    results = {}
    for i, (video_id, title) in enumerate(videos_to_download):
        print(f"\n[{i+1}/{len(videos_to_download)}] {title[:30]}...")
        success = await download_single_video(page, video_id, title, download_dir, browser)
        results[video_id] = success
        await asyncio.sleep(2)  # Be polite between requests

    await browser.close()

    print("\n" + "=" * 60)
    print("RESULTS:")
    succeeded = [v for v, s in results.items() if s]
    failed = [v for v, s in results.items() if not s]
    print(f"  Succeeded: {len(succeeded)}")
    print(f"  Failed: {len(failed)}")
    if failed:
        print(f"  Failed IDs: {failed}")


if __name__ == "__main__":
    import playwright as p
    asyncio.run(main())
