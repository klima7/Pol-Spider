import re
import shutil
from unidecode import unidecode
from pathlib import Path

from common import load_json, save_json

import click
from tqdm import tqdm


TRANSLATIONS_DIR_PATH = Path(__file__).parent.parent / 'components' / 'schema_trans'


def sanitize_name(name):
    name = unidecode(name).replace('-', '_')
    name = re.sub('[^A-Za-z0-9_]+', '', name)
    return name


def translate_columns(input_path, output_path):
    columns = load_json(input_path)
    for column in tqdm(columns, desc='Sanitizing columns'):
        column['column_name_original_pl'] = sanitize_name(column['column_name_original_pl'])
    save_json(output_path, columns)
    
    
def translate_tables(input_path, output_path):
    tables = load_json(input_path)
    for table in tqdm(tables, desc='Sanitizing tables'):
        table['name_original_pl'] = sanitize_name(table['name_original_pl'])
    save_json(output_path, tables)


@click.command()
@click.argument('input_name', type=str)
@click.argument('output_name', type=str)
def sanitize(input_name, output_name):
    """Sanitize given schema translation by removing special characters and create new one"""
    
    input_dir = TRANSLATIONS_DIR_PATH / input_name
    output_dir = TRANSLATIONS_DIR_PATH / output_name
    
    if output_dir.exists():
        shutil.rmtree(str(output_dir))
    output_dir.mkdir(parents=True, exist_ok=False)
    
    translate_tables(input_dir / 'table_trans.json', output_dir / 'table_trans.json')
    translate_columns(input_dir / 'column_trans.json', output_dir / 'column_trans.json')


if __name__ == '__main__':
    sanitize()
