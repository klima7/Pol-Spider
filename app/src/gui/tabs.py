import streamlit as st
from streamlit_ace import st_ace

from gui.constants import *
from gui.messages import QuestionMessage, ResponseMessage
from gui.components import table, uploader_enhanced
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
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        with st.container():
            col_joined, col_right = st.columns([5, 1])
            
            with col_joined:
                with st.form('send_form', border=False, clear_on_submit=True):
                    col_left, col_center = st.columns([4, 1])
                
                    with col_left:
                        question = st.text_input(
                            label='prompt',
                            placeholder=trans('question_placeholder'),
                            label_visibility='collapsed',
                        )
                        
                    with col_center:
                        ask_button = st.form_submit_button(
                            label=trans('ask'),
                            type='secondary',
                            use_container_width=True
                        )
                
            with col_right:
                clear_button = st.button(
                    label=trans('clear'),
                    type='secondary',
                    use_container_width=True
                )
                
                if clear_button:
                    st.session_state.messages.clear()
                    
        resdsql_model = load_resdsql_model()
                
        for message in st.session_state.messages:
            message.render()
                
        if ask_button:
            message = QuestionMessage(question)
            message.render()
            st.session_state.messages.append(message)
                
            sql_message = ResponseMessage(
                resdsql_model,
                db_path,
                question,
                sem_names
            )
            st.session_state.messages.append(sql_message)
            sql_message.render()
