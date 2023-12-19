import streamlit as st
import streamlit_ace
from streamlit_ace import st_ace
import random


SQL_SCHEMA_PLACEHOLDER = """
CREATE TABLE klienci(
    ...
)

CREATE TABLE zamowienia(
    ...
)
"""

def table():
    with st.container(border=True):
        st.subheader('DzienWynajmu')
        _ = st.text_input(label='nazwa tabeli', value='nazwa filmu', label_visibility='hidden', key=random.randint(0, 100000))
        
        st.divider()

        for i in range(random.randint(3, 7)):
            _ = st.text_input(label='fnazwa', value='nazwa filmu', key=random.randint(0, 100000))


st. set_page_config(layout="wide")

st.title('Polish Text-to-SQL')

# st.text('Upload SQLite database file or enter its schema in area bellow')

db = st.file_uploader(
    label='Upload SQLite database here or enter its schema in area bellow',
    type=['sqlite'],
    accept_multiple_files=False,
)

sql_schema = st_ace(
    language='sql',
    height=500,
    placeholder=SQL_SCHEMA_PLACEHOLDER,
    theme='dracula',
    keybinding='vscode',
    show_gutter=False,
    font_size=16,
    auto_update=False,
)

if False:
    col1, col2, col3 = st.columns(3)

    with col1:
        table()
        table()
        table()
        
    with col2:
        table()
        table()
        
    with col3:
        table()
        table()
    
    st.divider()
    
with st.expander('📥 Import / 📤 export config'):
    db = st.file_uploader(
        label='Import',
        accept_multiple_files=False,
        # label_visibility='hidden'
    )
    st.button(label='Export', use_container_width=True)
    # st.button(label='📥 Import config', use_container_width=True)
