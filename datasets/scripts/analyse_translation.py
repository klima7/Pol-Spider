from statistics import mean, stdev
from common import SchemaTranslation

import click

from common import save_json
from common.constants import *


@click.command()
@click.argument('translation_name', type=str)
def analyse(translation_name):
    """Analyse given translation"""
    
    results = _analyse(translation_name)
    path = TRANS_PATH / f'analysis_{translation_name}.json'
    save_json(path, results)
    print('Saved', str(path))
    
    
def _analyse(trans_name):
    table_names, column_names = _get_names(trans_name)
    return {
        'tables': _analyse_names(table_names),
        'columns': _analyse_names(column_names)
    }
    
    
def _analyse_names(names):
    lengths = [len(name) for name in names]
    return _get_min_max_avg_dev(lengths)


def _get_names(trans_name):
    trans = SchemaTranslation.load_by_name(trans_name)
    table_names, column_names = [], []

    for db_id in trans:
        for table_name in trans[db_id]:
            table_names.append(table_name)
            for column_name in trans[db_id][table_name]:
                column_names.append(column_name)
                
    return table_names, column_names


def _get_min_max_avg_dev(numbers):
    return {
        'min': min(numbers) if numbers else None,
        'max': max(numbers) if numbers else None,
        'avg': mean(numbers) if numbers else None,
        'dev': stdev(numbers) if numbers else None
    }


if __name__ == '__main__':
    analyse()
