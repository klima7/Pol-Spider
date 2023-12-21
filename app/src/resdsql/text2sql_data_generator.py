import json
import copy
import argparse
import random
import numpy as np


def lista_contains_listb(lista, listb):
    for b in listb:
        if b not in lista:
            return 0
    
    return 1

def prepare_input_and_output(use_contents, target_type, add_fk_info, output_skeleton, ranked_data):
    question = ranked_data["question"]

    schema_sequence = ""
    for table_id in range(len(ranked_data["db_schema"])):
        table_name_original = ranked_data["db_schema"][table_id]["table_name_original"]
        # add table name
        schema_sequence += " | " + table_name_original + " : "
        
        column_info_list = []
        for column_id in range(len(ranked_data["db_schema"][table_id]["column_names_original"])):
            # extract column name
            column_name_original = ranked_data["db_schema"][table_id]["column_names_original"][column_id]
            db_contents = ranked_data["db_schema"][table_id]["db_contents"][column_id]
            if use_contents and len(db_contents) != 0:
                column_contents = " , ".join(db_contents)
                column_info = table_name_original + "." + column_name_original + " ( " + column_contents + " ) "
            else:
                column_info = table_name_original + "." + column_name_original

            column_info_list.append(column_info)
        
        if target_type == "natsql":
            column_info_list.append(table_name_original + ".*")
    
        # add column names
        schema_sequence += " , ".join(column_info_list)

    if add_fk_info:
        for fk in ranked_data["fk"]:
            schema_sequence += " | " + fk["source_table_name_original"] + "." + fk["source_column_name_original"] + \
                " = " + fk["target_table_name_original"] + "." + fk["target_column_name_original"]
    
    # remove additional spaces in the schema sequence
    while "  " in schema_sequence:
        schema_sequence = schema_sequence.replace("  ", " ")

    # input_sequence = question + schema sequence
    input_sequence = question + schema_sequence
        
    if output_skeleton:
        if target_type == "sql":
            output_sequence = ranked_data["sql_skeleton"] + " | " + ranked_data["norm_sql"]
        elif target_type == "natsql":
            output_sequence = ranked_data["natsql_skeleton"] + " | " + ranked_data["norm_natsql"]
    else:
        if target_type == "sql":
            output_sequence = ranked_data["norm_sql"]
        elif target_type == "natsql":
            output_sequence = ranked_data["norm_natsql"]

    return input_sequence, output_sequence


def generate_dataset(input_dataset_path, output_dataset_path, topk_table_num, topk_column_num, mode, use_contents, add_fk_info, output_skeleton, target_type):
    with open(input_dataset_path) as f:
        dataset = json.load(f)

    table_coverage_state_list, column_coverage_state_list = [], []
    output_dataset = []
    for data_id, data in enumerate(dataset):
        ranked_data = dict()
        ranked_data["question"] = data["question"]
        ranked_data["sql"] = data["sql"]
        ranked_data["norm_sql"] = data["norm_sql"]
        ranked_data["sql_skeleton"] = data["sql_skeleton"]
        ranked_data["natsql"] = data["natsql"]
        ranked_data["norm_natsql"] = data["norm_natsql"]
        ranked_data["natsql_skeleton"] = data["natsql_skeleton"]
        ranked_data["db_id"] = data["db_id"]
        ranked_data["db_schema"] = []

        table_pred_probs = list(map(lambda x:round(x,4), data["table_pred_probs"]))
        # find ids of tables that have top-k probability
        topk_table_ids = np.argsort(-np.array(table_pred_probs), kind="stable")[:topk_table_num].tolist()
        
        # if the mode == eval, we record some information for calculating the coverage
        if mode == "eval":
            used_table_ids = [idx for idx, label in enumerate(data["table_labels"]) if label == 1]
            table_coverage_state_list.append(lista_contains_listb(topk_table_ids, used_table_ids))
            
            for idx in range(len(data["db_schema"])):
                used_column_ids = [idx for idx, label in enumerate(data["column_labels"][idx]) if label == 1]
                if len(used_column_ids) == 0:
                    continue
                column_pred_probs = list(map(lambda x:round(x,2), data["column_pred_probs"][idx]))
                topk_column_ids = np.argsort(-np.array(column_pred_probs), kind="stable")[:topk_column_num].tolist()
                column_coverage_state_list.append(lista_contains_listb(topk_column_ids, used_column_ids))

        # record top-k1 tables and top-k2 columns for each table
        for table_id in topk_table_ids:
            new_table_info = dict()
            new_table_info["table_name_original"] = data["db_schema"][table_id]["table_name_original"]
            column_pred_probs = list(map(lambda x:round(x,2), data["column_pred_probs"][table_id]))
            topk_column_ids = np.argsort(-np.array(column_pred_probs), kind="stable")[:topk_column_num].tolist()
            
            new_table_info["column_names_original"] = [data["db_schema"][table_id]["column_names_original"][column_id] for column_id in topk_column_ids]
            new_table_info["db_contents"] = [data["db_schema"][table_id]["db_contents"][column_id] for column_id in topk_column_ids]
            
            ranked_data["db_schema"].append(new_table_info)
        
        # record foreign keys among selected tables
        table_names_original = [table["table_name_original"] for table in data["db_schema"]]
        needed_fks = []
        for fk in data["fk"]:
            source_table_id = table_names_original.index(fk["source_table_name_original"])
            target_table_id = table_names_original.index(fk["target_table_name_original"])
            if source_table_id in topk_table_ids and target_table_id in topk_table_ids:
                needed_fks.append(fk)
        ranked_data["fk"] = needed_fks
        
        input_sequence, output_sequence = prepare_input_and_output(use_contents, target_type, add_fk_info, output_skeleton, ranked_data)
        
        # record table_name_original.column_name_original for subsequent correction function during inference
        tc_original = []
        for table in ranked_data["db_schema"]:
            for column_name_original in table["column_names_original"] + ["*"]:
                tc_original.append(table["table_name_original"] + "." + column_name_original)

        output_dataset.append(
            {
                "db_id": data["db_id"],
                "input_sequence": input_sequence, 
                "output_sequence": output_sequence,
                "tc_original": tc_original
            }
        )
    
    with open(output_dataset_path, "w") as f:
        f.write(json.dumps(output_dataset, indent = 2, ensure_ascii = False))
    
    if mode == "eval":
        print("Table top-{} coverage: {}".format(topk_table_num, sum(table_coverage_state_list)/len(table_coverage_state_list)))
        print("Column top-{} coverage: {}".format(topk_column_num, sum(column_coverage_state_list)/len(column_coverage_state_list)))
