import re

from tqdm import tqdm

from common import load_json, save_json
from .deepl_utils import translate_sentence, translate_phrase


def create_translation_entries(tables_json):
    tables_entries = []
    columns_entries = []

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
            tables_entries.append(entry)
            
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
            columns_entries.append(entry)
            
    return tables_entries, columns_entries


def translate_tables(
        table_trans_path,
        translation,
        translate_name=False,
        translate_name_original=False
    ):
    
    entries = load_json(table_trans_path)
    
    for i, entry in enumerate(tqdm(entries, desc='Translating tables')):
        if translate_name:
            translation.translate_table_name(entry)
        if translate_name_original:
            translation.translate_table_name_original(entry)
        if i % 20 == 0:
            save_json(table_trans_path, entries)
            
    save_json(table_trans_path, entries)
    
    
def translate_columns(
        column_trans_path,
        table_trans_path,
        translation,
        translate_name=False,
        translate_name_original=False
    ):
    
    column_entries = load_json(column_trans_path)
    table_entries = load_json(table_trans_path)
    
    for i, column_entry in enumerate(tqdm(column_entries, desc='Translating columns')):
        table_entry = [
            te for te in table_entries 
            if te['db_id'] == column_entry['db_id'] and \
                te['name_original'] == column_entry['table_name_original']
        ][0]
    
        if translate_name:
            translation.translate_column_name(column_entry, table_entry)
        if translate_name_original:
            translation.translate_column_name_original(column_entry, table_entry)
        if i % 20 == 0:
            save_json(column_trans_path, column_entries)
            
    save_json(column_trans_path, column_entries)


class BaseSchemaTranslation:
    
    def translate_table_name(self, table_entry):
        table_entry['name_pl'] = self._translate_name(
            table_entry['name'],
            table_entry['db_id']
        )
    
    def translate_column_name(self, column_entry, table_entry):
        column_entry['column_name_pl'] = self._translate_name(
            column_entry['column_name'],
            table_entry['name'],
            column_entry['db_id']
        )
    
    def translate_table_name_original(self, table_entry):
        # 'sqlite_sequence' is special table - do not translate its name
        if table_entry['name_original'] == 'sqlite_sequence':
            table_entry['name_original_pl'] = table_entry['name_original']
            return
        
        table_entry['name_original_pl'] = self._translate_name_original(
            table_entry['name_original'],
            table_entry['db_id']
        )
    
    def translate_column_name_original(self, column_entry, table_entry):
        # 'sqlite_sequence' is special table - do not translate its columns
        if column_entry['table_name_original'] == 'sqlite_sequence':
            column_entry['column_name_original_pl'] = column_entry['column_name_original']
            return
        
        column_entry['column_name_original_pl'] = self._translate_name_original(
            column_entry['column_name_original'],
            table_entry['name'],
            column_entry['db_id']
        )

    def _translate_name_original(self, name, db_name, table_name=None):
        name, id_suffix = self._strip_id_suffix_from_name(name, '_')
        name = name.replace('_', ' ')
        was_titled = name.title() == name
        name_pl = self._translate(name, db_name, table_name)
        if was_titled:
            name_pl = name_pl.title()
        name_pl = name_pl.replace(' ', '_') + id_suffix
        name_pl = self._sanitize_name(name_pl)
        return name_pl

    def _naturalize_name(self, name):
        return re.sub(r'[^a-z ]', ' ', name, flags=re.IGNORECASE)
    
    def _sanitize_name(self, name):
        return re.sub('[^a-z0-9_ąćźóęśżłń]+', '', name, flags=re.IGNORECASE)
    
    def _strip_id_suffix_from_name(self, name, separator):
        if name.lower().endswith(f'{separator}id'):
            rest = ''.join(list(name)[:-3])
            suffix = ''.join(list(name)[-3:])
        else:
            rest = name
            suffix = ''
        return rest, suffix
        
    def _translate_name(self, name, db_name, table_name=None):
        name, id_suffix = self._strip_id_suffix_from_name(name, ' ')
        name_pl = self._translate(name, db_name, table_name)
        name_pl = name_pl + id_suffix
        return name_pl
        
    def _translate(self, name, db_name, table_name=None):
        raise NotImplementedError()
    
    
class NoContextSchemaTranslation(BaseSchemaTranslation):
    
    def _translate(self, name, db_name, table_name=None):
        return translate_phrase(name)
    

class ContextSchemaTranslation(BaseSchemaTranslation):
    
    def _translate(self, name, db_name, table_name=None):
        return self._translate_name_in_context(name, db_name, table_name)

    def _translate_name_in_context(self, name, db_name, table_name=None):
        # To not translate id to longer form, like identifier
        if name.lower() == 'id':
            return name
        
        db_name = self._naturalize_name(db_name)
        context = f"from {db_name}"
        if table_name:
            table_name = self._naturalize_name(table_name)
            context += f" and {table_name})"
            
        text_pl = translate_sentence(f'{name} ({context})')
        paren_idx = text_pl.index('(')
        translated_name = text_pl[:paren_idx].strip()
        return translated_name
