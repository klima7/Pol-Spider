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


def selection_tab():
    st.subheader(trans('upload_db'))
    
    db_path = uploader_enhanced(
        label=trans('upload_db'),
        type=['sqlite'],
        label_visibility='collapsed',
    )

    sql_from_db = get_sql_from_db(db_path) if db_path else ''

    st.subheader(trans('provide_sql'))
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
        
        schema_image = get_schema_image_from_db(db_path)
        st.subheader(trans('graph_title'))
        st.image(schema_image)
        
    return db_path
