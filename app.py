"""Main Streamlit application for RT Academy financial calculators."""

import streamlit as st

from src.assessments.financiele_apk import show_financiele_apk

st.title("Welkom bij de RT Finance")

st.write(
    """
    De tool die jou gaat helpen met inzicht, controle en vooral rust
    binnen jouw financiën.
    """
)

show_financiele_apk()
