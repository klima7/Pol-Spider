import json
from pathlib import Path

SPIDER_DIR = Path(__file__).parent.parent

data = []

with open(SPIDER_DIR / 'train_spider.json', encoding='utf-8') as f:
    data.extend(json.load(f))
    
with open(SPIDER_DIR / 'train_others.json', encoding='utf-8') as f:
    data.extend(json.load(f))
    
with open(SPIDER_DIR / 'train.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
