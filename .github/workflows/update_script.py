import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 每个源的专属选择器（实时验证有效）
sites = [
    {"name": "CNN", "url": "https://www.cnn.com", "selector": ".container__headline, .pg-headline", "link_attr": "href"},
    {"name": "FT", "url": "https://www.ft.com", "selector": ".js-teaser-heading-link", "link_attr": "href"},
    {"name": "WSJ", "url": "https://www.wsj.com", "selector": "h1, h2 a[href^='/finance/'], a[href^='/finance/']", "link_attr": "href"},
    {"name": "Reuters", "url": "https://www.reuters.com", "selector": "a[href^='/business/'], a[href^='/world/'], h2 a", "link_attr": "href"},
    {"name": "Bloomberg", "url": "https://www.bloomberg.com", "selector": "a[href^='/news/articles/']", "link_attr": "href"},
    {"name": "CNBC", "url": "https://www.cnbc.com/world/", "selector": "a[href^='https://www.cnbc.com/2025/']", "link_attr": "href"},
    {"name": "Barrons", "url": "https://www.barrons.com", "selector": "a[href^='/articles/'], h3 a", "link_attr": "href"},
    {"name": "Forbes", "url": "https://www.forbes.com", "selector": "a[href*='/sites/'][href*='/2025/']", "link_attr": "href"},
    {"name": "WaPo", "url": "https://www.washingtonpost.com", "selector": "a[href*='/2025/']", "link_attr": "href"},
]

news_list = []

for site in sites:
    try:
        r = requests.get(site["url"], headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        links = soup.select(site["selector"])[:5]  # 多取几个备选
        found = False
        for link in links:
            title = link.get_text(strip=True)
            href = link.get(site.get("link_attr", "href"), "")
            if title and len(title) > 10 and href:
                if not href.startswith("http"):
                    href = site["url"].rstrip("/") + "/" + href.lstrip("/")
                summary = "点击阅读原文查看详情（实时抓取）"
                news_list.append({
                    "source": site["name"],
                    "title_en": title,
                    "title_zh": title,  # 暂用原标题，直译更准可后续优化
                    "summary": summary,
                    "url": href,
                    "time": "近期"
                })
                found = True
                break
        if not found:
            news_list.append({"source": site["name"], "title_zh": "暂无显眼头条", "summary": "访问官网查看", "url": site["url"]})
    except Exception as e:
        print(f"Error fetching {site['name']}: {e}")
        news_list.append({"source": site["name"], "title_zh": "抓取失败", "summary": "请稍后重试", "url": site["url"]})

# 生成卡片HTML
cards_html = ""
for i, news in enumerate(news_list[:9], 1):
    source_name = f"{i}. {news['source']}"
    if news['source'] == "FT": source_name = "2. 金融时报 (FT)"
    elif news['source'] == "WSJ": source_name = "3. 华尔街日报 (WSJ)"
    elif news['source'] == "WaPo": source_name = "9. 华盛顿邮报 (WaPo)"
    elif news['source'] == "Barrons": source_name = "7. 巴伦周刊 (Barron's)"
    
    cards_html += f'''
            <div class="card">
                <div class="source">{source_name}</div>
                <div class="new-badge">新</div>
                <div class="title">{news["title_zh"]}</div>
                <div class="summary">{news["summary"]}</div>
                <div class="time">发布时间：{news["time"]}</div>
                <div class="buttons">
                    <button class="read-original" onclick="window.open('{news["url"]}', '_blank')">阅读原文</button>
                    <button class="update">更新</button>
                    <button class="ai-analysis">AI 深度解读</button>
                </div>
            </div>'''

# 替换index.html
index_path = 'index.html'
if os.path.exists(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    update_time = datetime.now().strftime("%Y年%m月%d日 %H:%M (北京时间)")
    content = re.sub(r'<div id="last-update">.*?</div>', f'<div id="last-update">最后更新时间：{update_time}</div>', content, flags=re.DOTALL)
    content = re.sub(r'<div class="grid" id="news-grid">\s*<.*?>.*?</div>', f'<div class="grid" id="news-grid">\n{cards_html}\n        </div>', content, flags=re.DOTALL)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("index.html updated successfully!")
else:
    print("index.html not found!")
