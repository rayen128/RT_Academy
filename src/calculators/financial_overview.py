"""Financial Overview Calculator - Comprehensive financial analysis tool.

This module provides financial overview calculations by offering both simple
and advanced modes for analyzing assets, liabilities, and cash flow.

Features
--------
- Simple Mode: 5 basic input fields for quick financial overview
- Advanced Mode: Detailed breakdown of multiple income sources, expenses,
  assets, and debts
- Real-time validation and calculation of net worth and monthly balance
- Streamlit-based interactive user interface

Dependencies
------------
- streamlit: >=1.0.0 - Web UI framework for interactive data applications
- dataclasses: Built-in - For structured data containers
- typing: Built-in - For type hints and annotations

Example
-------
>>> from src.calculators.financial_overview import show_financial_overview
>>> # In a Streamlit app:
>>> show_financial_overview()
# Displays interactive financial overview calculator

Note
----
This module requires Streamlit context to run. All monetary values
are assumed to be in Euros (€). The simple mode includes validation
to ensure input consistency.
"""

from dataclasses import dataclass
from typing import List, Tuple

import streamlit as st

from src.utils.models import Asset, Liability, MonthlyFlow


@dataclass
class FinancialOverviewData:  # pylint: disable=too-many-instance-attributes
    """Data structure for comprehensive financial overview information.

    Represents all financial data collected from either simple or advanced
    input modes, providing a unified structure for calculations and display.

    Attributes
    ----------
    monthly_income : float
        Total monthly income in euros
    monthly_expenses : float
        Total monthly expenses in euros
    monthly_leftover : float
        Manually entered or calculated leftover amount
    total_assets : float
        Total value of all assets in euros
    total_debt : float
        Total amount of all debts in euros
    assets : List[Asset]
        Detailed list of individual assets
    liabilities : List[Liability]
        Detailed list of individual debts
    income_streams : List[MonthlyFlow]
        Detailed list of income sources
    expense_streams : List[MonthlyFlow]
        Detailed list of expense categories

    Example
    -------
    >>> data = FinancialOverviewData(
    ...     monthly_income=3000.0,
    ...     monthly_expenses=2500.0,
    ...     monthly_leftover=500.0,
    ...     total_assets=10000.0,
    ...     total_debt=5000.0,
    ...     assets=[Asset(name="Savings", value=10000.0)],
    ...     liabilities=[Liability(name="Loan", amount=5000.0)],
    ...     income_streams=[MonthlyFlow(name="Salary", amount=3000.0)],
    ...     expense_streams=[MonthlyFlow(name="Living", amount=2500.0)]
    ... )
    >>> data.monthly_income
    3000.0

    Note
    ----
    In simple mode, assets, liabilities, income_streams, and expense_streams
    will contain single items representing the totals.
    """

    monthly_income: float
    monthly_expenses: float
    monthly_leftover: float
    total_assets: float
    total_debt: float
    assets: List[Asset]
    liabilities: List[Liability]
    income_streams: List[MonthlyFlow]
    expense_streams: List[MonthlyFlow]


def get_simple_user_input() -> FinancialOverviewData:
    """Collect basic financial data through simplified input form.

    Displays a simple form with 5 essential financial input fields arranged
    in a two-column layout for quick financial overview entry.

    Returns
    -------
    FinancialOverviewData
        Complete financial data structure with simple aggregated values and
        single-item lists for consistency

    Example
    -------
    >>> # In Streamlit context:
    >>> data = get_simple_user_input()
    >>> data.monthly_income >= 0
    True
    >>> len(data.assets) <= 1  # Single aggregated asset entry
    True

    Note
    ----
        Creates single-item lists for assets, liabilities, income_streams,
        and expense_streams to maintain consistency with advanced mode data structure.
        All monetary inputs are validated to be non-negative.
    """
    st.write("### Basis Financiële Gegevens")

    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input(
            "Maandelijks inkomen (€)", min_value=0.0, value=3000.0, step=100.0
        )
        monthly_leftover = st.number_input(
            "Maandelijks over (€)", min_value=0.0, value=500.0, step=50.0
        )
        total_assets = st.number_input(
            "Totale bezittingen/spaargeld (€)",
            min_value=0.0,
            value=10000.0,
            step=1000.0,
        )

    with col2:
        monthly_expenses = st.number_input(
            "Maandelijkse uitgaven (€)", min_value=0.0, value=2500.0, step=100.0
        )
        total_debt = st.number_input(
            "Totale schulden (€)", min_value=0.0, value=0.0, step=1000.0
        )

    # Create simple data structures for consistency with advanced mode
    assets = (
        [Asset(name="Totale bezittingen", value=total_assets)]
        if total_assets > 0
        else []
    )
    liabilities = (
        [Liability(name="Totale schulden", amount=total_debt)] if total_debt > 0 else []
    )
    income_streams = (
        [MonthlyFlow(name="Maandelijks inkomen", amount=monthly_income)]
        if monthly_income > 0
        else []
    )
    expense_streams = (
        [MonthlyFlow(name="Maandelijkse uitgaven", amount=monthly_expenses)]
        if monthly_expenses > 0
        else []
    )

    return FinancialOverviewData(
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_leftover=monthly_leftover,
        total_assets=total_assets,
        total_debt=total_debt,
        assets=assets,
        liabilities=liabilities,
        income_streams=income_streams,
        expense_streams=expense_streams,
    )


