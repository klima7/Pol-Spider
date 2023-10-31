import json
import tempfile
import shutil
from pathlib import Path

from tqdm import tqdm
from joblib import Parallel, delayed

from common import load_json, save_json, SchemaTranslation
from common.constants import *
from .sql_parsing import create_sql, get_schemas_from_json, SQLParseException
from .tokenization import tokenize_question, tokenize_query, tokenize_query_no_value
from .sql_translation import translate_samples, translate_tables
from .db_translation import translate_db


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
        sql = create_sql(sample["db_id"], sample['query'][query_lang], schemas, tables)
    except SQLParseException as e:
        print(f"WARNING Unable to parse SQL for sample '{sample['query'][query_lang]}'")
        sql = create_sql(sample["db_id"], f"select count(*) from {list(schemas[sample['db_id']].keys())[0]}", schemas, tables)


    new_sample = {
        "db_id": sample["db_id"],
        "question": sample['question'][question_lang],
        "question_toks": tokenize_question(sample['question'][question_lang]),
        "query": sample['query'][query_lang],
        "query_toks": tokenize_query(sample['query'][query_lang]),
        "query_toks_no_value": tokenize_query_no_value(sample['query'][query_lang]),
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
    samples_path,output_path, tables_path, trans_path, db_prefix, query_lang, question_lang
):
    samples = load_json(samples_path)
    tables = load_json(tables_path)
    
    if trans_path:
        trans = SchemaTranslation.load(trans_path)
        samples = translate_samples(samples, trans, query_lang)
        
    for sample in samples:
        sample['db_id'] = f"{db_prefix}_{sample['db_id']}"
        
    samples = add_calculated_attributes(samples, tables, query_lang, question_lang)
    
    save_json(output_path, samples)
    
    
def get_schema_trans_path(trans_name):
    available_names = [path.name[:-5] for path in TRANS_PATH.glob('*/')]
    if not trans_name in available_names:
        return None
    else:
        return TRANS_PATH / (trans_name + '.json')


def synthesize_everything(
    output_name, samples_paths, gold_mapping, schema_translation_name='', with_db=False, query_lang='pl', question_lang='pl'
    ):
    trans_path = get_schema_trans_path(schema_translation_name)
    db_prefix = schema_translation_name
    
    complete_dir_path = COMPLETE_PATH / output_name
    
    if complete_dir_path.exists():
        shutil.rmtree(str(complete_dir_path))
    complete_dir_path.mkdir(parents=True, exist_ok=False)
    
    translate_tables(
        trans_path=trans_path,
        db_prefix=db_prefix,
        output_path=str(complete_dir_path / 'tables.json'),
    )
        
    for samples_path in samples_paths:
        synthesize_samples(
            samples_path=samples_path,
            output_path=complete_dir_path / Path(samples_path).name,
            tables_path= str(complete_dir_path / 'tables.json'),
            trans_path=trans_path,
            db_prefix=db_prefix,
            query_lang=query_lang,
            question_lang=question_lang
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
            trans_path=trans_path,
            db_prefix=db_prefix
        )
