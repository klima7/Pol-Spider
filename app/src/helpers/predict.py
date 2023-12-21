import time
import random
import json

import streamlit as st

from helpers.get_tables import get_tables
from resdsql.preprocessing import main as preprocessing


def predict_sql(question, sem_names, db_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        # create tables.json
        tables = get_tables(db_path, sem_names)
        with open(temp_dir / 'tables.json') as f:
            json.dump(tables, f, indent=4, ensure_ascii=False)
            
        # create dev.json
        with open(temp_dir / 'dev.json') as f:
            samples = {
                'db_id': 'base',
                'question': question,
            }
            json.dump(tables, f, indent=4, ensure_ascii=False)
            
        # preprocessing
        preprocessing(
            
        )
        
        return random.choice([
            "SELECT * FROM student",
            "SELECT imie FROM student",
        ])
