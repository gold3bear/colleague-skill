#!/usr/bin/env python3
"""Get YouTube transcript using Playwright browser session"""

import sys
import urllib.request
import re
from playwright.sync_api import sync_playwright

def get_transcript(video_id, output_path):
    with sync_playwright() as p:
        # Use existing Chrome browser with logged-in session
        context = p.chromium.launch_persistent_context(
            "C:/Users/gold3/AppData/Local/Google/Chrome/User Data/Default",
            headless=False,
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()
        page.goto(f"https://www.youtube.com/watch?v={video_id}")
        page.wait_for_timeout(3000)

        # Get transcript URL from player response
        transcript_url = page.evaluate("""() => {
            const trackList = window.ytInitialPlayerResponse?.captions?.playerCaptionsTracklistRenderer?.captionTracks;
            if (trackList && trackList.length > 0) {
                return trackList[0].baseUrl;
            }
            return null;
        }""")

        if not transcript_url:
            print("No transcript URL found")
            context.close()
            return None

        print(f"Transcript URL: {transcript_url[:100]}...")

        # Get cookies for the request
        cookies = context.cookies()
        cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

        context.close()

        # Now fetch the transcript with proper cookies
        req = urllib.request.Request(
            transcript_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Cookie': cookie_header,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('utf-8')
                print(f"Got transcript content, length: {len(content)}")

                # Save to file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Saved to {output_path}")
                return content
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            return None

if __name__ == "__main__":
    video_id = sys.argv[1] if len(sys.argv) > 1 else "nMEOcS8hzgg"
    output_path = sys.argv[2] if len(sys.argv) > 2 else f"colleagues/mrbrain/knowledge/transcripts/{video_id}.xml"

    get_transcript(video_id, output_path)
