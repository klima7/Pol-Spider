import json
import tempfile
import shutil
from pathlib import Path

from tqdm import tqdm
from joblib import Parallel, delayed

from common import load_json, save_json, SchemaTranslation, Dataset
from common.constants import *
from .sql_parsing import create_sql, get_schemas_from_json, SQLParseException
from .tokenization import tokenize_question, tokenize_query, tokenize_query_no_value
from .sql_translation import translate_queries, translate_tables
from .db_translation import translate_db


def synthesize_dataset(
        output_name,
        dataset_name,
        schema_trans_name=None,
        with_db=False,
        query_lang='pl',
        question_lang='pl'
    ):    
    complete_dir_path = COMPLETE_PATH / output_name
    if complete_dir_path.exists():
        shutil.rmtree(str(complete_dir_path))
    complete_dir_path.mkdir(parents=True, exist_ok=False)
    
    trans = SchemaTranslation.load_by_name(schema_trans_name)
    dataset = Dataset.load_by_name(dataset_name)
    
    translate_tables(
        trans=trans,
        db_prefix=schema_trans_name,
        output_path=complete_dir_path / 'tables.json',
    )
        
    for split_name in dataset:
        synthesize_samples(
            samples=dataset[split_name],
            output_path=complete_dir_path / (split_name + '.json'),
            tables_path=complete_dir_path / 'tables.json',
            trans=trans,
            db_prefix=schema_trans_name,
            query_lang=query_lang,
            question_lang=question_lang
        )
        
    create_gold_sql(
        samples_paths=[complete_dir_path / 'train_spider.json', complete_dir_path / 'train_others.json'],
        output_path=complete_dir_path / 'train_gold.sql',
    )
    
    create_gold_sql(
        samples_paths=[complete_dir_path / 'dev.json'],
        output_path=complete_dir_path / 'dev_gold.sql',
    )

    if with_db:
        translate_db(
            src_db_path=DATABASE_PATH,
            out_db_path=complete_dir_path / 'database',
            trans=trans,
            db_prefix=schema_trans_name
        )


def synthesize_samples(
    samples, output_path, tables_path, trans, db_prefix, query_lang, question_lang
):
    tables = load_json(tables_path)
    
    if trans:
        samples = translate_queries(samples, trans, query_lang)
        
    for sample in samples:
        sample.db_id = f"{db_prefix}_{sample.db_id}"
        
    complete_samples = add_calculated_attributes(samples, tables, query_lang, question_lang)
    save_json(output_path, complete_samples)


def add_calculated_attributes(samples, tables, query_lang, question_lang):
    _, tables_path = tempfile.mkstemp()
    with open(tables_path, "w") as f:
        json.dump(tables, f, indent=4, ensure_ascii=False)
    schemas, _, tables = get_schemas_from_json(tables_path)

    return Parallel(-1, backend="multiprocessing")(
        delayed(add_calculated_attributes_single)(sample, query_lang, question_lang, schemas, tables)
        for sample in tqdm(samples, desc="Adding calculated attributes")
    )


def add_calculated_attributes_single(sample, query_lang, question_lang, schemas, tables):
    try:
        sql = create_sql(
            db_id=sample.db_id,
            query=sample.query[query_lang],
            schemas=schemas,
            tables=tables
        )
    except SQLParseException:
        print(f"WARNING Unable to parse SQL for sample '{sample.query[query_lang]}'")
        fake_query=f"select count(*) from {list(schemas[sample.db_id].keys())[0]}"
        sql = create_sql(
            db_id=sample.db_id,
            query=fake_query,
            schemas=schemas,
            tables=tables
        )

    new_sample = {
        "db_id": sample.db_id,
        "question": sample.question[question_lang],
        "question_toks": tokenize_question(sample.question[question_lang]),
        "query": sample.query[query_lang],
        "query_toks": tokenize_query(sample.query[query_lang]),
        "query_toks_no_value": tokenize_query_no_value(sample.query[query_lang]),
        "sql": sql,
    }
    
    new_sample.update(sample.extras)
    
    return new_sample


def create_gold_sql(samples_paths, output_path):
    with open(output_path, 'w') as tgt:
        for samples_path in samples_paths:
            if not Path(samples_path).exists():
                continue
            samples = load_json(samples_path)
            for sample in samples:
                query = sample['query']
                db_id = sample['db_id']
                tgt.write(f"{query}\t{db_id}\n")
