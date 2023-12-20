from typing import Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

import streamlit as st


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


@dataclass 
class SqlMessage(Message):
    sql: str
    
    def render(self):
        with st.chat_message('assistant'):
            st.text(self.sql)


@dataclass
class ExecutionMessage(Message):
    data: Any
    
    def render(self):
        with st.chat_message('assistant'):
            st.text(str(self.data))
