import re

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


class BaseSchemaTranslation:
    
    def translate_table_name(self, table_entry):
        return ''
    
    def translate_table_name_original(self, table_entry):
        return ''
    
    def translate_column_name(self, column_entry, table_entry, all_tables_entry):
        return ''
    
    def translate_column_name_original(self, column_entry, table_entry, all_tables_entry):
        return ''
    
    
class NoContextSchemaTranslation(BaseSchemaTranslation):
    
    def translate_table_name(self, table_entry):
        return translate_phrase(table_entry['name'])
    
    def translate_table_name_original(self, table_entry):
        return translate_phrase(table_entry['name'])
    
    def translate_column_name(self, column_entry, table_entry, all_tables_entry):
        return translate_phrase(column_entry['column_name'])
    
    def translate_column_name_original(self, column_entry, table_entry, all_tables_entry):
        return translate_phrase(column_entry['column_name'])
    

class DoubleSchemaTranslation(BaseSchemaTranslation):
    
    def translate_table_name(self, table_entry):
        return self._translate_name(table_entry['name'], table_entry['db_id'])
    
    def translate_table_name_original(self, table_entry):
        return self._translate_original_name(table_entry['name_original'], table_entry['db_id'])
    
    def translate_column_name(self, column_entry, table_entry, all_tables_entry):
        return self._translate_name(column_entry['column_name'], table_entry['name'], column_entry['db_id'])
    
    def translate_column_name_original(self, column_entry, table_entry, all_tables_entry):
        return self._translate_original_name(column_entry['column_name_original'], table_entry['name'], column_entry['db_id'])

    def _translate_name(self, name, container_name, other_container_name=None):
        container_name = self._naturalize_name(container_name)
        if not other_container_name:
            text = f"{name} (from {container_name})"
        else:
            other_container_name = self._naturalize_name(other_container_name)
            text = f"{name} (from {container_name} and {other_container_name})"
        print(text)
        text_pl = translate_sentence(text)
        print(text_pl)
        paren_idx = text_pl.index('(')
        return text_pl[:paren_idx].strip()
    
    def _naturalize_name(self, name):
        return re.sub(r'[^a-zA-Z ]', ' ', name)

    def _translate_original_name(self, name, container, other_container=None):
        natural_text_en = name.replace('_', ' ')
        was_titled = all(word[0]==word[0].upper() and word[1:]==word[1:].lower() for word in natural_text_en.split(' '))
        natural_text_pl = self._translate_name(natural_text_en, container, other_container)
        if was_titled:
            natural_text_pl = natural_text_pl.title()
        return natural_text_pl.replace(' ', "_")
