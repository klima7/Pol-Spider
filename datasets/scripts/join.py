import shutil

from common import load_json, save_json
from common.constants import *

import click


@click.command()
@click.argument('output_name', type=str)
@click.argument('datasets_names', type=str, nargs=-1)
def join(output_name, datasets_names):
    """Join multiple datasets into one"""
    datasets_paths = [COMPLETE_PATH / name for name in datasets_names]
    output_path = COMPLETE_PATH / output_name
    _join_datasets(datasets_paths, output_path)
    
    
def _join_datasets(datasets_paths, output_path):
    if output_path.exists():
        print('Overwriting existing dataset')
        shutil.rmtree(str(output_path))
    output_path.mkdir()
    
    _join_dbs(datasets_paths, output_path)
    print('Joined databases')
    
    _join_tables(datasets_paths, output_path)
    print('Joined tables')
    
    _join_samples(datasets_paths, output_path)
    print('Joined samples')
    
    _join_gold(datasets_paths, output_path)
    print('Joined gold queries')
    
    
def _join_dbs(datasets_paths, output_path):
    base_out_path = Path(output_path) / 'database'
    for dataset_path in datasets_paths:
        base_src_path = Path(dataset_path) / 'database'
        if not base_src_path.exists():
            continue
        for src_db_path in [path for path in base_src_path.glob('*/') if path.is_dir()]:
            present = src_db_path.name in [path.name for path in base_out_path.glob('*/')]
            if not present:
                shutil.copytree(src_db_path, base_out_path / src_db_path.name)
                
    
def _join_tables(datasets_paths, output_path):
    joined_tables = []
    for dataset_path in datasets_paths:
        tables = load_json(Path(dataset_path) / 'tables.json')
        for entry in tables:
            if entry['db_id'] not in [x['db_id'] for x in joined_tables]:
                joined_tables.append(entry)
    save_json(Path(output_path) / 'tables.json', joined_tables)
    
   
    
def _join_samples(datasets_paths, output_path):
    joined_dev = []
    joined_spider = []
    joined_others = []
    
    joined_groups = [joined_dev, joined_spider, joined_others]
    split_names = ['dev.json', 'train_spider.json', 'train_others.json']
    
    for dataset_path in datasets_paths:
        for split_name, joined_group in zip(split_names, joined_groups):
            samples_path = Path(dataset_path) / split_name
            if not samples_path.exists():
                continue
            samples = load_json(samples_path)
            joined_group.extend(samples)
    
    for split_name, joined_group in zip(split_names, joined_groups):
        save_json(Path(output_path) / split_name, joined_group)
    
    
def _join_gold(datasets_paths, output_path):
    joined_dev = []
    joined_train = []
    
    for dataset_path in datasets_paths:
        dev_path = Path(dataset_path) / 'dev_gold.sql'
        if dev_path.exists():
            with open(dev_path, encoding='utf-8') as f:
                joined_dev.extend([line for line in f.readlines() if line.strip()])
            
        train_path = Path(dataset_path) / 'train_gold.sql'
        if train_path.exists():
            with open(train_path, encoding='utf-8') as f:
                joined_train.extend([line for line in f.readlines() if line.strip()])

    with open(Path(output_path) / 'dev_gold.sql', 'w', encoding='utf-8') as f:
        f.writelines(joined_dev)
        
    with open(Path(output_path) / 'train_gold.sql', 'w', encoding='utf-8') as f:
        f.writelines(joined_train)

if __name__ == '__main__':
    join()