def get_advanced_user_input() -> (
    FinancialOverviewData
):  # pylint: disable=too-many-locals
    """Collect detailed financial data through advanced multi-category form.

    Displays an advanced form allowing users to input multiple income sources,
    expense categories, assets, and liabilities with individual names and amounts.
    Categories are presented in logical order: income, expenses, assets, debts.

    Returns
    -------
    FinancialOverviewData
        Complete financial data structure with detailed breakdowns and
        calculated totals

    Example
    -------
    >>> # In Streamlit context:
    >>> data = get_advanced_user_input()
    >>> data.total_assets == sum(asset.value for asset in data.assets)
    True
    >>> data.monthly_leftover == data.monthly_income - data.monthly_expenses
    True

    Note
    ----
    Totals are automatically calculated from individual entries.
    The monthly_leftover is computed as income minus expenses.
    All individual items use dynamic numbering based on user-specified quantities.
    """
    assets = []
    liabilities = []
    income_streams = []
    expense_streams = []

    # Monthly Income
    st.write("### Maandelijkse Inkomsten")
    num_income = st.number_input(
        "Aantal inkomstenbronnen", min_value=0, value=1, step=1
    )
    for i in range(int(num_income)):
        col1, col2 = st.columns(2)
        with col1:
            income_name = st.text_input(
                f"Naam inkomstenbron {i + 1}", value=f"Inkomst {i + 1}"
            )
        with col2:
            income_amount = st.number_input(
                f"Bedrag inkomst {i + 1} (€)", min_value=0.0, value=0.0, step=100.0
            )
        income_streams.append(MonthlyFlow(name=income_name, amount=income_amount))

    # Monthly Expenses
    st.write("### Maandelijkse Uitgaven")
    num_expenses = st.number_input("Aantal uitgaven", min_value=0, value=1, step=1)
    for i in range(int(num_expenses)):
        col1, col2 = st.columns(2)
        with col1:
            expense_name = st.text_input(
                f"Naam uitgave {i + 1}", value=f"Uitgave {i + 1}"
            )
        with col2:
            expense_amount = st.number_input(
                f"Bedrag uitgave {i + 1} (€)", min_value=0.0, value=0.0, step=100.0
            )
        expense_streams.append(MonthlyFlow(name=expense_name, amount=expense_amount))

    # Assets section
    st.write("### Bezittingen")
    num_assets = st.number_input("Aantal bezittingen", min_value=0, value=1, step=1)
    for i in range(int(num_assets)):
        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.text_input(
                f"Naam bezitting {i + 1}", value=f"Bezitting {i + 1}"
            )
        with col2:
            asset_value = st.number_input(
                f"Waarde bezitting {i + 1} (€)", min_value=0.0, value=0.0, step=100.0
            )
        assets.append(Asset(name=asset_name, value=asset_value))

    # Liabilities section
    st.write("### Schulden")
    num_liabilities = st.number_input("Aantal schulden", min_value=0, value=1, step=1)
    for i in range(int(num_liabilities)):
        col1, col2 = st.columns(2)
        with col1:
            liability_name = st.text_input(
                f"Naam schuld {i + 1}", value=f"Schuld {i + 1}"
            )
        with col2:
            liability_amount = st.number_input(
                f"Bedrag schuld {i + 1} (€)", min_value=0.0, value=0.0, step=100.0
            )
        liabilities.append(Liability(name=liability_name, amount=liability_amount))

    # Calculate totals for consistency
    total_assets = sum(asset.value for asset in assets)
    total_debt = sum(liability.amount for liability in liabilities)
    monthly_income = sum(income.amount for income in income_streams)
    monthly_expenses = sum(expense.amount for expense in expense_streams)
    monthly_leftover = monthly_income - monthly_expenses

    return FinancialOverviewData(
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_leftover=monthly_leftover,
        total_assets=total_assets,
        total_debt=total_debt,
        assets=assets,
        liabilities=liabilities,
        income_streams=income_streams,
        expense_streams=expense_streams,
    )


