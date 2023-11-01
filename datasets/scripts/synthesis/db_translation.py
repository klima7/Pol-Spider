import os
import sqlite3
import shutil
from pathlib import Path

from tqdm import tqdm

from common import SchemaTranslation


def translate_db(src_db_path, out_db_path, trans, db_prefix):
    shutil.copytree(src_db_path, out_db_path)
    
    if trans:
        for db_id in tqdm(trans.dbs_names, desc='Translating databases'):
            script = _generate_renaming_sql_script(trans[db_id])
            db_path = str(Path(out_db_path) / db_id / f'{db_id}.sqlite')
            _execute_sql_script(db_path, script)
            
    for db_id in [path.name for path in Path(src_db_path).glob('*/') if path.is_dir()]:
        os.rename(
            src=str(Path(out_db_path) / db_id),
            dst=str(Path(out_db_path) / f'{db_prefix}_{db_id}')
        )


def _execute_sql_script(db_path, script):
    connection = sqlite3.connect(db_path) 
    cursor = connection.cursor()
    cursor.executescript(script)
    connection.commit()
    connection.close()
    
    
def _generate_renaming_sql_script(trans):
    statements = []
    
    for table_name, table_trans in trans.tables.items():
        for old_name, column_trans in table_trans.columns.items():
            new_name = column_trans.orig
            if old_name.lower() != new_name.lower():
                statement = _create_column_rename_sql(table_name, old_name, new_name)
                statements.append(statement)
            
    for old_name, table_trans in trans.tables.items():        
        new_name = table_trans.orig
        if old_name.lower() != new_name.lower():
            statement = _create_table_rename_sql(old_name, new_name)
            statements.append(statement)
            
    return '\n'.join(statements)


def _create_column_rename_sql(table_name, old_name, new_name):
    return f'ALTER TABLE "{table_name}" RENAME COLUMN "{old_name}" TO "{new_name}";'
    
    
def _create_table_rename_sql(old_name, new_name):
    return f'ALTER TABLE "{old_name}" RENAME TO "{new_name}";'
