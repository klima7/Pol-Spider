import sys
import json
from pathlib import Path

spider_dir = Path(sys.argv[1])

data = []

with open(spider_dir / 'train_spider.json', encoding='utf-8') as f:
    data.extend(json.load(f))
    
with open(spider_dir / 'train_others.json', encoding='utf-8') as f:
    data.extend(json.load(f))
    
with open(spider_dir / 'train.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)