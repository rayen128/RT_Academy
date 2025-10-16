"""Main Streamlit application for RT Academy financial calculators."""

import streamlit as st

from src.code.calculators.financial_overview import show_financiele_apk

st.title("Financiele APK")

st.write(
    """
    Om uiteindelijk naar je doel toe te werken, is het belangrijk om eerst
    te bepalen waar je nu staat. Dat doen we door een overzicht te maken van
    je huidige situatie. Op basis daarvan kunnen we bepalen hoe je verder moet.
    """
)

show_financiele_apk()

# Temporarily hidden - original goal selection
# goal = st.radio(
#     label="Financieel doel",  # Meaningful label for accessibility
#     options=["Financiën op orde brengen", "Schulden aflossen", "Vermogen opbouwen"],
#     # Hides the label visually but keeps it for screen readers
#     label_visibility="collapsed",
# )

# if goal == "Financiën op orde brengen":
#     st.info(
#         '''
#     🎯 Geweldig dat je je financiën op orde wilt brengen!

#     Enkele tips om te beginnen:
#     1. Maak een overzicht van je inkomsten en uitgaven
#     2. Stel een realistisch budget op
#     3. Begin met een emergency fund
#     4. Bekijk beide calculators hieronder om je financiële doelen te plannen
#     '''
#     )

#     show_financial_overview()

# elif goal == "Schulden aflossen":
#     st.info(
#         '''
#     💪 Goed dat je actie wilt ondernemen om je schulden af te lossen!

#     De Schuld Aflossing Calculator hieronder kan je helpen om:
#     1. Je schulden overzichtelijk in kaart te brengen
#     2. De beste aflossing strategie te kiezen
#     3. Te zien hoelang het duurt om schuldenvrij te worden
#     '''
#     )
#     # Automatically expand the debt payoff calculator
#     show_debt_payoff_calculator()


# else:  # Vermogen opbouwen
#     st.info(
#         '''
#     📈 Uitstekende keuze om te focussen op vermogensopbouw!

#     De Samengestelde Interest Calculator kan je helpen om:
#     1. Te zien hoe je geld groeit over tijd
#     2. Een realistisch spaar- of investeringsdoel te stellen
#     3. De kracht van samengestelde interest te benutten
#     '''
#     )
#     # Automatically expand the compound interest calculator
#     show_compound_interest_calculator()
