from pathlib import Path

import streamlit as st

from gui.translation import trans, lang
from helpers.utils import convert_name_to_sem


def table(table_name, column_names):
    with st.container(border=True):
        st.subheader('🗂 '+table_name)
        table_sem_name = st.text_input(
            label='table name',
            value=convert_name_to_sem(table_name),
            label_visibility='collapsed',
            key=f'table_{table_name}'
        )
        
        st.divider()

        columns_sem_dict = {}
        
        for column_name in column_names:
            column_sem_name = st.text_input(
                label='📊 ' + column_name,
                value=convert_name_to_sem(column_name),
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
    
    file_path = Path('/tmp/uploads') / file.file_id / file.name
    
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file.read())
    
    return file_path


def language_selector(default='pl'):
    options = ['pl', 'en']
    
    gui_texts = {
        'pl': trans('polish'),
        'en': trans('english')
    }
    
    st.selectbox(
        label=trans('lang_label'),
        options=options,
        index=options.index(lang()),
        format_func=lambda lang: gui_texts[lang],
        key='lang_selector',
    )


def ask_panel():
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
                
    return ask_button, clear_button, question
