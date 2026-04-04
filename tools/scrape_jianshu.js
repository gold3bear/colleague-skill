// 简书文章批量采集脚本
// 在浏览器控制台执行

const ARTICLE_URLS = [
    "https://www.jianshu.com/p/beeeceb21afd",
    "https://www.jianshu.com/p/2dcf7fb04a85",
    "https://www.jianshu.com/p/2ebc018fe5a9",
    "https://www.jianshu.com/p/c383bfc700a2",
    "https://www.jianshu.com/p/ae3ce66a31cb",
    "https://www.jianshu.com/p/d56e71fd6106",
    "https://www.jianshu.com/p/1515e0bfb8b6",
    "https://www.jianshu.com/p/c5c636e6b1e2",
    "https://www.jianshu.com/p/e783a5b8ea4f",
    "https://www.jianshu.com/p/79660a483037",
    "https://www.jianshu.com/p/668c3cf93e78",
    "https://www.jianshu.com/p/4ba4e794c8c3",
    "https://www.jianshu.com/p/f42a1dd08649",
    "https://www.jianshu.com/p/a89b77c41d14",
    "https://www.jianshu.com/p/25de2036fcfe",
    "https://www.jianshu.com/p/9f695468358e",
    "https://www.jianshu.com/p/0423da87d52c",
    "https://www.jianshu.com/p/0dda86859812",
];

async function scrapeArticle(url) {
    try {
        const response = await fetch(url);
        const html = await response.text();

        // Extract title
        const titleMatch = html.match(/<h1[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)<\/h1>/s);
        const title = titleMatch ? titleMatch[1].replace(/<[^>]+>/g, '').trim() : url;

        // Extract date
        const dateMatch = html.match(/(\d{4}\.\d{2}\.\d{2})/);
        const date = dateMatch ? dateMatch[1] : '';

        // Extract content
        const contentMatch = html.match(/<div[^>]*class="[^"]*show-content[^"]*"[^>]*>(.*?)<\/div>/s);
        let content = '';
        if (contentMatch) {
            content = contentMatch[1].replace(/<[^>]+>/g, '').replace(/\s+/g, '\n').trim();
        }

        return { title, url, date, content };
    } catch (e) {
        return { title: url, url, date: '', content: '', error: e.message };
    }
}

async function scrapeAll() {
    const results = [];
    for (let i = 0; i < ARTICLE_URLS.length; i++) {
        console.log(`Scraping ${i+1}/${ARTICLE_URLS.length}: ${ARTICLE_URLS[i]}`);
        const result = await scrapeArticle(ARTICLE_URLS[i]);
        results.push(result);
        await new Promise(r => setTimeout(r, 500)); // delay
    }
    console.log('DONE');
    console.log(JSON.stringify(results, null, 2));
    return results;
}

// Copy results to clipboard
scrapeAll().then(results => {
    const text = results.map(r => `## ${r.title}\n日期: ${r.date}\n链接: ${r.url}\n\n${r.content}\n\n---\n`).join('\n');
    navigator.clipboard.writeText(text);
    console.log('Results copied to clipboard!');
});