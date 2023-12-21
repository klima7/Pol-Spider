import os
import sys
import json
import sqlite3
from copy import deepcopy
from os import listdir, makedirs
from os.path import isfile, isdir, join, split, exists, splitext
from nltk import word_tokenize, tokenize
import traceback


def convert_fk_index(data):
    fk_holder = []
    for fk in data["foreign_keys"]:
        tn, col, ref_tn, ref_col = fk[0][0], fk[0][1], fk[1][0], fk[1][1]
        ref_cid, cid = None, None
        try:
            tid = data['table_names_original'].index(tn)
            ref_tid = data['table_names_original'].index(ref_tn)

            for i, (tab_id, col_org) in enumerate(data['column_names_original']):
                if tab_id == ref_tid and ref_col == col_org:
                    ref_cid = i
                elif tid == tab_id and col == col_org:
                    cid = i
            if ref_cid and cid:
                fk_holder.append([cid, ref_cid])
        except:
            traceback.print_exc()
            print("table_names_original: ", data['table_names_original'])
            print("finding tab name: ", tn, ref_tn)
            sys.exit()
    return fk_holder


def dump_db_json_schema(db, f):
    '''read table and column info'''

    conn = sqlite3.connect(db)
    conn.execute('pragma foreign_keys=ON')
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")

    data = {'db_id': f,
         'table_names_original': [],
         'table_names': [],
         'column_names_original': [(-1, '*')],
         'column_names': [(-1, '*')],
         'column_types': ['text'],
         'primary_keys': [],
         'foreign_keys': []}

    fk_holder = []
    for i, item in enumerate(cursor.fetchall()):
        table_name = item[0]
        data['table_names_original'].append(table_name)
        data['table_names'].append(table_name.lower().replace("_", ' '))
        fks = conn.execute("PRAGMA foreign_key_list('{}') ".format(table_name)).fetchall()
        #print("db:{} table:{} fks:{}".format(f,table_name,fks))
        fk_holder.extend([[(table_name, fk[3]), (fk[2], fk[4])] for fk in fks])
        cur = conn.execute("PRAGMA table_info('{}') ".format(table_name))
        for j, col in enumerate(cur.fetchall()):
            data['column_names_original'].append((i, col[1]))
            data['column_names'].append((i, col[1].lower().replace("_", " ")))
            #varchar, '' -> text, int, numeric -> integer,
            col_type = col[2].lower()
            if 'char' in col_type or col_type == '' or 'text' in col_type or 'var' in col_type:
                data['column_types'].append('text')
            elif 'int' in col_type or 'numeric' in col_type or 'decimal' in col_type or 'number' in col_type\
             or 'id' in col_type or 'real' in col_type or 'double' in col_type or 'float' in col_type:
                data['column_types'].append('number')
            elif 'date' in col_type or 'time' in col_type or 'year' in col_type:
                data['column_types'].append('time')
            elif 'boolean' in col_type:
                data['column_types'].append('boolean')
            else:
                data['column_types'].append('others')

            if col[5] == 1:
                data['primary_keys'].append(len(data['column_names'])-1)

    data["foreign_keys"] = fk_holder
    data['foreign_keys'] = convert_fk_index(data)

    return data


def apply_sem_names_to_tables(tables_json, sem_names, db_name='base'):
    new_tables_json = deepcopy(tables_json)
    db = [db for db in new_tables_json if db['db_id'] == db_name][0]
    
    for table_idx in range(len(db['table_names_original'])):
        name_original = db['table_names_original'][table_idx]
        if name_original in sem_names:
            db['table_names'][table_idx] = sem_names[name_original][0]
            
    for column_idx in range(len(db['column_names_original'])):
        table_idx, column_original = db['column_names_original'][column_idx]
        table_original = db['table_names_original'][table_idx]

        if table_original in sem_names and column_original in sem_names[table_original][1]:
            sem_name = sem_names[table_original][1][column_original]
            db['column_names'][column_idx] = (db['column_names'][column_idx][0], sem_name)
                
    return new_tables_json
        

def get_tables(db_path, sem_names=None, db_name='base'):
    ex_tabs = [
        {
            "column_names": [],
            "column_names_original": [],
            "column_types": [],
            "db_id": "base",
            "foreign_keys": [],
            "primary_keys": [],
            "table_names": [],
            "table_names_original": []
        }
    ]
    ex_tabs = {tab["db_id"]: tab for tab in ex_tabs}
    
    
    db_files = [db_path]
    tables = []
    
    for db in db_files:
        table = dump_db_json_schema(db, db_name)
        prev_tab_num = len(ex_tabs[db_name]["table_names"])
        prev_col_num = len(ex_tabs[db_name]["column_names"])
        cur_tab_num = len(table["table_names"])
        cur_col_num = len(table["column_names"])
        if db_name in ex_tabs.keys() and prev_tab_num == cur_tab_num and prev_col_num == cur_col_num and prev_tab_num != 0 and len(ex_tabs[db_name]["column_names"]) > 1:
            table["table_names"] = ex_tabs[db_name]["table_names"]
            table["column_names"] = ex_tabs[db_name]["column_names"]
        tables.append(table)
        
    tables = apply_sem_names_to_tables(tables, sem_names or {}, db_name)
        
    return tables
