import re
import shutil
from unidecode import unidecode
from pathlib import Path

from common import SchemaTranslation

import click
from tqdm import tqdm


TRANSLATIONS_DIR_PATH = Path(__file__).parent.parent / 'components' / 'schema_trans'


def sanitize_name(name):
    name = unidecode(name).replace('-', '_')
    name = re.sub('[^A-Za-z0-9_]+', '', name)
    return name
    
    
def sanitize_schema_translation(input_path, output_path):
    trans = SchemaTranslation.load(input_path)
    for db in trans.dbs.values():
        for table in db.tables.values():
            table.orig = sanitize_name(table.orig)
            for column in table.columns.values():
                column.orig = sanitize_name(column.orig)
    trans.save(output_path)


@click.command()
@click.argument('input_name', type=str)
@click.argument('output_name', type=str)
def sanitize(input_name, output_name):
    """Sanitize given schema translation by removing special characters and create new one"""
    
    input_path = TRANSLATIONS_DIR_PATH / (input_name + '.json')
    output_path = TRANSLATIONS_DIR_PATH / (output_name + '.json')
    
    sanitize_schema_translation(input_path, output_path)


if __name__ == '__main__':
    sanitize()
