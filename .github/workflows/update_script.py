import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

sites = [
    {"name": "CNN", "url": "https://www.cnn.com", "selector": "a.container__link"},
    {"name": "FT", "url": "https://www.ft.com", "selector": "a.js-teaser-heading-link"},
    {"name": "WSJ", "url": "https://www.wsj.com", "selector": "a[href*='/articles/']"},
    {"name": "Reuters", "url": "https://www.reuters.com", "selector": "a[href^='/world/'], a[href^='/business/']"},
    {"name": "Bloomberg", "url": "https://www.bloomberg.com", "selector": "a[href^='/news/articles/']"},
    {"name": "CNBC", "url": "https://www.cnbc.com/world/", "selector": "a[href^='https://www.cnbc.com/2025/']"},
    {"name": "Barrons", "url": "https://www.barrons.com", "selector": "a[href^='https://www.barrons.com/articles/']"},
    {"name": "Forbes", "url": "https://www.forbes.com", "selector": "a[href*='/sites/']"},
    {"name": "WaPo", "url": "https://www.washingtonpost.com", "selector": "a[href*='/2025/']"},
]

news_list = []

for site in sites:
    try:
        r = requests.get(site["url"], headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        links = soup.select(site["selector"])[:3]
        found = False
        for link in links:
            title = link.get_text(strip=True)
            if len(title) > 10 and 'http' in link.get('href', ''):
                url = link['href'] if link['href'].startswith('http') else site["url"] + link['href']
                summary = "点击阅读原文查看详情"
                news_list.append({
                    "source": site["name"],
                    "title_en": title,
                    "title_zh": title,  # 实际可后续优化翻译，这里先用原标题
                    "summary": summary,
                    "url": url,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                found = True
                break
        if not found:
            news_list.append({"source": site["name"], "title_zh": "暂无显眼头条或需订阅", "summary": "访问官网查看", "url": site["url"]})
    except:
        news_list.append({"source": site["name"], "title_zh": "抓取失败，请稍后刷新", "summary": "", "url": site["url"]})

# 生成HTML卡片
cards_html = ""
for i, news in enumerate(news_list[:9], 1):
    source_name = f"{i}. {news['source']}"
    if news['source'] == "FT":
        source_name = f"{i}. 金融时报 (FT)"
    elif news['source'] == "WSJ":
        source_name = f"{i}. 华尔街日报 (WSJ)"
    elif news['source'] == "WaPo":
        source_name = f"{i}. 华盛顿邮报 (WaPo)"
    elif news['source'] == "Barrons":
        source_name = "7. 巴伦周刊 (Barron's)"
    
    cards_html += f'''
            <div class="card">
                <div class="source">{source_name}</div>
                <div class="new-badge">新</div>
                <div class="title">{news.get("title_zh", "无标题")}</div>
                <div class="summary">{news["summary"]}</div>
                <div class="time">发布时间：{news.get("time", "近期")}</div>
                <div class="buttons">
                    <button class="read-original" onclick="window.open('{news["url"]}', '_blank')">阅读原文</button>
                    <button class="update">更新</button>
                    <button class="ai-analysis">AI 深度解读</button>
                </div>
            </div>'''

# 读取原index.html并替换
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换新闻网格和更新时间
update_time = datetime.now().strftime("%Y年%m月%d日 %H:%M (北京时间)")
content = re.sub(r'<div id="last-update">.*?</div>', f'<div id="last-update">最后更新时间：{update_time}</div>', content, flags=re.S)
content = re.sub(r'<div class="grid" id="news-grid">.*?</div>', f'<div class="grid" id="news-grid">\n{cards_html}\n        </div>', content, flags=re.S | re.M)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("News updated successfully!")
