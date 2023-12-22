import streamlit as st


DEFAULT_LANG = 'en'


ALL_TRANSLATIONS = {
    "title": {
        "en": "Polish Text-to-SQL",
        "pl": "Polskie Text-to-SQL"
    },
    "lang_label": {
        "en": "Interface language",
        "pl": "Język interfejsu"
    },
    "polish": {
        "en": "🇵🇱 Polish",
        "pl": "🇵🇱 Polski"
    },
    "english": {
        "en": "🇬🇧 English",
        "pl": "🇬🇧 Angielski"
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
        "en": "Upload SQLite database...",
        "pl": "Załaduj bazę danych SQLite..."
    },
    "provide_sql": {
        "en": "...Or provide SQL for schema creation",
        "pl": "...Lub dostarcz skrypt SQL tworzący schemat"
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
