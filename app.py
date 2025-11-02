"""Main Streamlit application for RT Academy financial calculators."""

import streamlit as st

from src.assessments.financiele_apk import show_financiele_apk

st.title("Financiele APK")

st.write(
    """
    Om uiteindelijk naar je doel toe te werken, is het belangrijk om eerst
    te bepalen waar je nu staat. Dat doen we door een overzicht te maken van
    je huidige situatie. Op basis daarvan kunnen we bepalen hoe je verder moet.
    """
)

show_financiele_apk()
