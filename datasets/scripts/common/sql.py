import sqlglot


def get_tables_names(query: str | sqlglot.Expression):
    if isinstance(query, str):
        query = sqlglot.parse_one(query, dialect=sqlglot.dialects.SQLite)
    
    tables_1 = [table.this.output_name for table in query.find_all(sqlglot.exp.Table)]
    tables_2 = [col.table for col in query.find_all(sqlglot.exp.Column) if col.table != '']
    tables_3 = [alias.this.output_name for alias in query.find_all(sqlglot.exp.TableAlias)]
    tables = [*tables_1, *tables_2, *tables_3]
    return tables


def get_columns_names(query: str | sqlglot.Expression):
    if isinstance(query, str):
        query = sqlglot.parse_one(query, dialect=sqlglot.dialects.SQLite)
        
    columns = [
        col.output_name
        for col in query.find_all(sqlglot.exp.Column)
        if col.this.quoted == False
    ]
    return columns
