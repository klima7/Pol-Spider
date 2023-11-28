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
    table_names, table_origs, column_names, column_origs = _get_names(trans_name)
    return {
        'tables': {
            'name': _analyse_names(table_names),
            'orig': _analyse_names(table_origs)
        },
        'columns': {
            'name': _analyse_names(column_names),
            'orig': _analyse_names(column_origs)
        },
    }
    
    
def _analyse_names(names):
    lengths = [len(name) for name in names]
    return _get_min_max_avg_dev(lengths)


def _get_names(trans_name):
    trans = SchemaTranslation.load_by_name(trans_name)
    table_names, table_origs = [], []
    column_names, column_origs = [], []

    for db_id in trans:
        for table_name in trans[db_id]:
            table_names.append(trans[db_id][table_name].name)
            table_origs.append(trans[db_id][table_name].orig)
            for column_name in trans[db_id][table_name]:
                column_names.append(trans[db_id][table_name][column_name].name)
                column_origs.append(trans[db_id][table_name][column_name].orig)
                
    return table_names, table_origs, column_names, column_origs


def _get_min_max_avg_dev(numbers):
    return {
        'min': min(numbers) if numbers else None,
        'max': max(numbers) if numbers else None,
        'avg': mean(numbers) if numbers else None,
        'dev': stdev(numbers) if numbers else None
    }


if __name__ == '__main__':
    analyse()
