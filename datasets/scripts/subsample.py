import shutil
import random
from pathlib import Path
from copy import deepcopy

import numpy as np
import click

from common import load_json, save_json
from common.constants import *
from third_party.evaluation import eval_hardness


@click.command()
@click.argument('input_name', type=str)
@click.argument('output_name', type=str)
@click.option('-t', '--train', type=int, default=0, help='Number of training samples')
@click.option('-d', '--dev', type=int, default=0, help='Number of dev samples')
@click.option('-s', '--seed', type=int, default=42, help='Seed')
def subsample(input_name, output_name, train, dev, seed):
    """Sanitize given schema translation by removing special characters and create new one"""
    
    _subsample(
        src_path=COMPLETE_PATH / input_name,
        dst_path=COMPLETE_PATH / output_name,
        train_size=train,
        dev_size=dev,
        seed=seed
    )


def _subsample(src_path, dst_path, train_size, dev_size, seed=42):
    random.seed(seed)
    
    if dst_path.exists():
        shutil.rmtree(str(dst_path))
    shutil.copytree(str(src_path), str(dst_path))
    
    train_distributions = _subsample_split(
        json_paths=[
            dst_path / 'train_spider.json',
            dst_path / 'train_others.json'
        ],
        gold_path=dst_path / 'train_gold.sql',
        size=train_size
    )
    
    dev_distributions = _subsample_split(
        json_paths=[
            dst_path / 'dev.json',
        ],
        gold_path=dst_path / 'dev_gold.sql',
        size=dev_size
    )
    
    distributions = {
        "train": train_distributions,
        "dev": dev_distributions
    }
    save_json(dst_path / 'distributions.json', distributions)
    
    
def _subsample_split(json_paths, gold_path, size):
    samples = []
    for path in json_paths:
        for sample in load_json(path):
            sample['path'] = path
            samples.append(sample)
            
    hardnesses = {'easy': [], 'medium': [], 'hard': [], 'extra': []}
    for sample in samples:
        hardness = eval_hardness(sample['sql'])
        hardnesses[hardness].append(sample)
        
    for dif_samples in hardnesses.values():
        random.shuffle(dif_samples)
        
    orig_distrib = {dif: len(dif_samples) / len(samples) for dif, dif_samples in hardnesses.items()}
    
    names = list(hardnesses.keys())
    count = np.array([len(dif_samples) for dif_samples in hardnesses.values()])
    scale_factor = len(samples) / max(size, 1)
    scaled_count = count / scale_factor
    
    # select samples one by one
    selected_hardnesses = {'easy': [], 'medium': [], 'hard': [], 'extra': []}
    for _ in range(size):
        selected_count = np.array([len(dif_samples) for dif_samples in selected_hardnesses.values()])
        diff = scaled_count - selected_count
        max_idx = np.argmax(diff)
        max_name = names[max_idx]
        sample = hardnesses[max_name].pop()
        selected_hardnesses[max_name].append(sample)
        
    sub_distrib = {dif: len(dif_samples) / max(size, 1) for dif, dif_samples in selected_hardnesses.items()}
    
    # flatten selected samples
    selected_samples = []
    for dif_samples in selected_hardnesses.values():
        selected_samples.extend(dif_samples)
    random.shuffle(selected_samples)
    
    # save new samples jsons
    for path in json_paths:
        path_samples = deepcopy([sample for sample in selected_samples if sample['path'] == path])
        for sample in path_samples:
            del sample['path']
        save_json(path, path_samples)
        
    # construct gold queries
    samples = []
    for path in json_paths:
        for sample in load_json(path):
            sample['path'] = path
            samples.append(sample)
            
    with open(gold_path, 'w') as f:
        for sample in samples:
            f.write(f"{sample['query']}\t{sample['db_id']}\n")
    
    return {
        'original': orig_distrib,
        'subsampled': sub_distrib
    }
    
    
if __name__ == '__main__':
    subsample()
