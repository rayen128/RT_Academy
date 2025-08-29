"""Financial Overview Calculator - Comprehensive financial analysis tool.

This module provides financial overview calculations by offering both simple
and advanced modes for analyzing assets, liabilities, and cash flow.

Features
--------
- Simple Mode: 4 basic input fields with automatic monthly leftover calculation
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
from typing import Dict, List, Tuple

import streamlit as st

from src.utils.models import Asset, Liability, MonthlyFlow
from src.utils.questionnaire import NumberQuestion, Questionnaire, QuestionnaireConfig


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


def create_financial_questionnaire() -> Questionnaire:
    """Create a questionnaire for collecting financial overview data.

    Creates a step-by-step questionnaire to collect the user's financial
    information including income, expenses, assets, and debts.

    Returns
    -------
    Questionnaire
        Configured questionnaire with financial questions

    Example
    -------
    >>> questionnaire = create_financial_questionnaire()
    >>> # In Streamlit context:
    >>> data = questionnaire.run()
    >>> if data:
    ...     print(f"Monthly income: €{data['monthly_income']:,.2f}")

    Note
    ----
    The questionnaire collects data for simple financial overview calculation.
    All monetary values are in Euros (€).
    """
    questions = [
        NumberQuestion(
            key="monthly_income",
            text="Wat is je maandelijks netto inkomen?",
            min_value=0.0,
            step=100.0,
            format_str="%.2f",
            help_text="Voer je totale maandelijkse netto inkomen in euro's in",
        ),
        NumberQuestion(
            key="monthly_expenses",
            text="Wat zijn je totale maandelijkse uitgaven?",
            min_value=0.0,
            step=100.0,
            format_str="%.2f",
            help_text=(
                "Voer je totale maandelijkse uitgaven in euro's in "
                "(huur, boodschappen, verzekeringen, etc.)"
            ),
        ),
        NumberQuestion(
            key="total_assets",
            text="Wat is de totale waarde van je bezittingen/spaargeld?",
            min_value=0.0,
            step=1000.0,
            format_str="%.2f",
            help_text=(
                "Voer de totale waarde van je bezittingen in euro's in "
                "(spaargeld, investeringen, huis, auto, etc.)"
            ),
        ),
        NumberQuestion(
            key="total_debt",
            text="Wat is het totale bedrag van je schulden?",
            min_value=0.0,
            step=1000.0,
            format_str="%.2f",
            help_text=(
                "Voer het totale bedrag van je schulden in euro's in "
                "(hypotheek, leningen, creditcards, etc.)"
            ),
        ),
    ]

    config = QuestionnaireConfig(
        session_prefix="financial_overview",
        show_progress=True,
        show_previous_answers=True,
        navigation_style="columns",
    )

    return Questionnaire("financial_data", questions, config)


def questionnaire_data_to_financial_overview(
    data: Dict[str, float],
) -> FinancialOverviewData:
    """Convert questionnaire data to FinancialOverviewData structure.

    Transforms the flat dictionary returned by the questionnaire into
    a structured FinancialOverviewData object with calculated values.

    Parameters
    ----------
    data : Dict[str, float]
        Dictionary containing questionnaire responses with keys:
        'monthly_income', 'monthly_expenses', 'total_assets', 'total_debt'

    Returns
    -------
    FinancialOverviewData
        Complete financial data structure with calculated monthly leftover
        and single-item lists for consistency

    Example
    -------
    >>> data = {
    ...     'monthly_income': 3000.0,
    ...     'monthly_expenses': 2500.0,
    ...     'total_assets': 10000.0,
    ...     'total_debt': 5000.0
    ... }
    >>> overview = questionnaire_data_to_financial_overview(data)
    >>> overview.monthly_leftover
    500.0

    Note
    ----
    Creates single-item lists for assets, liabilities, income_streams,
    and expense_streams to maintain consistency with advanced mode structure.
    """
    monthly_income = data.get("monthly_income", 0.0)
    monthly_expenses = data.get("monthly_expenses", 0.0)
    total_assets = data.get("total_assets", 0.0)
    total_debt = data.get("total_debt", 0.0)

    # Calculate monthly leftover
    monthly_leftover = monthly_income - monthly_expenses

    # Create simple data structures for consistency
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


def get_simple_user_input() -> FinancialOverviewData:
    """Collect basic financial data through simplified input form.

    Displays a simple form with 4 essential financial input fields arranged
    in a two-column layout for quick financial overview entry. Monthly leftover
    is automatically calculated from income min expenses.

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
        Monthly leftover is calculated as income minus expenses.
    """
    st.write("### Basis Financiële Gegevens")

    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input(
            "Maandelijks inkomen (€)", min_value=0.0, value=3000.0, step=100.0
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

    # Calculate monthly leftover
    monthly_leftover = monthly_income - monthly_expenses

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
    """Display comprehensive financial summary with metrics.

    Calculates and displays key financial metrics including net worth and
    monthly balance from the provided financial data.

    Parameters
    ----------
    data : FinancialOverviewData
        Complete financial data structure containing all user inputs and
        calculated values

    Returns
    -------
    None
        This function updates the Streamlit UI directly with metrics

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
    Monthly leftover is calculated automatically as income minus expenses.
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


def show_financial_overview() -> None:
    """Display the complete financial overview calculator interface.

    Main entry point for the financial overview calculator. Uses a step-by-step
    questionnaire to collect financial data, then displays comprehensive results.

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
    Uses questionnaire-based data collection for improved user experience.
    Results are displayed automatically when the questionnaire is completed.
    The expander starts expanded to show the questionnaire.
    """
    with st.expander("💶 Overzicht van je Huidige Situatie", expanded=True):
        st.write("### Financiële Vragenlijst")
        st.write("Beantwoord de volgende vragen om je financiële overzicht te krijgen:")

        # Create and run the questionnaire
        questionnaire = create_financial_questionnaire()
        questionnaire_data = questionnaire.run()

        # If questionnaire is completed, show results
        if questionnaire_data is not None:
            st.write("---")
            st.success("Vragenlijst voltooid! Hier is je financiële overzicht:")

            # Convert questionnaire data to financial overview data
            financial_data = questionnaire_data_to_financial_overview(
                questionnaire_data
            )

            # Display the summary
            display_summary(financial_data)

            # Add reset button to allow starting over
            st.write("---")
            if st.button("Opnieuw beginnen", key="reset_questionnaire"):
                questionnaire.reset()
                st.rerun()


def show_financial_overview_legacy() -> None:
    """Display the legacy financial overview calculator interface.

    Legacy version that uses the original form-based input method.
    Kept for backward compatibility.

    Returns
    -------
    None
        This function creates Streamlit UI components directly

    Note
    ----
    This is the original implementation before questionnaire integration.
    Use show_financial_overview() for the new questionnaire-based interface.
    """
    with st.expander("💶 Overzicht van je Huidige Situatie (Legacy)", expanded=False):
        data, calculate_clicked = get_user_input()

        if calculate_clicked:
            display_summary(data)
