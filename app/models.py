import time
from dataclasses import dataclass
from abc import ABC, abstractmethod

import streamlit as st
from predict import predict_sql
from utils import execute_sql_query


class Message(ABC):
    
    @abstractmethod
    def render(self):
        pass


@dataclass
class QuestionMessage(Message):
    question: str
    
    def render(self):
        with st.chat_message('user'):
            st.text(self.question)


class ResponseMessage(Message):
    
    def __init__(self, db_path: str, question: str):
        self.db_path = db_path
        self.question = question
        self.sql = None
        self.data = None
    
    
    def render(self):
        with st.chat_message('assistant'):
            self._render_sql()
            self._render_data()
            

    def _render_sql(self):
        if self.sql is None:
            with st.spinner('Thinking...'):
                self.sql = predict_sql()
                
        st.text(self.sql)
        
    def _render_data(self):
        if self.data is None:
            with st.spinner('Executing...'):
                time.sleep(1)
                self.data = execute_sql_query(self.db_path, self.sql)
        
        if isinstance(self.data, Exception):
            st.error(str(self.data), icon='🔥')
        else:
            height = 200 if len(self.data) > 1 else 50
            st.dataframe(
                self.data,
                use_container_width=True,
                height=height,
            )
