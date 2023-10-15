import json



def load_table_translations(tables_names_path):
    with open(tables_names_path, encoding="utf-8") as f:
        tables_names = json.load(f)

    tables_trans = {}

    for entry in tables_names:
        if entry["db_id"] not in tables_trans:
            tables_trans[entry["db_id"]] = {}

        translation = {
            "name": entry["name_pl"],
            "name_original": entry["name_original_pl"],
        }
        tables_trans[entry["db_id"]][entry["name_original"].lower()] = translation

    return tables_trans


def load_column_translations(columns_names_path):
    with open(columns_names_path, encoding="utf-8") as f:
        columns_names = json.load(f)

    columns_trans = {}

    for entry in columns_names:
        if entry["db_id"] not in columns_trans:
            columns_trans[entry["db_id"]] = {}
        db_stuff = columns_trans[entry["db_id"]]

        if entry["table_name_original"].lower() not in db_stuff:
            db_stuff[entry["table_name_original"].lower()] = {}
        table_stuff = db_stuff[entry["table_name_original"].lower()]

        translation = {
            "name": entry["column_name_pl"],
            "name_original": entry["column_name_original_pl"],
        }
        table_stuff[entry["column_name_original"].lower()] = translation

    return columns_trans
