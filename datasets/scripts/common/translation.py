from common import load_json, save_json


class SchemaTranslation:
    
    def __init__(self, json):
        self.dbs = {db_id: DbTranslation(db_json) for db_id, db_json in json.items()}
        
    @classmethod
    def load(cls, path):
        return cls(load_json(path))
        
    def __getitem__(self, db_name):
        return self.dbs[db_name]
    
    def __iter__(self):
        return iter(self.dbs_names)
    
    @property
    def dbs_names(self):
        return list(self.dbs.keys())
    
    def to_json(self):
        return {db_id: db.to_json() for db_id, db in self.dbs.items()}
    
    def save(self, path):
        save_json(path, self.to_json())
    
    
class DbTranslation:
    
    def __init__(self, db_json):
        self.tables = {table['orig_src'].lower(): TableTranslation(table) for table in db_json}
        
    def __getitem__(self, table_name):
        return self.tables[table_name.lower()]
    
    def __iter__(self):
        return iter(self.tables_names)
    
    @property
    def tables_names(self):
        return list(self.tables.keys())
    
    def to_json(self):
        return [table.to_json() for table in self.tables.values()]
    

class TableTranslation:
    
    def __init__(self, table_json):
        self.name = table_json['name_tgt']
        self.orig = table_json['orig_tgt']
        self.name_src = table_json['name_src']
        self.orig_src = table_json['orig_src']
        self.columns = {column['orig_src'].lower(): ColumnTranslation(column) for column in table_json['columns']}
    
    def __getitem__(self, column_name):
        return self.columns[column_name.lower()]
    
    def __iter__(self):
        return iter(self.columns_names)
    
    @property
    def columns_names(self):
        return list(self.columns.keys())
    
    def to_json(self):
        return {
            'name_src': self.name_src,
            'name_tgt': self.name,
            'orig_src': self.orig_src,
            'orig_tgt': self.orig,
            'columns': [column.to_json() for column in self.columns.values()]
        }
    
    
class ColumnTranslation:
    
    def __init__(self, column_json):
        self.name = column_json['name_tgt']
        self.orig = column_json['orig_tgt']
        self.name_src = column_json['name_src']
        self.orig_src = column_json['orig_src']

    def to_json(self):
        return {
            'name_src': self.name_src,
            'name_tgt': self.name,
            'orig_src': self.orig_src,
            'orig_tgt': self.orig
        }
