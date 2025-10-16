"""Financiele APK Calculator - Comprehensive financial analysis tool.

This module provides Financiele APK calculations by offering both simple
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
>>> from src.assessments.financiele_apk import show_financiele_apk
>>> # In a Streamlit app:
>>> show_financiele_apk()
# Displays interactive Financiele APK calculator

Note
----
This module requires Streamlit context to run. All monetary values
are assumed to be in Euros (€). The simple mode includes validation
to ensure input consistency.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

import plotly.graph_objects as go
import streamlit as st

from src.database.models import Asset, Liability, MonthlyFlow
from src.UI_components.Applied.questionnaire import (
    NumberQuestion,
    Questionnaire,
    QuestionnaireConfig,
)


def validate_financial_consistency(
    monthly_income: float, monthly_expenses: float, monthly_leftover: float
) -> Tuple[bool, str]:
    """Validate consistency between income, expenses and leftover amount.

    Parameters
    ----------
    monthly_income : float
        Total monthly income in euros
    monthly_expenses : float
        Total monthly expenses in euros
    monthly_leftover : float
        User-reported monthly leftover amount in euros

    Returns
    -------
    Tuple[bool, str]
        Boolean indicating if values are consistent and warning message if not

    Example
    -------
    >>> is_valid, message = validate_financial_consistency(3000.0, 2500.0, 500.0)
    >>> is_valid
    True
    >>> is_valid, message = validate_financial_consistency(3000.0, 2500.0, 300.0)
    >>> is_valid
    False
    """
    calculated_leftover = monthly_income - monthly_expenses
    difference = abs(calculated_leftover - monthly_leftover)
    tolerance = 50.0  # €50 tolerance

    if difference <= tolerance:
        return True, ""

    if monthly_leftover > calculated_leftover:
        return (
            False,
            f"⚠️ Je zegt €{monthly_leftover:,.2f} over te houden, maar op basis "
            f"van je inkomen (€{monthly_income:,.2f}) en uitgaven "
            f"(€{monthly_expenses:,.2f}) zou je €{calculated_leftover:,.2f} "
            f"over moeten houden. Controleer je bedragen.",
        )
    return (
        False,
        f"⚠️ Op basis van je inkomen (€{monthly_income:,.2f}) en uitgaven "
        f"(€{monthly_expenses:,.2f}) zou je €{calculated_leftover:,.2f} over "
        f"moeten houden, maar je zegt slechts €{monthly_leftover:,.2f} over "
        f"te houden. Mogelijk heb je uitgaven vergeten?",
    )


@dataclass
class FinancieleAPKData:  # pylint: disable=too-many-instance-attributes
    """Data structure for comprehensive Financiele APK information.

    Represents all financial data collected from either simple or advanced
    input modes, providing a unified structure for Financiele APK calculations and display.

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
    >>> data = FinancieleAPKData(
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


def create_financiele_apk_questionnaire() -> Questionnaire:
    """Create a questionnaire for collecting Financiele APK data.

    Creates a step-by-step questionnaire to collect the user's financial
    information including income, expenses, leftover money, assets, and debts.

    Returns
    -------
    Questionnaire
        Configured questionnaire with financial questions

    Example
    -------
    >>> questionnaire = create_financiele_apk_questionnaire()
    >>> # In Streamlit context:
    >>> data = questionnaire.run()
    >>> if data:
    ...     print(f"Monthly income: €{data['monthly_income']:,.2f}")

    Note
    ----
    The questionnaire collects data for simple Financiele APK calculation.
    All monetary values are in Euros (€).
    """
    questions = [
        NumberQuestion(
            key="monthly_income",
            text="Wat is je maandelijks netto totaal inkomen gemiddeld genomen?",
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
            key="monthly_leftover",
            text=(
                "Hoeveel geld houd je gemiddeld maandelijks over "
                "om te kunnen sparen of beleggen?"
            ),
            min_value=0.0,
            step=50.0,
            format_str="%.2f",
            help_text=(
                "(Tip: je kunt dit nagaan door je bankafschriften te checken. "
                "Reken alleen echt het geld dat je overhoudt. Dus niet geld "
                "dat je apart zet voor een vakantie, een nieuwe auto of "
                "andere spaardoelen.)"
            ),
        ),
        NumberQuestion(
            key="total_assets",
            text="Hoeveel spaargeld, beleggingen of andere bezittingen bezit je nu?",
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
            text="Wat is je totaal aantal schulden?",
            min_value=0.0,
            step=1000.0,
            format_str="%.2f",
            help_text='Als je geen schulden hebt, vul hier "0" in.',
        ),
    ]

    config = QuestionnaireConfig(
        session_prefix="financiele_apk",
        show_progress=True,
        show_previous_answers=True,
        navigation_style="columns",
    )

    return Questionnaire("financiele_apk_data", questions, config)


def _create_simple_financial_lists(
    monthly_income: float,
    monthly_expenses: float,
    total_assets: float,
    total_debt: float,
) -> Tuple[List[Asset], List[Liability], List[MonthlyFlow], List[MonthlyFlow]]:
    """Create simple financial data lists for consistency with advanced mode.

    Parameters
    ----------
    monthly_income : float
        Total monthly income in euros
    monthly_expenses : float
        Total monthly expenses in euros
    total_assets : float
        Total value of assets in euros
    total_debt : float
        Total amount of debt in euros

    Returns
    -------
    Tuple[List[Asset], List[Liability], List[MonthlyFlow], List[MonthlyFlow]]
        Tuple containing assets, liabilities, income_streams, expense_streams lists
    """
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

    return assets, liabilities, income_streams, expense_streams


def questionnaire_data_to_financiele_apk(
    data: Dict[str, float],
) -> FinancieleAPKData:
    """Convert questionnaire data to FinancieleAPKData structure.

    Transforms the flat dictionary returned by the questionnaire into
    a structured FinancieleAPKData object with user-provided values.

    Parameters
    ----------
    data : Dict[str, float]
        Dictionary containing questionnaire responses with keys:
        'monthly_income', 'monthly_expenses', 'monthly_leftover',
        'total_assets', 'total_debt'

    Returns
    -------
    FinancieleAPKData
        Complete financial data structure with user-provided monthly leftover
        and single-item lists for consistency

    Example
    -------
    >>> data = {
    ...     'monthly_income': 3000.0,
    ...     'monthly_expenses': 2500.0,
    ...     'monthly_leftover': 400.0,
    ...     'total_assets': 10000.0,
    ...     'total_debt': 5000.0
    ... }
    >>> overview = questionnaire_data_to_financiele_apk(data)
    >>> overview.monthly_leftover
    400.0

    Note
    ----
    Creates single-item lists for assets, liabilities, income_streams,
    and expense_streams to maintain consistency with advanced mode structure.
    Uses user-provided monthly_leftover instead of calculating it.
    """
    monthly_income = data.get("monthly_income", 0.0)
    monthly_expenses = data.get("monthly_expenses", 0.0)
    monthly_leftover = data.get("monthly_leftover", 0.0)
    total_assets = data.get("total_assets", 0.0)
    total_debt = data.get("total_debt", 0.0)

    # Create simple data structures for consistency
    assets, liabilities, income_streams, expense_streams = (
        _create_simple_financial_lists(
            monthly_income, monthly_expenses, total_assets, total_debt
        )
    )

    return FinancieleAPKData(
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


def create_cash_flow_visualization(data: FinancieleAPKData) -> go.Figure:
    """Create a bar chart visualization for monthly cash flow.

    Parameters
    ----------
    data : FinancieleAPKData
        Complete financial data structure

    Returns
    -------
    go.Figure
        Plotly figure showing income, expenses, and leftover amount
    """
    categories = ["Inkomsten", "Uitgaven", "Over/Tekort"]
    amounts = [data.monthly_income, data.monthly_expenses, data.monthly_leftover]
    colors = ["green", "red", "blue" if data.monthly_leftover >= 0 else "orange"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=categories,
            y=amounts,
            marker_color=colors,
            text=[f"€{amt:,.0f}" for amt in amounts],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="Maandelijkse Kasstromen",
        xaxis_title="Categorieën",
        yaxis_title="Bedrag (€)",
        showlegend=False,
        height=400,
    )

    return fig


def create_net_worth_visualization(data: FinancieleAPKData) -> go.Figure:
    """Create a bar chart visualization for net worth calculation.

    Parameters
    ----------
    data : FinancieleAPKData
        Complete financial data structure

    Returns
    -------
    go.Figure
        Plotly figure showing assets, liabilities, and net worth
    """
    net_worth = data.total_assets - data.total_debt

    categories = ["Bezittingen", "Schulden", "Eigen Vermogen"]
    # Make debt negative for visualization
    amounts = [data.total_assets, -data.total_debt, net_worth]
    colors = ["green", "red", "blue" if net_worth >= 0 else "orange"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=categories,
            y=amounts,
            marker_color=colors,
            text=[f"€{abs(amt):,.0f}" for amt in amounts],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="Eigen Vermogen Overzicht",
        xaxis_title="Categorieën",
        yaxis_title="Bedrag (€)",
        showlegend=False,
        height=400,
    )

    return fig


def display_summary(data: FinancieleAPKData) -> None:
    """Display comprehensive Financiele APK summary with metrics and visualizations.

    Calculates and displays key financial metrics including net worth and
    monthly leftover from the provided financial data, along with interactive
    charts showing cash flow and net worth breakdown.

    Parameters
    ----------
    data : FinancieleAPKData
        Complete financial data structure containing all user inputs and
        calculated values

    Returns
    -------
    None
        This function updates the Streamlit UI directly with metrics and charts

    Example
    -------
    >>> # In Streamlit context:
    >>> data = FinancieleAPKData(
    ...     monthly_income=3000.0, monthly_expenses=2500.0,
    ...     monthly_leftover=500.0, total_assets=10000.0, total_debt=5000.0,
    ...     assets=[], liabilities=[], income_streams=[], expense_streams=[]
    ... )
    >>> display_summary(data)
    # Displays metrics and charts for Financiele APK

    Note
    ----
    Uses the user-provided monthly_leftover value instead of calculating it.
    Includes interactive visualizations for better understanding of cash flow
    and net worth.
    """
    # Calculate totals from the data
    net_worth = data.total_assets - data.total_debt
    # Use the user-provided monthly_leftover instead of calculating it
    monthly_leftover = data.monthly_leftover

    # Display summary metrics
    st.write("### 📊 Financiele APK")

    # Assets, Liabilities, and Net Worth
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Totale Bezittingen", f"€{data.total_assets:,.2f}")
    with col2:
        st.metric("Totale Schulden", f"€{data.total_debt:,.2f}")
    with col3:
        st.metric("Eigen Vermogen", f"€{net_worth:,.2f}")

    st.write("---")

    # Monthly Cash Flow
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Maandelijkse Inkomsten", f"€{data.monthly_income:,.2f}")
    with col2:
        st.metric("Maandelijkse Uitgaven", f"€{data.monthly_expenses:,.2f}")
    with col3:
        label = "Maandelijks Over" if monthly_leftover >= 0 else "Maandelijks Tekort"
        delta_color = "normal" if monthly_leftover >= 0 else "inverse"
        st.metric(
            label,
            f"€{abs(monthly_leftover):,.2f}",
            delta=f"{'Positief' if monthly_leftover >= 0 else 'Negatief'} saldo",
            delta_color=delta_color,
        )

    st.write("---")

    # Visualizations Section
    st.write("### 📈 Visualisatie")

    # Create two columns for the charts
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Maandelijks overzicht**")
        cash_flow_fig = create_cash_flow_visualization(data)
        st.plotly_chart(cash_flow_fig, use_container_width=True)

        # Text summary for cash flow
        if data.monthly_leftover > 0:
            st.success(
                f"✅ Je houdt maandelijks €{data.monthly_leftover:,.2f} over "
                f"voor sparen/beleggen"
            )
        elif data.monthly_leftover < 0:
            st.error(
                f"⚠️ Je hebt een maandelijks tekort van "
                f"€{abs(data.monthly_leftover):,.2f}"
            )
        else:
            st.warning("💡 Je inkomsten en uitgaven zijn precies gelijk")

    with col2:
        st.write("**Vermogen overzicht**")
        net_worth_fig = create_net_worth_visualization(data)
        st.plotly_chart(net_worth_fig, use_container_width=True)

        # Text summary for net worth
        if net_worth > 0:
            st.success(f"💰 Je eigen vermogen is €{net_worth:,.2f}")
        elif net_worth < 0:
            st.error(
                f"📉 Je hebt een negatief eigen vermogen van €{abs(net_worth):,.2f}"
            )
        else:
            st.warning("💡 Je bezittingen en schulden zijn gelijk aan elkaar")


def show_financiele_apk() -> None:
    """Display the complete Financiele APK calculator interface.

    Main entry point for the Financiele APK calculator. Uses a step-by-step
    questionnaire to collect financial data, then displays comprehensive results.

    Returns
    -------
    None
        This function creates Streamlit UI components directly

    Example
    -------
    >>> # In Streamlit app:
    >>> show_financiele_apk()
    # Creates expandable "💶 Financiele APK" section

    Note
    ----
    Uses questionnaire-based data collection for improved user experience.
    Results are displayed automatically when the questionnaire is completed.
    The expander starts expanded to show the questionnaire.
    """
    with st.expander("💶 Financiele APK", expanded=True):
        st.write("### Financiele APK Vragenlijst")
        questionnaire = create_financiele_apk_questionnaire()
        questionnaire_data = questionnaire.run()

        # If questionnaire is completed, show results
        if questionnaire_data is not None:
            # Validate consistency before showing results
            monthly_income = questionnaire_data.get("monthly_income", 0.0)
            monthly_expenses = questionnaire_data.get("monthly_expenses", 0.0)
            monthly_leftover = questionnaire_data.get("monthly_leftover", 0.0)

            is_consistent, warning_message = validate_financial_consistency(
                monthly_income, monthly_expenses, monthly_leftover
            )

            if not is_consistent:
                st.warning(warning_message)
                st.info(
                    "💡 We gebruiken je opgegeven bedragen, maar controleer "
                    "deze nog even."
                )

            st.write("---")
            st.success("Vragenlijst voltooid! Hier is je Financiele APK:")

            # Convert questionnaire data to Financiele APK data
            financial_data = questionnaire_data_to_financiele_apk(questionnaire_data)

            # Display the summary
            display_summary(financial_data)

            # Add reset button to allow starting over
            st.write("---")
            if st.button("Opnieuw beginnen", key="reset_questionnaire"):
                questionnaire.reset()
                st.rerun()
