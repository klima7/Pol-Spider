import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import streamlit as st
from streamlit_ace import st_ace

from gui.components import uploader_enhanced
from gui.translation import trans
from helpers.database import (
    get_sql_from_db,
    get_db_from_sql,
    get_schema_image_from_db,
    get_error_from_sql,
)


SQL_SCHEMA_PLACEHOLDER = """
CREATE TABLE klienci(
    ...
)

CREATE TABLE zamowienia(
    ...
)
"""


EXAMPLES_PATH = Path('../db')


def selection_tab():
    # upload new
    st.subheader(trans('upload_db'))
    db_path = uploader_enhanced(
        label=trans('upload_db'),
        type=['sqlite'],
        label_visibility='collapsed',
    )
    
    # select example
    st.subheader(trans('select_example'))
    examples_dict = {e.path: e for e in get_examples()}
    db_path_new = st.selectbox(
        label='',
        options=examples_dict.keys(),
        index=0,
        format_func=lambda path: examples_dict[path].disp_name,
        label_visibility='collapsed',
    )
    db_path = db_path or db_path_new

    # provide sql
    st.subheader(trans('provide_sql'))
    db_path_new = sql_schema_input(db_path)
    db_path = db_path or db_path_new
    
    # graph
    if db_path:
        schema_image = get_schema_image_from_db(db_path)
        st.subheader(trans('graph_title'))
        st.image(schema_image)
        
    return db_path


def sql_schema_input(db_path):
    sql_from_db = get_sql_from_db(db_path) if db_path else ''
    schema_sql = st_ace(
        value=sql_from_db,
        language='sql',
        height=500,
        placeholder=SQL_SCHEMA_PLACEHOLDER,
        theme='dracula',
        keybinding='vscode',
        show_gutter=False,
        font_size=16,
        auto_update=False,
        readonly=(db_path is not None)
    )
    
    schema_error = get_error_from_sql(schema_sql)
    
    if schema_error:
        st.error(f'{trans("schema_error")}: {schema_error}', icon="🔥")
        
    elif len(schema_sql) > 0:
        if db_path is None:
            db_path = get_db_from_sql(schema_sql)



@dataclass
class ExampleDb:
    name: str
    path: Optional[Path] = None
    description: Optional[dict] = None
    schema: Optional[str] = None
    content: Optional[str] = None
    
    @property
    def disp_name(self):
        if self.path is None:
            return self.name
        else:
            return f"{self.name} ({trans('schema')}: {trans(self.schema)})"
            # return f"{self.name} ({trans('schema')}: {trans(self.schema)}, {trans('content')}: {trans(self.content)})"


def get_examples():
    examples = []
    for db_path in EXAMPLES_PATH.glob('**/*.sqlite'):
        meta_path = db_path.parent / 'metadata.json'
        with open(meta_path) as f:
            meta = json.load(f)
        example = ExampleDb(path=db_path, **meta)
        examples.append(example)
        
    nothing_example = ExampleDb(name=trans('nothing'))
    examples = list(sorted(examples, key=lambda e: e.name[2:]))
    return [nothing_example, *examples]
