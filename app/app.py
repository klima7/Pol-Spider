import tempfile
import random
from pathlib import Path

import streamlit as st
import streamlit_ace
from streamlit_ace import st_ace
import numpy as np

from utils import get_sql_from_db, get_schema_image_from_sql, get_error_from_sql, get_schema_dict_from_sql, divide_schema_dict


SQL_SCHEMA_PLACEHOLDER = """
CREATE TABLE klienci(
    ...
)

CREATE TABLE zamowienia(
    ...
)
"""


UPLOADS_DIR = Path('/tmp/uploads')

CLAR_COLUMNS = 3


def table(table_name, column_names):
    with st.container(border=True):
        st.subheader('🗂 '+table_name)
        _ = st.text_input(
            label='table name',
            value=table_name,
            label_visibility='collapsed',
            key=f'table_{table_name}'
        )
        
        st.divider()

        for column_name in column_names:
            _ = st.text_input(
                label='📊 ' + column_name,
                value=column_name,
                key=f'column_{table_name}_{column_name}'
            )


def uploader_enhanced(*args, **kwargs):
    file = st.file_uploader(
        *args,
        **kwargs,
        accept_multiple_files=False,
    )
    
    if file is None:
        return None
    
    file_path = UPLOADS_DIR / file.file_id / file.name
    
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file.read())
    
    return file_path


st. set_page_config(layout="wide")

st.title('🇵🇱 Polish Text-to-SQL')

tab1, tab2, tab3 = st.tabs(["1️⃣ DB Selection", "2️⃣ DB Clarification ", "3️⃣ Chat"])

with tab1:
    db_path = uploader_enhanced(
        label='Upload SQLite database here or enter only its schema in area bellow',
        type=['sqlite']
    )

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
    schema_ok = len(schema_sql) > 0 and schema_error is None
    
    if schema_error:
        st.error(f'Schema Error: {schema_error}', icon="🚨")

    if schema_ok:
        schema_image = get_schema_image_from_sql(schema_sql)
        st.image(schema_image)
        
        schema_dict = get_schema_dict_from_sql(schema_sql)
        
    # with st.expander('📥 Import / 📤 export config'):
    #     db = st.file_uploader(
    #         label='Import',
    #         accept_multiple_files=False,
    #     )
    #     st.button(label='Export', use_container_width=True)

with tab2:
    if not schema_ok:
        st.info('Complete tab 1 first', icon='⏪')
    else:
        form = st.form("send_form", border=False)
        with form:
            st.form_submit_button('Apply', use_container_width=True, type='primary')
            clar_columns = st.columns(CLAR_COLUMNS)
            schema_dict_groups = divide_schema_dict(schema_dict, CLAR_COLUMNS)

            for column, schema_dict_group in zip(clar_columns, schema_dict_groups):
                with column:
                    for table_name, table_columns in schema_dict_group.items():
                        table(table_name, table_columns)


with tab3:
    if not schema_ok:
        st.info('Complete tab 1 first', icon='⏪')
    else:
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                prompt = st.text_input(
                    label='prompt',
                    placeholder='Ask about anything',
                    label_visibility='collapsed',
                )
                
            with col2:
                ask_button = st.button(
                    label='Ask ❓',
                    type='secondary',
                    use_container_width=True
                )
                
            with col3:
                clear_button = st.button(
                    label='Clear 🗑️',
                    type='secondary',
                    use_container_width=True
                )
                
        with st.chat_message('user'):
            st.write('Jaki jast najstarszy pracownik w dziale finansów?')
        with st.chat_message('assistant'):
            st.write('SELECT * form department')
        with st.chat_message('assistant'):
            st.write('How are you?')
        
        with st.chat_message('user'):
            st.write('Jaki jast najstarszy pracownik w dziale finansów?')
        with st.chat_message('assistant'):
            st.write('SELECT * form department')
        with st.chat_message('assistant'):
            st.write('How are you?')
            
        with st.chat_message('user'):
            st.write('Jaki jast najstarszy pracownik w dziale finansów?')
        with st.chat_message('assistant'):
            st.write('SELECT * form department')
        with st.chat_message('assistant'):
            st.write('How are you?')

        
        