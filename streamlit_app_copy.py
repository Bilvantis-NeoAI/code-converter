import streamlit as st
import os
from io import BytesIO
from jinja2 import Template
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))
from src.prompts.prompt_manager import PromptManager
from src.config.llm_config import get_llm

def convert_cobol_code(cobol_code, target_lang):
    prompt_manager = PromptManager()
    if target_lang == "Java":
        template_str = prompt_manager.load_cobal_java_template()
    else:
        template_str = prompt_manager.load_cobal_python_template()
    prompt = Template(template_str)
    prompt_str = prompt.render(cobol_code=cobol_code)
    llm = get_llm()
    response = llm.invoke(prompt_str)
    try:
        json_str = response.content.split("```json")[1].split("````")[0].strip()
        result = json.loads(json_str)
    except Exception:
        try:
            json_str = response.content.split("```json")[1].split("```")[0].strip()
            result = json.loads(json_str)
        except Exception:
            result = {"error": "Failed to parse JSON", "raw_response": response.content}
    return result

def main():
    st.set_page_config(page_title="COBOL Code Converter", layout="wide")
    st.markdown("""
        <style>
        .small-button button {
            padding: 0.25rem 0.75rem !important;
            font-size: 0.9rem !important;
        }
        .block-container {
            padding-top: 1.5rem;
        }
        .centered-heading {
            text-align: center;
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 1.2rem;
            margin-top: 2.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="centered-heading">COBOL Code Converter</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a COBOL file", type=["cob", "cbl"])
    file_content = None
    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8")
    col1, col2, col3 = st.columns([3, 1, 3])
    with col1:
        st.subheader("File Content")
        if file_content:
            st.code(file_content, language="cobol")
        else:
            st.info("Upload a COBOL file to see its content here.")
    with col2:
        st.subheader("Conversion Options")
        target_lang = st.selectbox("Convert to:", ["Java", "Python"])
        convert_clicked = st.button("Convert", key="convert_btn", use_container_width=True, disabled=uploaded_file is None)
        if 'converted_code' not in st.session_state:
            st.session_state['converted_code'] = None
        if 'download_ready' not in st.session_state:
            st.session_state['download_ready'] = False
        if convert_clicked and uploaded_file is not None:
            with st.spinner(f"Converting to {target_lang}..."):
                result = convert_cobol_code(file_content, target_lang)
                code = result.get("code")
                if code:
                    st.session_state['converted_code'] = code
                    st.session_state['download_ready'] = True
                    st.success("Conversion successful!")
                elif "raw_response" in result:
                    st.session_state['converted_code'] = result["raw_response"]
                    st.session_state['download_ready'] = False
                    st.warning("Could not parse code. Showing raw response:")
                else:
                    st.session_state['converted_code'] = None
                    st.session_state['download_ready'] = False
                    st.error(f"Unexpected response: {result}")
        if st.session_state.get('converted_code') and st.session_state.get('download_ready'):
            st.markdown("<div style='margin-top: 0.5em'></div>", unsafe_allow_html=True)
            st.download_button(
                label=f"Download {target_lang} File",
                data=st.session_state['converted_code'],
                file_name=f"converted.{ 'java' if target_lang == 'Java' else 'py'}",
                mime="text/x-java-source" if target_lang == 'Java' else "text/x-python",
                use_container_width=True
            )
    with col3:
        st.subheader("Converted Output")
        if st.session_state.get('converted_code'):
            st.code(st.session_state['converted_code'], language=target_lang.lower())

if __name__ == "__main__":
    main() 