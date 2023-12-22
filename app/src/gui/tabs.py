import streamlit as st
from streamlit_ace import st_ace

from gui.constants import *
from gui.messages import QuestionMessage, ResponseMessage
from gui.components import table, uploader_enhanced, ask_panel
from gui.resources import load_resdsql_model
from gui.translation import trans
from helpers.utils import (
    get_sql_from_db,
    get_db_from_sql,
    get_schema_image_from_db,
    get_error_from_sql,
    get_schema_dict_from_db,
    divide_schema_dict,
)


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


def clarification_tab(db_path):
    if not db_path:
        st.info(trans('complete_1'), icon='⏪')
        return None
    else:
        schema_dict = get_schema_dict_from_db(db_path)
        
        form = st.form("clar_form", border=False)
        with form:
            st.form_submit_button(trans('apply'), use_container_width=True, type='primary')
            clar_columns = st.columns(CLAR_COLUMNS)
            schema_dict_groups = divide_schema_dict(schema_dict, CLAR_COLUMNS)

            sem_names = {}

            for column, schema_dict_group in zip(clar_columns, schema_dict_groups):
                with column:
                    for table_name, table_columns in schema_dict_group.items():
                        table_sem, columns_sem = table(table_name, table_columns)
                        sem_names[table_name] = (table_sem, columns_sem)
                        
        return sem_names
    
    
def chat_tab(db_path, sem_names):
    if not db_path:
        st.info(trans('complete_1'), icon='⏪')
    else:
        resdsql_model = load_resdsql_model()
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []
                
        for message in st.session_state.messages:
            message.render()
            
        ask_button, clear_button, question = ask_panel()
        
        if clear_button:
            st.session_state.messages.clear()
            st.rerun()
                
        if ask_button:
            message = QuestionMessage(question)
            st.session_state.messages.append(message)
                
            sql_message = ResponseMessage(
                resdsql_model,
                db_path,
                question,
                sem_names
            )
            st.session_state.messages.append(sql_message)
            
            st.rerun()
