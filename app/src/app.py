import os

import streamlit as st

from gui.resources import load_resdsql_model
from gui.translation import language_selector, trans
from gui.tabs import (
    selection_tab,
    clarification_tab,
    chat_tab
)


st.set_page_config(
    page_title='Text2SQL',
    page_icon='🇵🇱',
    layout='wide'
)

if os.environ.get('OPENAI_API_KEY') is not None:
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title(trans('title'))
    with col2:
        language_selector()
else:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title(trans('title'))
    with col2:
        openai_api_key = st.text_input(
            label=trans('openai_api_key'),
            type='password'
        )
    with col3:
        language_selector()

load_resdsql_model()

tab1, tab2, tab3 = st.tabs([
    trans('selection_tab'),
    trans('clarification_tab'),
    trans('chat_tab')
])

with tab1:
    db_path = selection_tab()
with tab2:
    sem_names = clarification_tab(db_path)
with tab3:
    chat_tab(db_path, sem_names, openai_api_key)
