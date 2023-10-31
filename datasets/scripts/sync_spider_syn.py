from pathlib import Path

from tqdm import tqdm

from common.helpers import load_json, save_json
from common.constants import *


FILENAMES = ['train_spider.json', 'dev.json']


def synchronize():
    for filename in FILENAMES:
        spider = load_json(SAMPLES_PATH / 'spider' / filename)
        spider_syn = load_json(SAMPLES_PATH / 'spider_syn' / filename)
        
        spider_idx = 0
        spider_sample = spider[spider_idx]
        
        for sample in tqdm(spider_syn, desc=f'Syncing {filename}'):
            while not (
                spider_sample['question']['en'] == sample['question_original']['en'] and 
                spider_sample['db_id'] == sample['db_id']
                ):
                spider_idx += 1
                
                if spider_idx >= len(spider):
                    print(sample['question_original']['en'])
                    raise Exception('Unexpected exception')
                
                spider_sample = spider[spider_idx]
            sample['question_original'] = spider_sample['question']
                
        save_json(SAMPLES_PATH / 'spider_syn' / filename, spider_syn)


if __name__ == '__main__':
    synchronize()
    print('Done')
