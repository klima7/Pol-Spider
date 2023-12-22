import streamlit as st

from resdsql import ResdsqlModel


@st.cache_resource
def load_resdsql_model():
    device="0"
    return ResdsqlModel(
        classifier_path='../models/classifier',
        text2sql_path='../models/text2sql',
        classifier_device=device,
        text2sql_device=device,
        num_beams=8,
        num_return_sequences=8
    )
