import streamlit as st

from gui.resources import load_resdsql_model
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

st.title('🇵🇱 Polish Text-to-SQL')

load_resdsql_model()

tab1, tab2, tab3 = st.tabs([
    '1️⃣ DB Selection',
    '2️⃣ DB Clarification',
    '3️⃣ Chat'
])

with tab1:
    db_path = selection_tab()
with tab2:
    sem_names = clarification_tab(db_path)
with tab3:
    chat_tab(db_path, sem_names)
