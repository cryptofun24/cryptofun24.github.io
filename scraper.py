import urllib.request
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

FEEDS = [
    {"source": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"},
    {"source": "CoinTelegraph", "url": "https://cointelegraph.com/rss"},
    {"source": "Decrypt", "url": "https://decrypt.co/feed"},
    {"source": "Bitcoin Magazine", "url": "https://bitcoinmagazine.com/.rss/full/"}
]

articles = []
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for feed in FEEDS:
    try:
        req = urllib.request.Request(feed["url"], headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            for item in root.findall('.//item')[:5]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else '#'
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''
                
                # Извлекување на слика
                image_url = ""
                enclosure = item.find('enclosure')
                if enclosure is not None and enclosure.get('url'):
                    image_url = enclosure.get('url')
                else:
                    for child in item:
                        if 'thumbnail' in child.tag or 'content' in child.tag:
                            if child.get('url'):
                                image_url = child.get('url')
                                break
                
                if not image_url:
                    image_url = "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=600&auto=format&fit=crop&q=80"

                # Чистење на содржината за убаво читање во модалот
                clean_text = re.sub('<[^<]+?>', ' ', description)
                clean_text = ' '.join(clean_text.split())
                
                if not clean_text or len(clean_text) < 30:
                    clean_text = title + " - Оваа вест е автоматски преземена од " + feed["source"] + ". Кликнете на копчето подолу за целосниот оригинален текст."

                if title:
                    articles.append({
                        "title": title,
                        "source": feed["source"],
                        "url": link,
                        "date": pubDate[:16] if pubDate else 'Today',
                        "image": image_url,
                        "content": clean_text
                    })
    except Exception as e:
        print(f"Error fetching {feed['source']}: {e}")

with open('news.json', 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Successfully fetched {len(articles)} articles at {datetime.now()}")
