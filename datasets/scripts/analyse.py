import sys
from copy import deepcopy
from statistics import mean, stdev

import click
import sqlparse

from common import load_json, save_json, get_tables_names, get_columns_names
from common.constants import *


@click.command()
@click.argument('dataset_name', type=str)
def analyse(dataset_name):
    """Analyse given dataset"""
    
    samples, train_samples, dev_samples = _load_samples(dataset_name)
    
    splits = [samples, train_samples, dev_samples]
    splits_names = ['all', 'train', 'dev']
    
    analysis = {
        split_name: _analyse_samples(samples)
        for split_name, samples in zip(splits_names, splits)
    }
    
    save_json(COMPLETE_PATH / dataset_name / 'analysis.json', analysis)
    
    
def _load_samples(dataset_name):
    dataset_path = COMPLETE_PATH / dataset_name
    if not dataset_path.exists():
        print('Dataset with given name does not exist')
        sys.exit(1) 
    
    dev_samples = []
    train_samples = []
    
    # dev
    path = dataset_path / 'dev.json'
    if path.exists():
        dev_samples.extend(load_json(path))
    
    # train_spider
    path = dataset_path / 'train_spider.json'
    if path.exists():
        train_samples.extend(load_json(path))
        
    # train_others
    path = dataset_path / 'train_others.json'
    if path.exists():
        train_samples.extend(load_json(path))
    
    samples = deepcopy(dev_samples + train_samples)
    return samples, train_samples, dev_samples, 
    
    
def _analyse_samples(samples):
    return {
        'samples count': len(samples),
        'question length': _analyse_question_length(samples),
        'value length': _analyse_value_length(samples),
        'column name length': _analyse_column_name_length(samples),
        'table name length': _analyse_table_name_length(samples)
    }
    
    
def _analyse_question_length(samples):
    character_lengths = [len(sample['question']) for sample in samples]
    token_lengths = [len(sample['question_toks']) for sample in samples]
    return {
        'characters': _get_min_max_avg_dev(character_lengths),
        'tokens': _get_min_max_avg_dev(token_lengths)
    }
    

def _analyse_value_length(samples):
    values = []
    for sample in samples:
        sample_values = _get_values_from_query(sample['query'])
        values.extend(sample_values)
    lengths = [len(value) for value in values]
    return {
        'characters': _get_min_max_avg_dev(lengths)
    }


def _analyse_table_name_length(samples):
    table_names = []
    for sample in samples:
        sample_table_names = get_tables_names(sample['query'])
        table_names.extend(sample_table_names)
    lengths = [len(name) for name in table_names]
    return {
        'characters': _get_min_max_avg_dev(lengths)
    }


def _analyse_column_name_length(samples):
    table_names = []
    for sample in samples:
        sample_table_names = get_columns_names(sample['query'])
        table_names.extend(sample_table_names)
    lengths = [len(name) for name in table_names]
    return {
        'characters': _get_min_max_avg_dev(lengths)
    }


def _get_min_max_avg_dev(numbers):
    return {
        'min': min(numbers),
        'max': max(numbers),
        'avg': mean(numbers),
        'dev': stdev(numbers)
    }
    
    
def _get_values_from_query(query):
    values = []
    for token in sqlparse.parse(query)[0].flatten():
        if str(token.ttype).startswith('Token.Literal.String'):
            values.append(token.value)
    return values


if __name__ == '__main__':
    analyse()
