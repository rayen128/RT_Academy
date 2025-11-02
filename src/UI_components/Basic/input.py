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

from typing import Callable, Optional, Union, cast

import streamlit as st


def display_currency_input(  # pylint: disable=too-many-arguments,too-many-positional-arguments
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
    return cast(
        float,
        st.number_input(
            f"{label} (€)",
            min_value=float(min_value),
            value=float(value),
            step=float(step),
            format="%.2f",
            help=help_text,
            key=key,
        ),
    )


def display_percentage_input(  # pylint: disable=too-many-arguments,too-many-positional-arguments
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
    return cast(
        float,
        st.number_input(
            f"{label} (%)",
            min_value=float(min_value),
            max_value=float(max_value),
            value=float(value),
            step=float(step),
            format="%.1f",
            help=help_text,
            key=key,
        ),
    )


def display_smart_number_input(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    label: str,
    min_value: Union[int, float] = 0,
    max_value: Optional[Union[int, float]] = None,
    value: Union[int, float] = 0,
    step: Union[int, float] = 1,
    format_str: str = "%.2f",
    help_text: Optional[str] = None,
    key: Optional[str] = None,
    auto_detect_type: bool = True,
) -> Union[int, float]:
    """Smart number input that auto-detects currency/percentage based on label.

    Automatically detects if the input should be a currency or percentage field
    based on keywords in the label text, then delegates to the appropriate
    specialized input component for consistent formatting and behavior.

    Parameters
    ----------
    label : str
        Input field label (used for auto-detection)
    min_value : Union[int, float], optional
        Minimum allowed value, by default 0
    max_value : Optional[Union[int, float]], optional
        Maximum allowed value, by default None
    value : Union[int, float], optional
        Default/initial value, by default 0
    step : Union[int, float], optional
        Step size for increment/decrement buttons, by default 1
    format_str : str, optional
        Format string for display (used for fallback only), by default "%.2f"
    help_text : Optional[str], optional
        Help text shown on hover, by default None
    key : Optional[str], optional
        Unique key for the input widget, by default None
    auto_detect_type : bool, optional
        Whether to enable auto-detection, by default True

    Returns
    -------
    Union[int, float]
        User input value

    Example
    -------
    >>> # Auto-detects as currency input
    >>> income = display_smart_number_input(
    ...     "Monthly Income (€)",
    ...     value=3000.0,
    ...     step=250.0,
    ...     help_text="Enter your total monthly income"
    ... )

    >>> # Auto-detects as percentage input
    >>> rate = display_smart_number_input(
    ...     "Interest Rate (%)",
    ...     value=5.5,
    ...     step=0.1,
    ...     help_text="Annual interest rate"
    ... )

    >>> # Falls back to standard number input
    >>> age = display_smart_number_input(
    ...     "Age",
    ...     min_value=16,
    ...     max_value=100,
    ...     value=30,
    ...     step=1
    ... )
    """
    if auto_detect_type:
        # Currency detection - look for currency-related keywords
        is_currency = (
            "€" in label.lower()
            or "euro" in label.lower()
            or "bedrag" in label.lower()
            or "kosten" in label.lower()
            or "prijs" in label.lower()
            or "waarde" in label.lower()
            or "saldo" in label.lower()
            or "schuld" in label.lower()
            or "inkomen" in label.lower()
            or "uitgaven" in label.lower()
        )

        # Percentage detection - look for percentage-related keywords
        is_percentage = (
            "%" in label.lower()
            or "percentage" in label.lower()
            or "procent" in label.lower()
            or "rente" in label.lower()
            or "rendement" in label.lower()
        )

        if is_currency:
            # Clean label by removing currency symbols
            clean_label = label.replace("(€)", "").replace("€", "").strip()
            return display_currency_input(
                clean_label,
                min_value=float(min_value),
                value=float(value),
                step=float(step),
                help_text=help_text,
                key=key,
            )
        elif is_percentage:
            # Clean label by removing percentage symbols
            clean_label = label.replace("(%)", "").replace("%", "").strip()
            max_val_pct = max_value if max_value is not None else 100.0
            return display_percentage_input(
                clean_label,
                min_value=float(min_value),
                max_value=float(max_val_pct),
                value=float(value),
                step=float(step),
                help_text=help_text,
                key=key,
            )

    # Fallback to standard number input for non-currency/percentage fields
    # or when auto-detection is disabled
    return cast(
        Union[int, float],
        st.number_input(
            label,
            min_value=min_value,
            max_value=max_value,
            value=value,
            step=step,
            format=format_str,
            help=help_text,
            key=key,
        ),
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
    return cast(bool, st.button(label, key=key, help=help_text, type=button_type))


def display_reset_section(
    reset_function: Callable,
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
    "display_smart_number_input",
    "display_calculation_button",
    "display_reset_section",
]
