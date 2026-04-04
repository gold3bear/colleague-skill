#!/usr/bin/env python3
"""微信公众号文章采集器"""

from playwright.sync_api import sync_playwright
import time
import os
import json
from datetime import datetime

ALL_URLS = [
    'https://mp.weixin.qq.com/s/PnmoOxajO3sScFAJcAyuWw',
    'https://mp.weixin.qq.com/s/LYsT9i4hi5Zhm5qX_LvCqA',
    'https://mp.weixin.qq.com/s/i59dgKty_JUidv9sgasbNw',
    'https://mp.weixin.qq.com/s/Whh5IMsvjy748N4Sx0ojuw',
    'https://mp.weixin.qq.com/s/6pog0Eis0EQ2SaJPCycXFQ',
    'https://mp.weixin.qq.com/s/QCjfBBD7xp7XNZjkBTx0RQ',
    'https://mp.weixin.qq.com/s/VV1BUMQIMrb5LxQNusQsDg',
    'https://mp.weixin.qq.com/s/KH8VVmlajIB633lqjKUrTg',
    'https://mp.weixin.qq.com/s/bH_cu1pOqN2HOte7cLBuqg',
    'https://mp.weixin.qq.com/s/FdNBf47qKqHJmHrk9P_P9g',
    'https://mp.weixin.qq.com/s/QIbWKBRWBYEhxbsGT-QWkQ',
    'https://mp.weixin.qq.com/s/4BnYZkf6O1ohHmPNSrUbwQ',
    'https://mp.weixin.qq.com/s/W-RLw4_opn-r9OSwAru56A',
    'https://mp.weixin.qq.com/s/mZYt6jmNxdqQ2SXN7ikNAw',
    'https://mp.weixin.qq.com/s/vq9elvqMdDBZVsefspQ35Q',
    'https://mp.weixin.qq.com/s/T3fNd5_0M41bdTXgwKhCeg',
    'https://mp.weixin.qq.com/s/FtN86IYgA0bscwgQAjsNkg',
    'https://mp.weixin.qq.com/s/FB_4EH6SZ5iIIjkUi6l01w',
    'https://mp.weixin.qq.com/s/pGBHKYV21i9K8y4DkrNC2A',
    'https://mp.weixin.qq.com/s/myFl1NdH9IjimTj_O9ud2Q',
    'https://mp.weixin.qq.com/s/7fmJfVOEeX85XuLpsdw-6g',
    'https://mp.weixin.qq.com/s/c-icCLB8zmNGkv1UFdq3Cw',
    'https://mp.weixin.qq.com/s/RLuOfHgVQHqDIpa_a5_KLg',
    'https://mp.weixin.qq.com/s/pZtOsncvBnrW5eLaa-J9kg',
    'https://mp.weixin.qq.com/s/BpdPt2DXUU1KOPMX4hHm0w',
    'https://mp.weixin.qq.com/s/Vwp7wSGGhbbBhC-k4xri2A',
    'https://mp.weixin.qq.com/s/f2j8O9NbnWOAyBhH-Hg4Ww',
    'https://mp.weixin.qq.com/s/vgxt7cc2InsViPBPsEMbpw',
    'https://mp.weixin.qq.com/s/mIjFzDWf9VGsTASzi203cw',
    'https://mp.weixin.qq.com/s/hi3yUcgy3FDkyuRylhiczQ',
    'https://mp.weixin.qq.com/s/T0FkI4mHiSTdE8SwdAupFA',
    'https://mp.weixin.qq.com/s/lud-CWbX26ytZqY7HCcy6w',
    'https://mp.weixin.qq.com/s/_46n7R8_6IDPvJRq5_M6GA',
    'https://mp.weixin.qq.com/s/k4n7Wq7hVJeGLHDyM1AbFw',
    'https://mp.weixin.qq.com/s/Ph4FJcuuTqgh7nHaVleq9g',
    'https://mp.weixin.qq.com/s/sJph6nbGQNhQSzm9yKHT3g',
    'https://mp.weixin.qq.com/s/-QmOt-eFyZUYKQ5excL6NQ',
    'https://mp.weixin.qq.com/s/TWvAhsChL5DFun-ayRoD9A',
    'https://mp.weixin.qq.com/s/k_5_6jfbyGsl5qwSBpgQ9Q',
    'https://mp.weixin.qq.com/s/iy3B_eTJIZrHYO_BuN5y2A',
    'https://mp.weixin.qq.com/s/e4uOFCDThhVo8-4IzYbLHw',
    'https://mp.weixin.qq.com/s/6-dCexhlKpTi7ej-6QpsWA',
    'https://mp.weixin.qq.com/s/pjRDJUm17f380mZTyADLqw',
    'https://mp.weixin.qq.com/s/ttZrgiYB3a110UFAVWNVrA',
    'https://mp.weixin.qq.com/s/-8SfkCaAOqxCgqWx78M-FQ',
    'https://mp.weixin.qq.com/s/d0qzjvGIhOv33wXM7VLKZQ',
    'https://mp.weixin.qq.com/s/wKTbP_rLmOXdROs0XUIz8A',
    'https://mp.weixin.qq.com/s/Ib8UvD2qh4hEaEwte_qutA',
    'https://mp.weixin.qq.com/s/rrwenMFVcqTWvqdQsXOmyg',
    'https://mp.weixin.qq.com/s/3245mP9-03alR7KKpdYSmQ',
    'https://mp.weixin.qq.com/s/L9T1QGpDLMmSStcfNVf8Vw',
    'https://mp.weixin.qq.com/s/JrO-9fIZBnhqDkCv2E2lQw',
    'https://mp.weixin.qq.com/s/kW5waniHsMXHzzBwaIhReA',
    'https://mp.weixin.qq.com/s/0BLpHp0vKVUJJkKC5HckOA',
    'https://mp.weixin.qq.com/s/KMGxljQnSriYBASBtnYeHg',
    'https://mp.weixin.qq.com/s/gWhOWaufWJtHdEOMwgeQEg',
    'https://mp.weixin.qq.com/s/Fc7n8VmF1M046EvdGqXXzA',
    'https://mp.weixin.qq.com/s/gKwnbCHILvYBIpWMvZE4Yg',
    'https://mp.weixin.qq.com/s/d2NSmr6RTTk4J3vC1rI0EQ',
    'https://mp.weixin.qq.com/s/GZlVl0s5DyivZ0c-ksXBDg',
    'https://mp.weixin.qq.com/s/untPSG0wuWkeht-T542syw',
    'https://mp.weixin.qq.com/s/Y2HxWtBU9ta9sOfyPQqDYQ',
    'https://mp.weixin.qq.com/s/3PQ4bWUbAp0KRxRSCGoINg',
    'https://mp.weixin.qq.com/s/BzWGWPChuECh10k2u3CHNw',
    'https://mp.weixin.qq.com/s/168UVcTLd-UQAQ_1tZV_3A',
    'https://mp.weixin.qq.com/s/2GQqMqFxHTXwiE2MrgcJCQ',
    'https://mp.weixin.qq.com/s/3Yn7cpXFLuJ89k5a4HbN7A',
    'https://mp.weixin.qq.com/s/vK6EFXTHl8QcyuMZ9CBmZA',
    'https://mp.weixin.qq.com/s/DgYpXVC3q_6RUyb6ZUmtzQ',
    'https://mp.weixin.qq.com/s/w576jVcbj6jTPaF0r0Rtkg',
    'https://mp.weixin.qq.com/s/sdBCyX3KlmzWBdxgZfr-uQ',
    'https://mp.weixin.qq.com/s/-E3Wv41PXY-uFtBdfHQGDQ',
    'https://mp.weixin.qq.com/s/aLB6YOtGQJJsdYVJsYoSuA',
    'https://mp.weixin.qq.com/s/J_6wQWyUYg84x64gvV9ouA',
    'https://mp.weixin.qq.com/s/3OLjOlv2qm4VesBbTRUjEA',
    'https://mp.weixin.qq.com/s/6As5m0NbL1MiMGOJci7wZA',
    'https://mp.weixin.qq.com/s/XFcWI5g_8VS0qC_L13GBDA',
    'https://mp.weixin.qq.com/s/wfDHRWAQ_Wi5-pH2gdW1yQ',
    'https://mp.weixin.qq.com/s/UWg7ND_gMf5yUh-n0ojxpQ',
    'https://mp.weixin.qq.com/s/Je9e493vcxc_oVCDPWJTqA',
    'https://mp.weixin.qq.com/s/uwf58sUiVYQw_eGtNVgrqw',
    'https://mp.weixin.qq.com/s/D-9ZETFxUWq75XoGOudoYA',
    'https://mp.weixin.qq.com/s/qxzxqS2K6YSyFBkN_1s2Zg',
    'https://mp.weixin.qq.com/s/89lECNexzRo-MieMdEgqyA',
    'https://mp.weixin.qq.com/s/CeMhIhjqWrBZHUBCbMoQPQ',
    'https://mp.weixin.qq.com/s/EgrW9wDrjb4V9EsVo8B0vw',
    'https://mp.weixin.qq.com/s/x7jbJsICqz_JY4JcK7EQfg',
    'https://mp.weixin.qq.com/s/462OxHrADd9tplKakO9kjQ',
    'https://mp.weixin.qq.com/s/iiHuiraNd5fV27uWaUmxAw',
    'https://mp.weixin.qq.com/s/WXVfZKDY7nSLT6BGzG6wpQ',
    'https://mp.weixin.qq.com/s/ISDaTPnWD0wua2QH6TKu6A',
    'https://mp.weixin.qq.com/s/0syZ7rewdtnN4GQrjQ5sHQ',
    'https://mp.weixin.qq.com/s/5SVMQNk2mae3cw8wJB-gqA',
    'https://mp.weixin.qq.com/s/i_1LVyWatOmNzUf51cWp_Q',
    'https://mp.weixin.qq.com/s/WX7IB2px733_Yvh_3fPt_Q',
    'https://mp.weixin.qq.com/s/BQn_qQsSzV2S-cwmFL0ECw',
    'https://mp.weixin.qq.com/s/AQOicFLDDmYSh8-FITDrbw',
    'https://mp.weixin.qq.com/s/rRTIhH6KrLu_CUCs1Jynpw',
    'https://mp.weixin.qq.com/s/qGbhIiepdwP5eJJz0Spnfw',
    'https://mp.weixin.qq.com/s/ZBG1Tj18_z3G7OYpSDIYqA',
    'https://mp.weixin.qq.com/s/Jm0JRDnTlv8NKInVXELGXQ',
    'https://mp.weixin.qq.com/s/sa-7yPrBKJ22gVCPLDsJXA',
    'https://mp.weixin.qq.com/s/jndENHxB0bv5uW6tv8Q9vQ',
]

