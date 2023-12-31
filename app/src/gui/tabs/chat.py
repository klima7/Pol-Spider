import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

import streamlit as st
import sqlparse

from gui.resources import load_resdsql_model
from gui.translation import trans
from helpers.database import execute_sql_query
import c3sql


MAX_TABLE_HEIGHT = 200


def chat_tab(db_path, sem_names, openai_api_key):
    if not db_path:
        st.info(trans('complete_1'), icon='⏪')
    else:
        resdsql_model = load_resdsql_model()
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []
                
        for message in st.session_state.messages:
            message.render()
            
        ask_button, clear_button, question, model = ask_panel()
        
        if clear_button:
            st.session_state.messages.clear()
            st.rerun()
                
        if ask_button:
            message = QuestionMessage(question)
            st.session_state.messages.append(message)
                
            if model == 'resdsql':
                response_message = ResdsqlResponseMessage(
                    resdsql_model,
                    db_path,
                    question,
                    sem_names
                )
            elif model == 'c3':
                response_message = C3sqlResponseMessage(
                    openai_api_key,
                    db_path,
                    question,
                    sem_names
                )
            
            st.session_state.messages.append(response_message)
            
            st.rerun()


def ask_panel():
    with st.container():
        col_joined, col_right = st.columns([5, 1])
        
        with col_joined:
            with st.form('send_form', border=False, clear_on_submit=True):
                col_question, col_model, col_ask = st.columns([4, 1, 1])
            
                with col_question:
                    question = st.text_input(
                        label='prompt',
                        placeholder=trans('question_placeholder'),
                        label_visibility='collapsed',
                    )
                    
                with col_model:
                    model = st.selectbox(
                        label='Model',
                        options=['resdsql', 'c3'],
                        index=0,
                        format_func=lambda text: '🤖 ' + text.upper(),
                        key='model_select',
                        label_visibility='collapsed'
                    )
                    
                with col_ask:
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
                
    return ask_button, clear_button, question, model


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
    
    def __init__(self, db_path, question, sem_names, name, avatar=None):
        self.db_path = db_path
        self.question = question
        self.sem_names = sem_names
        self.name = name
        self.avatar = avatar
        
        self.sql = None
        self.data = None
        self.first_render = True
    
    def render(self):
        with st.chat_message(name=self.name, avatar=self.avatar):
            self._predict_sql_if_needed()
            self._render_sql()
            self._render_data()
            
    def _predict_sql_if_needed(self):
        if self.sql is None:
                with st.spinner(trans('thinking')):
                    try:
                        self.sql = self._predict_sql()
                        if isinstance(self.sql, str):
                            self.sql = sqlparse.format(
                                self.sql,
                                reindent=True,
                                keyword_case='upper',
                                identifier_case='lower',
                                # indent_tabs=True,
                            )
                    except Exception as e:
                        self.sql = e

    def _predict_sql(self):
        raise NotImplementedError

    def _render_sql(self):        
        placeholder = st.empty()
        
        if isinstance(self.sql, Exception):
            st.error(str(self.sql), icon='🔥')
        elif self.first_render:
            for idx in range(len(self.sql)):
                placeholder.text(self.sql[:idx+1])
                time.sleep(0.05)
            self.first_render = False
        else:
            placeholder.text(self.sql)
            
        
    def _render_data(self):
        if isinstance(self.sql, Exception):
            return
        
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


class ResdsqlResponseMessage(ResponseMessage):
    
    def __init__(self, model, db_path, question, sem_names=None):
        super().__init__(db_path, question, sem_names, name='RESDSQL')
        self.model = model
    
    def _predict_sql(self):
        return self.model(
            self.question,
            self.db_path,
            self.sem_names
        )


class C3sqlResponseMessage(ResponseMessage):
    
    def __init__(self, openai_api_key, db_path, question, sem_names=None):
        super().__init__(db_path, question, sem_names, name='C3SQL')
        self.openai_api_key = openai_api_key
    
    def _predict_sql(self):
        return c3sql.predict_sql(
            self.question,
            self.db_path,
            self.openai_api_key,
            self.sem_names
        )
