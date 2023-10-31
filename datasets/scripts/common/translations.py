from common import load_json


class SchemaTranslation:
    
    def __init__(self, json):
        self.dbs = {db_id: DbTranslation(db_json) for db_id, db_json in json.items()}
        
    @classmethod
    def load(cls, path):
        return cls(load_json(path))
        
    def __getitem__(self, db_name):
        return self.dbs[db_name]
    
    @property
    def dbs_names(self):
        return list(self.dbs.keys())
    
    
class DbTranslation:
    
    def __init__(self, db_json):
        self.tables = {table['orig_src'].lower(): TableTranslation(table) for table in db_json}
        
    def __getitem__(self, table_name):
        return self.tables[table_name.lower()]
    
    @property
    def tables_names(self):
        return list(self.tables.keys())
    

class TableTranslation:
    
    def __init__(self, table_json):
        self.name = table_json['name_tgt']
        self.orig = table_json['orig_tgt']
        self.columns = {column['orig_src'].lower(): ColumnTranslation(column) for column in table_json['columns']}
    
    def __getitem__(self, column_name):
        return self.columns[column_name.lower()]
    
    @property
    def columns_names(self):
        return list(self.columns.keys())
    
    
class ColumnTranslation:
    
    def __init__(self, column_json):
        self.name = column_json['name_tgt']
        self.orig = column_json['orig_tgt']
