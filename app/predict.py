import time
import random

import streamlit as st


def predict_sql(question, sem_names):
    time.sleep(1)
    # st.write(question)
    # st.json(sem_names)
    return random.choice([
        "SELECT * FROM student",
        "SELECT imie FROM student",
    ])
