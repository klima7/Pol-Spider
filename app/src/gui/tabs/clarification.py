import streamlit as st

from gui.translation import trans
from helpers.database import (
    get_schema_dict_from_db,
    divide_schema_dict,
)


CLAR_COLUMNS = 3


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


def table(table_name, column_names):
    with st.container(border=True):
        st.subheader('📋 '+table_name)
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


def convert_name_to_sem(name):
    if len(name) == 0:
        return name
    
    sem_name = name[0]
    
    for letter in name[1:]:
        prev_letter = sem_name[-1]
        if prev_letter.islower() and letter.isupper():
            sem_name += ' '
        sem_name += letter
        
    sem_name = sem_name.replace('_', ' ').lower()
        
    return sem_name