def scrape_all(urls, batch_size=10):
    """分批采集"""
    all_articles = []
    total_batches = (len(urls) + batch_size - 1) // batch_size

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            'C:/Users/gold3/AppData/Local/Google/Chrome/User Data/Default',
            headless=False,
            viewport={'width': 1280, 'height': 720},
        )
        page = context.new_page()

        for batch in range(total_batches):
            start = batch * batch_size
            end = min(start + batch_size, len(urls))
            batch_urls = urls[start:end]

            print(f'\\n=== Batch {batch+1}/{total_batches} ({start+1}-{end}) ===')

            for i, url in enumerate(batch_urls):
                idx = start + i + 1
                print(f'[{idx}/{len(urls)}] ', end='', flush=True)
                try:
                    page.goto(url, timeout=30000)
                    page.wait_for_timeout(1500)

                    title = page.title()
                    content = page.inner_text('#js_content') if page.query_selector('#js_content') else ''

                    all_articles.append({'title': title, 'url': url, 'content': content[:20000]})
                    print(f'{title[:35]}... ({len(content)} chars)')
                except Exception as e:
                    print(f'Error: {e}')
                    all_articles.append({'title': url, 'url': url, 'content': '', 'error': str(e)})

            # Save intermediate results
            with open(f'zsxq_data/wechat/articles_batch{batch+1}.json', 'w', encoding='utf-8') as f:
                json.dump(all_articles, f, ensure_ascii=False, indent=2)

        context.close()

    return all_articles

if __name__ == '__main__':
    os.makedirs('zsxq_data/wechat', exist_ok=True)
    articles = scrape_all(ALL_URLS, batch_size=20)

    # Save final results
    with open('zsxq_data/wechat/articles_full.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    with open('zsxq_data/wechat/articles_full.md', 'w', encoding='utf-8') as f:
        f.write('# 微信公众号文章集 - PM熊叔\n\n')
        f.write('采集时间: ' + datetime.now().strftime('%Y-%m-%d') + '\n')
        f.write('文章数量: ' + str(len(articles)) + '\n\n---\n\n')
        for i, a in enumerate(articles):
            f.write('## ' + str(i+1) + '. ' + a.get('title', '') + '\n\n')
            f.write('链接: ' + a.get('url', '') + '\n\n')
            f.write('内容:\n' + a.get('content', '') + '\n\n---\n\n')

    total = sum(len(a.get('content', '')) for a in articles)
    print(f'\\n=== FINAL: {len(articles)} articles, {total} total chars ===')