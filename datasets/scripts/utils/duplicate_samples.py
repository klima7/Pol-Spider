import re

import numpy as np
from tqdm import tqdm
import seaborn as sns

from common import load_json, save_json
from common.constants import *


coarse_samples_paths = {
    'cosql': [
        SAMPLES_PATH / 'cosql_wc' / 'dev.json',
        SAMPLES_PATH / 'cosql_wc' / 'train_spider.json'
    ],
    'sparc': [
        SAMPLES_PATH / 'sparc_wc' / 'dev.json',
        SAMPLES_PATH / 'sparc_wc' / 'train_spider.json'
    ],
    'spider': [
        SAMPLES_PATH / 'spider' / 'dev.json',
        SAMPLES_PATH / 'spider' / 'train_others.json',
        SAMPLES_PATH / 'spider' / 'train_spider.json'
    ],
    'spider_dk': [
        SAMPLES_PATH / 'spider_dk' / 'dev.json'
    ],
    'spider_syn': [
        SAMPLES_PATH / 'spider_syn' / 'dev.json',
        SAMPLES_PATH / 'spider_syn' / 'train_spider.json'
    ]
}

fine_samples_paths = {
    'cosql D': [
        SAMPLES_PATH / 'cosql_wc' / 'dev.json',
    ],
    'cosql T': [
        SAMPLES_PATH / 'cosql_wc' / 'train_spider.json'
    ],
    'sparc D': [
        SAMPLES_PATH / 'sparc_wc' / 'dev.json',
    ],
    'sparc T': [
        SAMPLES_PATH / 'sparc_wc' / 'train_spider.json'
    ],
    'spider D': [
        SAMPLES_PATH / 'spider' / 'dev.json'
    ],
    'spider T': [
        SAMPLES_PATH / 'spider' / 'train_others.json',
        SAMPLES_PATH / 'spider' / 'train_spider.json'
    ],
    'spider_dk D': [
        SAMPLES_PATH / 'spider_dk' / 'dev.json'
    ],
    'spider_syn D': [
        SAMPLES_PATH / 'spider_syn' / 'dev.json',
    ],
    'spider_syn T': [
        SAMPLES_PATH / 'spider_syn' / 'train_spider.json'
    ]
}


def intra_dataset_deduplication(path):
    samples = load_json(path)
    deduplciated_samples = _remove_intra_dataset_duplicates(samples)
    save_json(path, deduplciated_samples)


def _remove_intra_dataset_duplicates(samples):
    deduplicated_samples = {}
    
    for sample in samples:
        db_id = sample['db_id']
        question = _normalize_question(sample['question'])
        key = (db_id, question)
        if key not in deduplicated_samples.keys():
            deduplicated_samples[key] = sample
    deduplicated_samples = list(deduplicated_samples.values())
    
    initial_size = len(samples)
    deduplicated_size = len(deduplicated_samples)
    
    print('Initial size:', initial_size)
    print('Deduplicated size:', deduplicated_size)
    print('Removed', initial_size - deduplicated_size, 'samples')
    
    return deduplicated_samples


def _normalize_question(question):
    question_norm = question.lower().strip()
    question_norm = re.sub(r"\s+", " ", question_norm)
    return question_norm


def cross_dataset_deduplication(deduplicate_samples_paths, other_samples_paths):
    other_samples = []
    for path in other_samples_paths:
        other_samples.extend(load_json(path))
        
    other_pairs = [(sample['db_id'], _normalize_question(sample['question'])) for sample in other_samples]
    
    for path in deduplicate_samples_paths:
        samples = load_json(path)
        
        deduplicated_samples = []
        
        for sample in samples:
            pair = (sample['db_id'], _normalize_question(sample['question']))
            if pair not in other_pairs:
                deduplicated_samples.append(sample)
        
        removed_count = len(samples) - len(deduplicated_samples)
        percent = removed_count / len(samples)
        print(f'Removed {removed_count} samples ({percent:.2f}%) from {path}')
        
        save_json(path, deduplicated_samples)


def analyse_cross_dataset_duplication(datasets_paths):
    datasets = _load_datasets(datasets_paths)
    duplication_matrix = _create_duplication_matrix(datasets)
    _show_duplication_matrix(duplication_matrix, datasets)
    return duplication_matrix
    

def _load_datasets(datasets_paths):
    datasets = {}

    for name, paths in datasets_paths.items():
        datasets[name] = []
        for path in paths:
            samples = load_json(path)
            pairs = [(sample['db_id'], _normalize_question(sample['question'])) for sample in samples]
            datasets[name].extend(pairs)
            
    return datasets


def _create_duplication_matrix(datasets):
    duplication_matrix = np.zeros((len(datasets), len(datasets)), dtype=np.uint32)

    for i, name_i in enumerate(tqdm(datasets.keys())):
        for j, name_j in enumerate(datasets.keys()):
            if i <= j:
                continue
            
            pairs_i = datasets[name_i]
            pairs_j = datasets[name_j]
            
            duplicates_count = 0
            
            for pair_i in pairs_i:
                duplicates = [pair_j for pair_j in pairs_j if pair_j == pair_i]
                if duplicates:
                    duplicates_count += 1
                    
            duplication_matrix[i][j] = duplicates_count
            duplication_matrix[j][i] = duplicates_count
            
    return duplication_matrix


def _show_duplication_matrix(duplication_matrix, datasets):
    names_with_size = [f'{name}\n({len(samples)})' for name, samples in datasets.items()]

    duplication_matrix_viz = sns.heatmap(
        duplication_matrix,
        annot=True,
        fmt="d",
        xticklabels=names_with_size,
        yticklabels=names_with_size,
    )

    duplication_matrix_viz.set_yticklabels(
        duplication_matrix_viz.get_yticklabels(),
        rotation=0,
        fontsize=10
    )
