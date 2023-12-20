import tempfile
import random
import time
from pathlib import Path

import streamlit as st
import streamlit_ace
from streamlit_ace import st_ace
import numpy as np

from models import *
from utils import get_sql_from_db, get_db_from_sql, get_schema_image_from_sql, get_error_from_sql, get_schema_dict_from_sql, divide_schema_dict


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
        table_sem_name = st.text_input(
            label='table name',
            value=table_name,
            label_visibility='collapsed',
            key=f'table_{table_name}'
        )
        
        st.divider()

        columns_sem_dict = {}
        
        for column_name in column_names:
            column_sem_name = st.text_input(
                label='📊 ' + column_name,
                value=column_name,
                key=f'column_{table_name}_{column_name}'
            )
            columns_sem_dict[column_name] = column_sem_name
            
    return table_sem_name, columns_sem_dict


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

if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title('🇵🇱 Polish Text-to-SQL')

tab1, tab2, tab3 = st.tabs(["1️⃣ DB Selection", "2️⃣ DB Clarification ", "3️⃣ Chat"])

with tab1:
    with st.expander('📥 Import / 📤 export config'):
        db = st.file_uploader(
            label='Import',
            accept_multiple_files=False,
            label_visibility='collapsed'
        )
        st.button(label='Export', use_container_width=True, type='primary')
    
    st.subheader('Upload any SQLite database...')
    
    db_path = uploader_enhanced(
        label='Upload SQLite database here or enter only its schema in area bellow',
        type=['sqlite'],
        label_visibility='collapsed',
    )

    sql_from_db = get_sql_from_db(db_path) if db_path else ''

    st.subheader('...Or provide SQL for schema creation')
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
        st.error(f'Schema Error: {schema_error}', icon="🔥")
    
    if schema_ok:
        schema_image = get_schema_image_from_sql(schema_sql)
        st.subheader('This is graph of provided database')
        st.image(schema_image)
        
        schema_dict = get_schema_dict_from_sql(schema_sql)
        
    if schema_ok and db_path is None:
        db_path = get_db_from_sql(schema_sql)

with tab2:
    if not schema_ok:
        st.info('Complete tab 1 first', icon='⏪')
    else:
        form = st.form("clar_form", border=False)
        with form:
            st.form_submit_button('Apply', use_container_width=True, type='primary')
            clar_columns = st.columns(CLAR_COLUMNS)
            schema_dict_groups = divide_schema_dict(schema_dict, CLAR_COLUMNS)

            sem_names = {}

            for column, schema_dict_group in zip(clar_columns, schema_dict_groups):
                with column:
                    for table_name, table_columns in schema_dict_group.items():
                        table_sem, columns_sem = table(table_name, table_columns)
                        sem_names[table_name] = (table_sem, columns_sem)


with tab3:
    if not schema_ok:
        st.info('Complete tab 1 first', icon='⏪')
    else:
        with st.container():
            col_joined, col_right = st.columns([5, 1])
            
            with col_joined:
                with st.form('send_form', border=False, clear_on_submit=True):
                    col_left, col_center = st.columns([4, 1])
                
                    with col_left:
                        question = st.text_input(
                            label='prompt',
                            placeholder='Ask about anything',
                            label_visibility='collapsed',
                        )
                        
                    with col_center:
                        ask_button = st.form_submit_button(
                            label='Ask ❓',
                            type='secondary',
                            use_container_width=True
                        )
                
            with col_right:
                clear_button = st.button(
                    label='Clear 🗑️',
                    type='secondary',
                    use_container_width=True
                )
                
                if clear_button:
                    st.session_state.messages.clear()
                
        for message in st.session_state.messages:
            message.render()
                
        if ask_button:
            message = QuestionMessage(question)
            message.render()
            st.session_state.messages.append(message)
                
            time.sleep(0.5)
                
            sql_message = ResponseMessage(db_path, question, sem_names)
            st.session_state.messages.append(sql_message)
            sql_message.render()
