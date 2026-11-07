import urllib.request
import xml.etree.ElementTree as ET
import json
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
                
                # Обид да се најде слика (преку enclosure, media:content или во самиот HTML опис)
                image_url = ""
                enclosure = item.find('enclosure')
                if enclosure is not None and enclosure.get('url'):
                    image_url = enclosure.get('url')
                else:
                    # Барање слика низ media namespace или во HTML содржината
                    for child in item:
                        if 'thumbnail' in child.tag or 'content' in child.tag:
                            if child.get('url'):
                                image_url = child.get('url')
                                break
                
                # Ако нема издвоена слика, ставаме убава стандардна крипто слика како замена
                if not image_url:
                    image_url = "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=600&auto=format&fit=crop&q=80"

                # Чистење на описот за целосен текст
                clean_desc = description.replace('<p>', '').replace('</p>', '').replace('<br>', ' ')
                # Отстранување на останати HTML тагови за чист текст
                import re
                clean_text = re.sub('<[^<]+?>', '', description)
                
                if title:
                    articles.append({
                        "title": title,
                        "source": feed["source"],
                        "url": link,
                        "date": pubDate[:16] if pubDate else 'Today',
                        "image": image_url,
                        "content": clean_text if clean_text else title
                    })
    except Exception as e:
        print(f"Error fetching {feed['source']}: {e}")

with open('news.json', 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Successfully fetched {len(articles)} articles with images at {datetime.now()}")
