import streamlit as st


DEFAULT_LANG = 'en'


ALL_TRANSLATIONS = {
    "title": {
        "en": "🏳 Polish Text-to-SQL",
        "pl": "🏳 Polskie Text-to-SQL"
    },
    "lang_label": {
        "en": "Interface language",
        "pl": "Język interfejsu"
    },
    "polish": {
        "en": "polish",
        "pl": "polski"
    },
    "english": {
        "en": "english",
        "pl": "angielski"
    },
    "openai_api_key": {
        "en": "OpenAI API key",
        "pl": "Klucz API dla OpenAI"
    },
    "selection_tab": {
        "en": "1️⃣ DB Selection",
        "pl": "1️⃣ Wybór Bazy"
    },
    "clarification_tab": {
        "en": "2️⃣ DB Clarification",
        "pl": "2️⃣ Objaśnienie Nazw"
    },
    "chat_tab": {
        "en": "3️⃣ Chat",
        "pl": "3️⃣ Chat"
    },
    "upload_db": {
        "en": "Upload SQLite database ...",
        "pl": "Załaduj bazę danych SQLite ..."
    },
    "provide_sql": {
        "en": "... Or provide SQL for schema creation",
        "pl": "... Lub dostarcz skrypt SQL tworzący schemat"
    },
    "select_example": {
        "en": "... Or select example database",
        "pl": "... Lub wybierz przykładową bazę"
    },
    "nothing": {
        "en": "🕳️ Nothing",
        "pl": "🕳️ Brak"
    },
    "schema": {
        "en": "schema",
        "pl": "schemat"
    },
    "content": {
        "en": "content",
        "pl": "zawartość"
    },
    "graph_title": {
        "en": "Graph of provided database",
        "pl": "Diagram wybranej bazy danych"
    },
    "schema_error": {
        "en": "Schema Error",
        "pl": "Błąd w schemacie"
    },
    "complete_1": {
        "en": "Complete tab 1 first",
        "pl": "Ukończ najpierw zakładkę 1"
    },
    "apply": {
        "en": "Apply",
        "pl": "Zastosuj"
    },
    "ask": {
        "en": "Ask ❓",
        "pl": "Zapytaj ❓"
    },
    "clear": {
        "en": "Clear 🗑️",
        "pl": "Wyczyść 🗑️"
    },
    "question_placeholder": {
        "en": "Ask about anything",
        "pl": "Zapytaj o cokolwiek"
    },
    "thinking": {
        "en": "Thinking...",
        "pl": "Myślę..."
    },
    "executing": {
        "en": "Executing...",
        "pl": "Wykonuję..."
    },
}


def lang():
    return st.session_state.lang_selector if 'lang_selector' in st.session_state else DEFAULT_LANG


def trans(id):
    return ALL_TRANSLATIONS[id][lang()]


def language_selector(default='pl'):
    options = ['pl', 'en']
    
    gui_texts = {
        'pl': '🏳 ' + trans('polish').capitalize(),
        'en': '🏳 ' + trans('english').capitalize()
    }
    
    st.selectbox(
        label=trans('lang_label'),
        options=options,
        index=options.index(lang()),
        format_func=lambda lang: gui_texts[lang],
        key='lang_selector',
    )
