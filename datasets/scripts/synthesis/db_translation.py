import sqlite3
import shutil
from pathlib import Path

from tqdm import tqdm

from common import load_column_translations, load_table_translations


def translate_db(src_db_path, out_db_path, column_trans_path, table_trans_path):
    shutil.copytree(src_db_path, out_db_path)
    
    if column_trans_path is None or table_trans_path is None:
        return
    
    column_trans = load_column_translations(column_trans_path)
    table_trans = load_table_translations(table_trans_path)
    
    for db_id in tqdm(table_trans.keys(), desc='Translating databases'):
        script = _generate_renaming_sql_script(db_id, column_trans, table_trans)
        db_path = str(Path(out_db_path) / db_id / f'{db_id}.sqlite')
        _execute_sql_script(db_path, script)


def _execute_sql_script(db_path, script):
    connection = sqlite3.connect(db_path) 
    cursor = connection.cursor()
    cursor.executescript(script)
    connection.commit()
    connection.close()
    
    
def _generate_renaming_sql_script(db_id, column_trans, table_trans):
    column_trans = column_trans[db_id]
    table_trans = table_trans[db_id]
    
    statements = []
    
    for table_name, columns_dict in column_trans.items():
        for old_name, translations in columns_dict.items():
            new_name = translations['name_original']
            if old_name.lower() != new_name.lower():
                statement = _create_column_rename_sql(table_name, old_name, new_name)
                statements.append(statement)
            
    for old_name, translations in table_trans.items():        
        new_name = translations['name_original']
        if old_name.lower() != new_name.lower():
            statement = _create_table_rename_sql(old_name, new_name)
            statements.append(statement)
            
    return '\n'.join(statements)


def _create_column_rename_sql(table_name, old_name, new_name):
    return f'ALTER TABLE "{table_name}" RENAME COLUMN "{old_name}" TO "{new_name}";'
    
    
def _create_table_rename_sql(old_name, new_name):
    return f'ALTER TABLE "{old_name}" RENAME TO "{new_name}";'
