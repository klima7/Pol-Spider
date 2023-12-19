import subprocess
import tempfile
import sqlite3
from pathlib import Path

from eralchemy import render_er
import cv2


def get_sql_from_db(db_path):
    sql = subprocess.check_output(["sqlite3", db_path, ".schema"])
    sql = sql.decode('utf-8').replace(';', ';\n')
    return sql


def get_db_from_sql(sql):
    path = Path(tempfile.mkdtemp()) / 'db.sqlite'
    with sqlite3.connect(path) as conn:
        conn.executescript(sql)
    return path


def get_schema_image_from_sql(sql):
    db_path = get_db_from_sql(sql)
    path = Path(tempfile.mkdtemp()) / 'schema.png'
    render_er(f"sqlite:///{db_path}", str(path))
    return cv2.imread(str(path))
    
    
def get_columns_from_db(db_path, table_name):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        query = f"pragma table_info({table_name});"
        cursor.execute(query)
        records = cursor.fetchall()
        columns = [record[1] for record in records]
        cursor.close()
        return columns
    
    
def get_tables_from_db(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT name FROM sqlite_schema WHERE type ='table' or type='column' AND name NOT LIKE 'sqlite_%';"
        cursor.execute(query)
        records = cursor.fetchall()
        tables = [record[0] for record in records]
        cursor.close()
        return tables
    

def get_schema_dict_from_db(db_path):
    tables = get_tables_from_db(db_path)
    schema_dict = {table: get_columns_from_db(db_path, table) for table in tables}
    return schema_dict


def get_schema_dict_from_sql(sql):
    db_path = get_db_from_sql(sql)
    return get_schema_dict_from_db(db_path)


def get_error_from_sql(sql):
    if sql.strip() == 0:
        return None
    
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / 'db.sqlite'
        try:
            with sqlite3.connect(path) as conn:
                conn.executescript(sql)
            return None
        except sqlite3.OperationalError as e:
            return str(e)


def divide_schema_dict(schema_dict, groups_count):
    groups = [{} for i in range(groups_count)]
    
    items = sorted(schema_dict.items(), key=lambda i: len(i[1]), reverse=True)
    for table, columns in items:
        groups_lengths = [(sum([len(columns)+2 for columns in group.values()]), idx) for idx, group in enumerate(groups)]
        smallest_group_idx = list(sorted(groups_lengths))[0][1]
        groups[smallest_group_idx][table] = columns
        
    return groups
