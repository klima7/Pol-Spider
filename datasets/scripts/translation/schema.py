import re

from .deepl_utils import translate_sentence


def create_translation_entries(tables_json):
    tables_ent = []
    columns_ent = []

    for entry in tables_json:
        tables_names = entry['table_names']
        tables_names_original = entry['table_names_original']
        column_names = entry['column_names']
        column_names_original = entry['column_names_original']
        db_id = entry['db_id']
        foreign_keys = entry['foreign_keys']
        primary_keys = entry['primary_keys']
        
        foreign_keys = {a: tables_names[column_names[b][0]] for (a, b) in foreign_keys}
        
        for name, name_original in zip(tables_names, tables_names_original):
            entry = {
                'db_id': db_id,
                'name': name,
                'name_original': name_original,
                'name_pl': name,
                'name_original_pl': name_original
            }
            tables_ent.append(entry)
            
        for column_idx, ((table_idx, name), (_, column_name_original)) in enumerate(zip(column_names, column_names_original)):
            if name == '*':
                continue
            
            entry = {
                'db_id': db_id,
                'table_name_original': tables_names_original[table_idx],
                'column_name': name,
                'column_name_original': column_name_original,
                'primary_key': column_idx in primary_keys,
                'foreign_key': foreign_keys.get(column_idx, ''),
                'column_name_pl': name,
                'column_name_original_pl': column_name_original,
            }
            columns_ent.append(entry)
            
    return tables_ent, columns_ent


def translate_name(name, container_name, other_container_name=None):
    container_name = re.sub(r'[^a-zA-Z ]', ' ', container_name)
    if not other_container_name:
        text = f"{name} (from {container_name})"
    else:
        other_container_name = re.sub(r'[^a-zA-Z ]', ' ', other_container_name)
        text = f"{name} (from {container_name} and {other_container_name})"
    text_pl = translate_sentence(text)
    paren_idx = text_pl.index('(')
    return text_pl[:paren_idx].strip()


def translate_original_name(name, container, other_container=None):
    natural_text_en = name.replace('_', ' ')
    was_titled = all(word[0]==word[0].upper() and word[1:]==word[1:].lower() for word in natural_text_en.split(' '))
    natural_text_pl = translate_name(natural_text_en, container, other_container)
    if was_titled:
        natural_text_pl = natural_text_pl.title()
    return natural_text_pl.replace(' ', "_")
