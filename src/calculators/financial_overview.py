import streamlit as st
from dataclasses import dataclass
from typing import List


@dataclass
class Asset:
    name: str
    value: float


@dataclass
class Liability:
    name: str
    amount: float


@dataclass
class MonthlyFlow:
    name: str
    amount: float


def get_user_input() -> tuple[List[Asset], List[Liability], List[MonthlyFlow], List[MonthlyFlow]]:
    """Get user input for assets, liabilities, and monthly cash flows."""
    assets = []
    liabilities = []
    income_streams = []
    expenses = []

    # Assets section
    st.write("### Bezittingen")
    num_assets = st.number_input(
        "Aantal bezittingen", min_value=0, value=1, step=1)
    for i in range(int(num_assets)):
        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.text_input(
                f"Naam bezitting {i + 1}", value=f"Bezitting {i + 1}")
        with col2:
            asset_value = st.number_input(
                f"Waarde bezitting {i + 1} (€)", min_value=0.0, value=0.0, step=100.0)
        assets.append(Asset(name=asset_name, value=asset_value))

    # Liabilities section
    st.write("### Schulden")
    num_liabilities = st.number_input(
        "Aantal schulden", min_value=0, value=1, step=1)
    for i in range(int(num_liabilities)):
        col1, col2 = st.columns(2)
        with col1:
            liability_name = st.text_input(
                f"Naam schuld {i + 1}", value=f"Schuld {i + 1}")
        with col2:
            liability_amount = st.number_input(
                f"Bedrag schuld {i + 1} (€)", min_value=0.0, value=0.0, step=100.0)
        liabilities.append(
            Liability(name=liability_name, amount=liability_amount))

    # Monthly Income
    st.write("### Maandelijkse Inkomsten")
    num_income = st.number_input(
        "Aantal inkomstenbronnen", min_value=0, value=1, step=1)
    for i in range(int(num_income)):
        col1, col2 = st.columns(2)
        with col1:
            income_name = st.text_input(
                f"Naam inkomstenbron {i + 1}", value=f"Inkomst {i + 1}")
        with col2:
            income_amount = st.number_input(
                f"Bedrag inkomst {i + 1} (€)", min_value=0.0, value=0.0, step=100.0)
        income_streams.append(MonthlyFlow(
            name=income_name, amount=income_amount))

    # Monthly Expenses
    st.write("### Maandelijkse Uitgaven")
    num_expenses = st.number_input(
        "Aantal uitgaven", min_value=0, value=1, step=1)
    for i in range(int(num_expenses)):
        col1, col2 = st.columns(2)
        with col1:
            expense_name = st.text_input(
                f"Naam uitgave {i + 1}", value=f"Uitgave {i + 1}")
        with col2:
            expense_amount = st.number_input(
                f"Bedrag uitgave {i + 1} (€)", min_value=0.0, value=0.0, step=100.0)
        expenses.append(MonthlyFlow(name=expense_name, amount=expense_amount))

    return assets, liabilities, income_streams, expenses


def display_summary(assets: List[Asset],
                    liabilities: List[Liability],
                    income_streams: List[MonthlyFlow],
                    expenses: List[MonthlyFlow]):
    """Display the financial summary."""
    # Calculate totals
    total_assets = sum(asset.value for asset in assets)
    total_liabilities = sum(liability.amount for liability in liabilities)
    net_worth = total_assets - total_liabilities

    total_income = sum(income.amount for income in income_streams)
    total_expenses = sum(expense.amount for expense in expenses)
    monthly_balance = total_income - total_expenses

    # Display summary metrics
    st.write("## Financieel Overzicht")

    # Assets, Liabilities, and Net Worth
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Totale Bezittingen", f"€{total_assets:,.2f}")
    with col2:
        st.metric("Totale Schulden", f"€{total_liabilities:,.2f}")
    with col3:
        st.metric("Netto Vermogen", f"€{net_worth:,.2f}")

    st.write("---")

    # Monthly Cash Flow
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Maandelijkse Inkomsten", f"€{total_income:,.2f}")
    with col2:
        st.metric("Maandelijkse Uitgaven", f"€{total_expenses:,.2f}")
    with col3:
        label = "Maandelijks Over" if monthly_balance >= 0 else "Maandelijks Tekort"
        delta_color = "normal" if monthly_balance >= 0 else "inverse"
        st.metric(label, f"€{abs(monthly_balance):,.2f}",
                  delta=f"{'Positief' if monthly_balance >= 0 else 'Negatief'} saldo",
                  delta_color=delta_color)


def show_financial_overview():
    """Main function to show the financial overview calculator."""
    with st.expander("💶 Overzicht van je Huidige Situatie", expanded=False):
        assets, liabilities, income_streams, expenses = get_user_input()
        display_summary(assets, liabilities, income_streams, expenses)
