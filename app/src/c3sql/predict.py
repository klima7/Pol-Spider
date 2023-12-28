import json
import tempfile
import shutil
import subprocess
from pathlib import Path

from helpers.get_tables import get_tables


def predict_sql(question, db_path, openai_api_key, sem_names=None):
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # paths
        temp_dir = Path(temp_dir)
        aux_dir = temp_dir / 'aux'
        tables_path = temp_dir / 'tables.json'
        samples_path = temp_dir / 'dev.json'
        database_path = temp_dir / 'database'
        database_base_path = database_path / 'base'
        output_path = temp_dir / 'output.sql'

        # create tables
        tables = get_tables(db_path, sem_names=sem_names)
        with open(tables_path, 'w') as f:
            json.dump(tables, f, indent=4, ensure_ascii=False)

        # create samples
        with open(samples_path, 'w') as f:
            samples = [{ 'db_id': 'base', 'question': question, 'query': 'unknown'}]
            json.dump(samples, f, indent=4, ensure_ascii=False)
            
        # create database
        database_base_path.mkdir(parents=True)
        shutil.copy(str(db_path), str(database_base_path / 'base.sqlite'))
        
        # create aux dir
        aux_dir.mkdir()
        
        # run bash script
        ret = subprocess.call([
            'sh', './run_c3sql.sh',
            str(tables_path), str(samples_path), str(database_path), str(output_path), str(aux_dir), openai_api_key
        ], cwd=str(Path.cwd() / 'c3sql'))

        assert ret == 0

        # read output
        with open(output_path, 'r') as f:
            sql = f.readlines()[0].strip()
        
        return sql
