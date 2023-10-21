import click
from pathlib import Path

from common import load_json


TRANSLATIONS_DIR_PATH = Path(__file__).parent.parent / 'components' / 'schema_trans'



def check_tables_conflicts(table_trans_path):
    tables = load_json(table_trans_path)
        
    db_ids = set(table['db_id'] for table in tables)
    for db_id in db_ids:
        tables_names = list(table['name_original_pl'] for table in tables if table['db_id'] == db_id)
        duplicates = list(set([name for name in tables_names if len([x for x in tables_names if x == name]) > 1]))
        if duplicates:
            print(f"Conflicting tables {duplicates} in database '{db_id}'")
    
    
def check_columns_conflicts(column_trans_path):
    columns = load_json(column_trans_path)
        
    db_ids = set(column['db_id'] for column in columns)
    for db_id in db_ids:
        tables_names = set(column['table_name_original'] for column in columns if column['db_id'] == db_id)
        for table_name in tables_names:
            columns_names = [column['column_name_original_pl'] for column in columns if column['db_id'] == db_id and column['table_name_original'] == table_name]
            duplicates = list(set([name for name in columns_names if len([x for x in columns_names if x == name]) > 1]))
            if duplicates:
                print(f"Conflicting columns {duplicates} in table '{table_name}' in database '{db_id}'")


@click.command()
@click.argument('translation_name', type=str)
def sanitize(translation_name):
    """Check names conflicts in given translation"""
    translation_dir = TRANSLATIONS_DIR_PATH / translation_name

    check_tables_conflicts(translation_dir / 'table_trans.json')
    check_columns_conflicts(translation_dir / 'column_trans.json')


if __name__ == '__main__':
    sanitize()
