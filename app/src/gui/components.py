from pathlib import Path

import streamlit as st

from gui.translation import trans


def uploader_enhanced(*args, **kwargs):
    file = st.file_uploader(
        *args,
        **kwargs,
        accept_multiple_files=False,
    )
    
    if file is None:
        return None
    
    file_path = Path('/tmp/uploads') / file.file_id / file.name
    
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file.read())
    
    return file_path


def password_protection():
    def check_password():
        """Returns `True` if the user had the correct password."""

        def password_entered():
            """Checks whether a password entered by the user is correct."""
            if st.session_state["password"] == (os.environ.get('PASSWORD') or 'password'):
                st.session_state["password_correct"] = True
                del st.session_state["password"]
            else:
                st.session_state["password_correct"] = False

        if st.session_state.get("password_correct", False):
            return True

        st.title(trans('title'))
        
        st.write('Application is proctected. Enter password.')

        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password",
        )
        if "password_correct" in st.session_state:
            st.error("😕 Password incorrect")
        return False


    if not check_password():
        st.stop()
