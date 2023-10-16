import json
import tempfile

from tqdm import tqdm
from joblib import Parallel, delayed

from .process_sql import create_sql, get_schemas_from_json, SQLParseException
from .tokenization import tokenize_question, tokenize_query, tokenize_query_no_value


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
    except SQLParseException:
        print(f"WARNING Unable to parse SQL for sample '{sample['query_pl']}'")
        sql = {
            "from": {"table_units": [], "conds": []},
            "select": [],
            "where": [],
            "groupBy": [],
            "having": [],
            "orderBy": [],
            "limit": None,
            "intersect": None,
            "union": None,
            "except": None,
        }

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


def create_gold_sql(samples_list, output_path):
    result = ""
    with open(output_path, 'w') as f:
        for samples in samples_list:
            for sample in samples:
                f.write(f"{sample['query_pl']}\t{sample['db_id']}\n")
    return result
