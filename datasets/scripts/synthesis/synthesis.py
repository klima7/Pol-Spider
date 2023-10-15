import re
import json
import shutil
import tempfile
from copy import deepcopy

import sqlparse
from sqlparse import sql
import sqlglot
from sqlglot import dialects
import sqlglot.expressions as exp
import spacy
from tqdm import tqdm
from pathlib import Path
from joblib import Parallel, delayed

from translation import load_column_translations, load_table_translations


def translate_tables(tables, table_trans, column_trans):
    translated_tables = deepcopy(tables)

    for db in tqdm(translated_tables, desc="Translating tables"):
        db_id = db["db_id"]

        # translate columns
        assert db["column_names"][0][1] == "*"
        assert db["column_names_original"][0][1] == "*"
        for i in range(1, len(db["column_names_original"])):
            table_idx, column_name_original = db["column_names_original"][i]
            table_name = db["table_names_original"][table_idx]
            translations = column_trans[db_id][table_name.lower()][
                column_name_original.lower()
            ]
            db["column_names_original"][i][1] = translations["name_original"]
            db["column_names"][i][1] = translations["name"]

        # translate tables
        for i in range(len(db["table_names_original"])):
            table_name = db["table_names_original"][i]
            translations = table_trans[db_id][table_name.lower()]
            db["table_names_original"][i] = translations["name"]
            db["table_names"][i] = translations["name_original"]

    return translated_tables
