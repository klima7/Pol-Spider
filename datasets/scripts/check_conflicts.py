import click

from common import SchemaTranslation
from common.constants import *


def get_duplicates(elements):
    return list(set([
        e1 for e1 in elements 
        if len([e2 for e2 in elements if e2 == e1]) > 1
    ]))
    


def check_conflicts(trans_path):
    trans = SchemaTranslation.load(trans_path)
    
    for db_id, db in trans.dbs.items():
        tables_names = [table.orig.lower() for table in db.tables.values()]
        tables_duplicates = get_duplicates(tables_names)
        if tables_duplicates:
            print(f"Conflicting tables names {tables_duplicates} in database '{db_id}'")
        for table_name, table in db.tables.items():
            columns_names = [column.orig.lower() for column in table.columns.values()]
            columns_duplicates = get_duplicates(columns_names)
            if columns_duplicates:
                print(f"Conflicting columns names {columns_duplicates} in database '{db_id}' in table '{table_name}'")


@click.command()
@click.argument('translation_name', type=str)
def check_conflicts_cmd(translation_name):
    """Check names conflicts in given translation"""
    
    trans_path = TRANS_PATH / (translation_name + '.json')
    check_conflicts(trans_path)


if __name__ == '__main__':
    check_conflicts_cmd()