def get_user_input() -> Tuple[FinancialOverviewData, bool]:
    """Coordinate user input collection with mode selection and calculation trigger.

    Provides a toggle for simple vs advanced mode and handles the overall
    input collection process with a calculation button.

    Returns
    -------
    Tuple[FinancialOverviewData, bool]
        A tuple containing complete financial data from selected input mode
        and boolean indicating if calculate button was pressed

    Example
    -------
    >>> # In Streamlit context:
    >>> data, should_calculate = get_user_input()
    >>> isinstance(data, FinancialOverviewData)
    True
    >>> isinstance(should_calculate, bool)
    True

    Note
    ----
    The advanced mode toggle determines which input collection function
    is called. The calculate button state is returned to control when
    results should be displayed.
    """
    # Advanced mode toggle
    advanced_mode = st.checkbox("Geavanceerde instellingen")

    if advanced_mode:
        data = get_advanced_user_input()
    else:
        data = get_simple_user_input()

    calculate_button = st.button("Bereken Overzicht")

    return data, calculate_button


def display_summary(data: FinancialOverviewData) -> None:
    """Display comprehensive financial summary with metrics and validation.

    Calculates and displays key financial metrics including net worth and
    monthly balance. Provides validation warnings for inconsistent simple mode inputs.

    Parameters
    ----------
    data : FinancialOverviewData
        Complete financial data structure containing all user inputs and
        calculated values

    Returns
    -------
    None
        This function updates the Streamlit UI directly with metrics
        and validation messages

    Example
    -------
    >>> # In Streamlit context:
    >>> data = FinancialOverviewData(
    ...     monthly_income=3000.0, monthly_expenses=2500.0,
    ...     monthly_leftover=500.0, total_assets=10000.0, total_debt=5000.0,
    ...     assets=[], liabilities=[], income_streams=[], expense_streams=[]
    ... )
    >>> display_summary(data)
    # Displays metrics: Net Worth: €5,000.00, Monthly Balance: €500.00

    Note
    ----
    In simple mode (identified by single or no asset/liability entries),
    provides validation warning if manually entered leftover amount doesn't
    match calculated income minus expenses difference.
    """
    # Calculate totals from the data
    net_worth = data.total_assets - data.total_debt
    monthly_balance = data.monthly_income - data.monthly_expenses

    # Display summary metrics
    st.write("### Financieel Overzicht")

    # Assets, Liabilities, and Net Worth
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Totale Bezittingen", f"€{data.total_assets:,.2f}")
    with col2:
        st.metric("Totale Schulden", f"€{data.total_debt:,.2f}")
    with col3:
        st.metric("Netto Vermogen", f"€{net_worth:,.2f}")

    st.write("---")

    # Monthly Cash Flow
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Maandelijkse Inkomsten", f"€{data.monthly_income:,.2f}")
    with col2:
        st.metric("Maandelijkse Uitgaven", f"€{data.monthly_expenses:,.2f}")
    with col3:
        label = "Maandelijks Over" if monthly_balance >= 0 else "Maandelijks Tekort"
        delta_color = "normal" if monthly_balance >= 0 else "inverse"
        st.metric(
            label,
            f"€{abs(monthly_balance):,.2f}",
            delta=f"{'Positief' if monthly_balance >= 0 else 'Negatief'} saldo",
            delta_color=delta_color,
        )

    # Validation check - compare calculated vs input leftover in simple mode
    if len(data.assets) <= 1 and len(data.liabilities) <= 1:  # Simple mode
        # Allow for small rounding differences
        if abs(monthly_balance - data.monthly_leftover) > 0.01:
            st.warning(
                f"Let op: Het berekende maandelijkse saldo "
                f"(€{monthly_balance:,.2f}) komt niet overeen met het "
                f"ingevoerde bedrag (€{data.monthly_leftover:,.2f}). "
                f"Controleer je invoer."
            )


def show_financial_overview() -> None:
    """Display the complete financial overview calculator interface.

    Main entry point for the financial overview calculator. Creates an expandable
    section with mode selection, input collection, and results display.

    Returns
    -------
    None
        This function creates Streamlit UI components directly

    Example
    -------
    >>> # In Streamlit app:
    >>> show_financial_overview()
    # Creates expandable "💶 Overzicht van je Huidige Situatie" section

    Note
    ----
    Designed to be called from the main Streamlit application.
    Results are only displayed after the user clicks the calculate button.
    The expander starts collapsed to save screen space.
    """
    with st.expander("💶 Overzicht van je Huidige Situatie", expanded=False):
        data, calculate_clicked = get_user_input()

        if calculate_clicked:
            display_summary(data)
