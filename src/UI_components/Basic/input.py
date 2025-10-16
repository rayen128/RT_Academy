"""Input Components for RT Academy Financial Calculators.

This module provides standardized user input components including currency
inputs, percentage inputs, and action buttons. All components maintain
consistent styling and behavior across the application.

Components
----------
- display_currency_input: Euro currency input fields with validation
- display_percentage_input: Percentage input fields with constraints
- display_calculation_button: Standardized action buttons
- display_reset_section: Reset functionality with confirmation

Dependencies
------------
- streamlit: Web UI framework
- typing: Type hints
"""

from typing import Optional

import streamlit as st


def display_currency_input(
    label: str,
    min_value: float = 0.0,
    value: float = 0.0,
    step: float = 100.0,
    help_text: Optional[str] = None,
    key: Optional[str] = None,
) -> float:
    """Display a standardized currency input field.

    Creates a consistent Euro currency input with proper formatting,
    validation, and help text. Includes automatic currency symbol.

    Parameters
    ----------
    label : str
        Input field label (currency symbol added automatically)
    min_value : float, optional
        Minimum allowed value, by default 0.0
    value : float, optional
        Default/initial value, by default 0.0
    step : float, optional
        Step size for increment/decrement buttons, by default 100.0
    help_text : Optional[str], optional
        Help text shown on hover, by default None
    key : Optional[str], optional
        Unique key for the input widget, by default None

    Returns
    -------
    float
        User input value

    Example
    -------
    >>> monthly_income = display_currency_input(
    ...     "Monthly Income",
    ...     value=3000.0,
    ...     step=250.0,
    ...     help_text="Enter your total monthly income after taxes",
    ...     key="income_input"
    ... )

    >>> rent_amount = display_currency_input(
    ...     "Monthly Rent",
    ...     min_value=0.0,
    ...     value=1200.0,
    ...     help_text="Include utilities if applicable"
    ... )
    """
    return st.number_input(
        f"{label} (€)",
        min_value=min_value,
        value=value,
        step=step,
        format="%.2f",
        help=help_text,
        key=key,
    )


def display_percentage_input(
    label: str,
    min_value: float = 0.0,
    max_value: float = 100.0,
    value: float = 7.0,
    step: float = 0.1,
    help_text: Optional[str] = None,
    key: Optional[str] = None,
) -> float:
    """Display a standardized percentage input field.

    Creates a consistent percentage input with proper constraints,
    formatting, and validation. Includes automatic percentage symbol.

    Parameters
    ----------
    label : str
        Input field label (percentage symbol added automatically)
    min_value : float, optional
        Minimum allowed percentage, by default 0.0
    max_value : float, optional
        Maximum allowed percentage, by default 100.0
    value : float, optional
        Default percentage value, by default 7.0
    step : float, optional
        Step size for increment/decrement, by default 0.1
    help_text : Optional[str], optional
        Help text shown on hover, by default None
    key : Optional[str], optional
        Unique key for the input widget, by default None

    Returns
    -------
    float
        User input percentage value

    Example
    -------
    >>> interest_rate = display_percentage_input(
    ...     "Annual Interest Rate",
    ...     min_value=0.0,
    ...     max_value=25.0,
    ...     value=5.5,
    ...     step=0.25,
    ...     help_text="Current market interest rate for this type of loan"
    ... )

    >>> savings_rate = display_percentage_input(
    ...     "Savings Rate",
    ...     min_value=0.0,
    ...     max_value=50.0,
    ...     value=10.0,
    ...     help_text="Percentage of income you want to save monthly"
    ... )
    """
    return st.number_input(
        f"{label} (%)",
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        format="%.1f",
        help=help_text,
        key=key,
    )


def display_calculation_button(
    label: str = "Bereken",
    key: Optional[str] = None,
    help_text: Optional[str] = None,
    button_type: str = "primary",
) -> bool:
    """Display a standardized calculation button.

    Creates a consistent action button for triggering calculations
    or form submissions. Supports different button styles.

    Parameters
    ----------
    label : str, optional
        Button text, by default "Bereken" (Dutch for "Calculate")
    key : Optional[str], optional
        Unique key for the button widget, by default None
    help_text : Optional[str], optional
        Help text shown on hover, by default None
    button_type : str, optional
        Button style type, by default "primary"
        Options: "primary", "secondary"

    Returns
    -------
    bool
        True if button was clicked in this interaction, False otherwise

    Example
    -------
    >>> if display_calculation_button("Calculate Overview", key="calc_btn"):
    ...     # Perform calculations
    ...     calculate_financial_overview()

    >>> if display_calculation_button(
    ...     "Analyze Debt",
    ...     help_text="Click to analyze your debt situation",
    ...     button_type="secondary"
    ... ):
    ...     # Perform debt analysis
    ...     analyze_debt_situation()
    """
    return st.button(label, key=key, help=help_text, type=button_type)


def display_reset_section(
    reset_function,
    reset_key: str = "reset_button",
    button_label: str = "Opnieuw beginnen",
    confirmation_required: bool = False,
) -> None:
    """Display a standardized reset section with button.

    Creates a consistent reset interface with optional confirmation.
    Includes visual separator and standardized styling.

    Parameters
    ----------
    reset_function : callable
        Function to call when reset is confirmed/clicked
    reset_key : str, optional
        Unique key for reset button, by default "reset_button"
    button_label : str, optional
        Reset button text, by default "Opnieuw beginnen" (Dutch for "Start Over")
    confirmation_required : bool, optional
        Whether to show confirmation dialog, by default False

    Example
    -------
    >>> def reset_calculator():
    ...     st.session_state.clear()
    ...     st.success("Calculator reset successfully!")

    >>> display_reset_section(
    ...     reset_calculator,
    ...     reset_key="financial_reset",
    ...     button_label="Reset Calculator",
    ...     confirmation_required=True
    ... )
    """
    st.write("---")

    if confirmation_required:
        if st.button(button_label, key=reset_key):
            if st.button("Confirm Reset", key=f"{reset_key}_confirm"):
                reset_function()
                st.rerun()
    else:
        if st.button(button_label, key=reset_key):
            reset_function()
            st.rerun()


__all__ = [
    "display_currency_input",
    "display_percentage_input",
    "display_calculation_button",
    "display_reset_section",
]
