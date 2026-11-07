import urllib.request
import xml.etree.ElementTree as ET
import json
import os
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
            
            # Extract RSS items
            for item in root.findall('.//item')[:5]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else '#'
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''
                
                # Clean simple tags
                clean_desc = description.split('<')[0] if description else ''
                
                if title:
                    articles.append({
                        "title": title,
                        "source": feed["source"],
                        "url": link,
                        "date": pubDate[:16] if pubDate else 'Today',
                        "content": clean_desc[:250] + '...' if clean_desc else title
                    })
    except Exception as e:
        print(f"Error fetching {feed['source']}: {e}")

# Save to news.json
with open('news.json', 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Successfully fetched {len(articles)} articles at {datetime.now()}")
