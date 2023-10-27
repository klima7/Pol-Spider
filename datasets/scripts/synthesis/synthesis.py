import json
import tempfile
import shutil
from pathlib import Path

from tqdm import tqdm
from joblib import Parallel, delayed

from common import load_json, save_json, load_txt, load_column_translations, load_table_translations
from common.constants import *
from .sql_parsing import create_sql, get_schemas_from_json, SQLParseException
from .tokenization import tokenize_question, tokenize_query, tokenize_query_no_value
from .sql_translation import translate_samples, translate_tables
from .db_translation import translate_db


def add_calculated_attributes(samples, tables):
    _, tables_path = tempfile.mkstemp()
    with open(tables_path, "w") as f:
        json.dump(tables, f, indent=4, ensure_ascii=False)
    schemas, _, tables = get_schemas_from_json(tables_path)

    return Parallel(-1, backend="multiprocessing")(
        delayed(add_calculated_attributes_single)(sample, schemas, tables)
        for sample in tqdm(samples, desc="Adding calculated attributes")
    )


def add_calculated_attributes_single(sample, schemas, tables):
    try:
        sql = create_sql(sample["db_id"], sample["query_pl"], schemas, tables)
    except SQLParseException as e:
        print(f"WARNING Unable to parse SQL for sample '{sample['query_pl']}'")
        sql = create_sql(sample["db_id"], f"select count(*) from {list(schemas[sample['db_id']].keys())[0]}", schemas, tables)


    new_sample = {
        "db_id": sample["db_id"],
        "question": sample["question_pl"],
        "question_toks": tokenize_question(sample["question_pl"]),
        "query": sample["query_pl"],
        "query_toks": tokenize_query(sample["query_pl"]),
        "query_toks_no_value": tokenize_query_no_value(sample["query_pl"]),
        "sql": sql,
    }
    
    for extra_attr in ["type"]:
        if extra_attr in sample:
            new_sample[extra_attr] = sample[extra_attr]
    
    return new_sample


def create_gold_sql(samples_paths, output_path):
    samples_list = [load_json(path) for path in samples_paths]
    with open(output_path, 'w') as f:
        for samples in samples_list:
            for sample in samples:
                f.write(f"{sample['query']}\t{sample['db_id']}\n")


def synthesize_samples(
    samples_path, output_path, tables_path, column_trans_path, table_trans_path, db_prefix
):
    samples = load_json(samples_path)
    
    if column_trans_path and table_trans_path:
        table_trans = load_table_translations(table_trans_path)
        column_trans = load_column_translations(column_trans_path)
        samples = translate_samples(samples, table_trans, column_trans)
        
    for sample in samples:
        sample['db_id'] = f"{db_prefix}_{sample['db_id']}"
        
    tables = load_json(tables_path)
    samples = add_calculated_attributes(samples, tables)
    save_json(output_path, samples)
    
    
def get_paths_from_schema_translation_name(schema_translation_name):
    available_names = [path.name for path in TRANS_PATH.glob('*/')]
    if not schema_translation_name in available_names:
        return None, None, ''
    else:
        return (
            TRANS_PATH / schema_translation_name / 'column_trans.json',
            TRANS_PATH / schema_translation_name / 'table_trans.json',
            load_txt(TRANS_PATH / schema_translation_name / 'db_prefix.txt')
        )


def synthesize_everything(
    output_name, samples_paths, gold_mapping, schema_translation_name='', with_db=False
    ):
    column_trans_path, table_trans_path, db_prefix = get_paths_from_schema_translation_name(schema_translation_name)
    
    complete_dir_path = COMPLETE_PATH / output_name
    
    if complete_dir_path.exists():
        shutil.rmtree(str(complete_dir_path))
    complete_dir_path.mkdir(parents=True, exist_ok=False)
    
    if column_trans_path is not None:
        translate_tables(
            column_trans_path=column_trans_path,
            table_trans_path=table_trans_path,
            db_prefix=db_prefix,
            output_path=str(complete_dir_path / 'tables.json'),
        )
        
    else:
        shutil.copyfile(
            str(BASE_PATH / 'tables.json'),
            str(complete_dir_path / 'tables.json')
        )
        
    for samples_path in samples_paths:
        synthesize_samples(
            samples_path=samples_path,
            output_path=complete_dir_path / Path(samples_path).name,
            tables_path= str(complete_dir_path / 'tables.json'),
            column_trans_path=column_trans_path,
            table_trans_path=table_trans_path,
            db_prefix=db_prefix
        )
        
    for gold_name, samples_names in gold_mapping.items():
        create_gold_sql(
            [complete_dir_path / name for name in samples_names],
            complete_dir_path / gold_name
        )
        
    if with_db:
        translate_db(
            src_db_path=str(DATABASE_PATH),
            out_db_path=str(complete_dir_path / 'database'),
            column_trans_path=column_trans_path,
            table_trans_path=table_trans_path,
            db_prefix=db_prefix
        )
