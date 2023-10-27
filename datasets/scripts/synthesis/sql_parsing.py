from .third_party.process_sql import get_sql
from .third_party.parse_sql_one import Schema, get_schemas_from_json


class SQLParseException(Exception):
    pass


def create_sql(db_id, query, schemas, tables):
    try:
        schema = schemas[db_id]
        table = tables[db_id]
        schema = Schema(schema, table)
        sql_label = get_sql(schema, query)
        return sql_label
    except Exception:
        raise SQLParseException()
