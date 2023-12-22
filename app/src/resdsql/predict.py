import json
import tempfile
import shutil
from pathlib import Path

from helpers.get_tables import get_tables
from .preprocessing import preprocess
from .schema_item_classifier import classify_schema_items
from .text2sql_data_generator import generate_dataset
from .text2sql import generate_sql


def predict_sql(classifier_models, text2sql_models, question, db_path, sem_names=None, num_beams=8, num_return_sequences=8, seed=None):
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # paths
        temp_dir = Path(temp_dir)
        tables_path = temp_dir / 'tables.json'
        samples_path = temp_dir / 'dev.json'
        preprocessed_samples_path = temp_dir / 'preprocessed_test.json'
        database_path = temp_dir / 'database'
        database_base_path = database_path / 'base'
        with_probs_path = temp_dir / 'with_probs.json'
        dataset_path = temp_dir / 'dataset.json'

        # create tables
        tables = get_tables(db_path, sem_names=sem_names)
        with open(tables_path, 'w') as f:
            json.dump(tables, f, indent=4, ensure_ascii=False)

        # create samples
        with open(samples_path, 'w') as f:
            samples = [{ 'db_id': 'base', 'question': question }]
            json.dump(samples, f, indent=4, ensure_ascii=False)
            
        # create database
        database_base_path.mkdir(parents=True)
        shutil.copy(str(db_path), str(database_base_path / 'base.sqlite'))

        # preprocess
        preprocess(
            mode='test',
            table_path=str(tables_path),
            input_dataset_path=str(samples_path),
            output_dataset_path=str(preprocessed_samples_path),
            db_path=str(database_path),
            target_type='sql',
        )
        
        # classify schema items
        classify_schema_items(
            models=classifier_models,
            batch_size=1,
            seed=seed,
            dev_filepath=str(preprocessed_samples_path),
            output_filepath=str(with_probs_path),
            use_contents=True,
            add_fk_info=True,
            mode='test',
        )
        
        # create dataset with top schema items
        generate_dataset(
            input_dataset_path=str(with_probs_path),
            output_dataset_path=str(dataset_path),
            topk_table_num=4,
            topk_column_num=5,
            mode='test',
            use_contents=True,
            add_fk_info=True,
            output_skeleton=True,
            target_type='sql'
        )
        
        # generate final sql
        sql = generate_sql(
            models=text2sql_models,
            batch_size=1,
            seed=seed,
            mode="eval",
            dev_filepath=str(dataset_path),
            db_path=str(database_path),
            num_beams=num_beams,
            num_return_sequences=num_return_sequences,
            target_type="sql",
        )[0]
        
        return sql
