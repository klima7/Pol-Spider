from pathlib import Path

from tqdm import tqdm

from common.helpers import load_json, save_json


SAMPLES_DIR_PATH = Path(__file__).parent.parent / 'components' / 'samples'
FILENAMES = ['train_spider.json', 'dev.json']


def synchronize():
    for filename in FILENAMES:
        spider = load_json(SAMPLES_DIR_PATH / 'spider' / filename)
        spider_syn = load_json(SAMPLES_DIR_PATH / 'spider_syn' / filename)
        
        for sample, sample_syn in tqdm(zip(spider, spider_syn), total=len(spider), desc=f'Syncing {filename}'):
            sample_syn['question_original_pl'] = sample['question_pl']
            sample_syn['query_pl'] = sample['query_pl']

        save_json(SAMPLES_DIR_PATH / 'spider_syn' / filename, spider_syn)


if __name__ == '__main__':
    synchronize()
    print('Done')
