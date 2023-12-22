from pathlib import Path

import streamlit as st


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
