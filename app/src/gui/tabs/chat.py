import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

import streamlit as st

from gui.resources import load_resdsql_model
from gui.translation import trans
from helpers.database import execute_sql_query


MAX_TABLE_HEIGHT = 200


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
    
    def __init__(self, model, db_path, question, sem_names=None):
        self.model = model
        self.db_path = db_path
        self.question = question
        self.sem_names = sem_names
        
        self.sql = None
        self.data = None
        self.first_render = True
    
    
    def render(self):
        with st.chat_message('assistant'):
            self._render_sql()
            self._render_data()
            

    def _render_sql(self):
        if self.sql is None:
            with st.spinner(trans('thinking')):
                self.sql = self.model(
                    self.question,
                    self.db_path,
                    self.sem_names
                )
                
        placeholder = st.empty()
        
        if self.first_render:
            for idx in range(len(self.sql)):
                placeholder.text(self.sql[:idx+1])
                time.sleep(0.05)
            self.first_render = False
        else:
            placeholder.text(self.sql)
            
        
    def _render_data(self):
        if self.data is None:
            with st.spinner(trans('executing')):
                time.sleep(1)
                self.data = execute_sql_query(self.db_path, self.sql)
        
        if isinstance(self.data, Exception):
            st.error(str(self.data), icon='🔥')
        else:
            height = MAX_TABLE_HEIGHT if len(self.data) > 1 else 50
            st.dataframe(
                self.data,
                use_container_width=True,
                height=height,
            )
