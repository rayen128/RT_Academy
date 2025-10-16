"""Status and Validation Components for RT Academy Financial Calculators.

This module provides components for displaying status messages, validation
results, and user feedback. Components ensure consistent messaging and
help users understand their financial situation and input validation.

Components
----------
- get_financial_status_message: Generate status messages based on financial values
- display_status_message: Display styled status messages
- display_validation_results: Show validation warnings and suggestions
- display_progress_indicator: Show calculation or loading progress

Dependencies
------------
- streamlit: Web UI framework
- typing: Type hints
"""

from typing import List, Optional, Tuple

import streamlit as st


def get_financial_status_message(
    value: float,
    positive_template: str,
    negative_template: str,
    neutral_template: str,
    currency: str = "€",
) -> Tuple[str, str]:
    """Generate financial status message and type based on value.

    Creates contextual status messages for financial values with appropriate
    formatting and status types for consistent user feedback.

    Parameters
    ----------
    value : float
        Financial value to evaluate (can be positive, negative, or zero)
    positive_template : str
        Template for positive values (use {value} placeholder for amount)
    negative_template : str
        Template for negative values (use {value} placeholder for amount)
    neutral_template : str
        Template for neutral/zero values (no placeholder needed)
    currency : str, optional
        Currency symbol to use, by default "€"

    Returns
    -------
    Tuple[str, str]
        Tuple containing (message_text, status_type)
        status_type options: 'success', 'error', 'warning'

    Example
    -------
    >>> msg, status = get_financial_status_message(
    ...     750.0,
    ...     "✅ You save {value} monthly - excellent progress!",
    ...     "⚠️ You overspend {value} monthly - consider reducing expenses",
    ...     "💡 You break even - try to increase savings"
    ... )
    >>> print(f"{msg} (Status: {status})")
    ✅ You save €750.00 monthly - excellent progress! (Status: success)

    >>> msg, status = get_financial_status_message(
    ...     -200.0,
    ...     "Great! You have {value} surplus",
    ...     "Warning: You have a {value} deficit",
    ...     "You're breaking even"
    ... )
    >>> print(f"{msg} (Status: {status})")
    Warning: You have a €200.00 deficit (Status: error)
    """
    formatted_value = f"{currency}{abs(value):,.2f}"

    if value > 0:
        return positive_template.format(value=formatted_value), "success"
    elif value < 0:
        return negative_template.format(value=formatted_value), "error"
    else:
        return neutral_template, "warning"


def display_status_message(
    message: str, status_type: str, icon_override: Optional[str] = None
) -> None:
    """Display a status message with appropriate styling.

    Shows status messages using Streamlit's built-in styling with
    optional custom icons for enhanced visual communication.

    Parameters
    ----------
    message : str
        Message text to display (supports markdown formatting)
    status_type : str
        Type of status determining styling and default icon
        Options: 'success', 'error', 'warning', 'info'
    icon_override : Optional[str], optional
        Custom icon to override default status icon, by default None

    Example
    -------
    >>> display_status_message(
    ...     "Your financial health looks great!",
    ...     "success"
    ... )

    >>> display_status_message(
    ...     "Consider increasing your emergency fund",
    ...     "warning",
    ...     icon_override="🚨"
    ... )

    >>> display_status_message(
    ...     "**Debt Alert:** Your debt-to-income ratio is high",
    ...     "error"
    ... )
    """
    # Add custom icon if provided
    if icon_override:
        message = f"{icon_override} {message}"

    if status_type == "success":
        st.success(message)
    elif status_type == "error":
        st.error(message)
    elif status_type == "warning":
        st.warning(message)
    elif status_type == "info":
        st.info(message)
    else:
        st.write(message)  # Fallback for unknown status types


def display_validation_results(
    validations: List[Tuple[bool, str]],
    title: str = "Validation Results",
    show_success_count: bool = True,
    success_message: str = "All validations passed!",
) -> None:
    """Display validation results in a consistent format.

    Shows validation warnings and suggestions in a user-friendly format.
    Optionally displays success count and summary message.

    Parameters
    ----------
    validations : List[Tuple[bool, str]]
        List of (is_valid, message) tuples
        - is_valid: True if validation passed, False if failed
        - message: Validation message (empty string to skip display)
    title : str, optional
        Section title for validation results, by default "Validation Results"
    show_success_count : bool, optional
        Whether to show count of successful validations, by default True
    success_message : str, optional
        Message when all validations pass, by default "All validations passed!"

    Example
    -------
    >>> validations = [
    ...     (False, "Income seems low for your listed expenses"),
    ...     (True, "Debt-to-income ratio is within healthy range"),
    ...     (False, "Consider increasing your emergency fund to 6 months"),
    ...     (True, "")  # Valid but no message to display
    ... ]
    >>> display_validation_results(
    ...     validations,
    ...     title="Financial Health Check",
    ...     show_success_count=True
    ... )
    """
    warnings = [msg for is_valid, msg in validations if not is_valid and msg.strip()]
    passed_count = sum(1 for is_valid, _ in validations if is_valid)
    total_count = len(validations)

    if warnings:
        st.warning(f"**{title}:**")
        for warning in warnings:
            st.write(f"• {warning}")

        if show_success_count and total_count > 0:
            st.info(
                f"💡 {passed_count}/{total_count} validations passed. These suggestions can help improve your financial health."
            )
        else:
            st.info("💡 These are suggestions to improve your financial health.")
    else:
        if total_count > 0:
            st.success(f"✅ **{title}:** {success_message}")


def display_progress_indicator(
    progress_value: float,
    title: str = "Progress",
    subtitle: Optional[str] = None,
    show_percentage: bool = True,
) -> None:
    """Display a progress indicator for calculations or goals.

    Shows progress towards financial goals or calculation completion
    with optional subtitle and percentage display.

    Parameters
    ----------
    progress_value : float
        Progress value between 0.0 and 1.0 (0% to 100%)
    title : str, optional
        Progress indicator title, by default "Progress"
    subtitle : Optional[str], optional
        Additional context text below progress bar, by default None
    show_percentage : bool, optional
        Whether to show percentage text, by default True

    Example
    -------
    >>> display_progress_indicator(
    ...     0.65,
    ...     title="Emergency Fund Goal",
    ...     subtitle="€3,250 of €5,000 target",
    ...     show_percentage=True
    ... )

    >>> display_progress_indicator(
    ...     0.85,
    ...     title="Debt Payoff Progress",
    ...     subtitle="15 months remaining"
    ... )
    """
    # Ensure progress is within valid range
    progress_value = max(0.0, min(1.0, progress_value))

    if show_percentage:
        percentage_text = f" ({progress_value:.1%})"
        st.write(f"**{title}**{percentage_text}")
    else:
        st.write(f"**{title}**")

    st.progress(progress_value)

    if subtitle:
        st.caption(subtitle)


def display_comparison_status(
    current_value: float,
    target_value: float,
    label: str,
    format_as_currency: bool = True,
    improvement_threshold: float = 0.05,
) -> None:
    """Display comparison between current and target values.

    Shows current vs target comparison with status indication
    and improvement suggestions.

    Parameters
    ----------
    current_value : float
        Current actual value
    target_value : float
        Target or recommended value
    label : str
        Description of what's being compared
    format_as_currency : bool, optional
        Whether to format values as currency, by default True
    improvement_threshold : float, optional
        Percentage threshold to consider "close to target", by default 0.05 (5%)

    Example
    -------
    >>> display_comparison_status(
    ...     current_value=450.0,
    ...     target_value=500.0,
    ...     label="Monthly Savings",
    ...     format_as_currency=True
    ... )

    >>> display_comparison_status(
    ...     current_value=25.5,
    ...     target_value=20.0,
    ...     label="Debt-to-Income Ratio (%)",
    ...     format_as_currency=False
    ... )
    """
    if target_value == 0:
        return

    ratio = current_value / target_value
    difference = current_value - target_value

    # Format values based on type
    if format_as_currency:
        current_str = f"€{current_value:,.2f}"
        target_str = f"€{target_value:,.2f}"
        diff_str = f"€{abs(difference):,.2f}"
    else:
        current_str = f"{current_value:.1f}"
        target_str = f"{target_value:.1f}"
        diff_str = f"{abs(difference):.1f}"

    # Determine status
    if abs(ratio - 1.0) <= improvement_threshold:
        status = "success"
        message = (
            f"✅ **{label}:** {current_str} (Target: {target_str}) - You're on track!"
        )
    elif current_value > target_value:
        status = "warning" if ratio < 1.2 else "error"
        message = f"📈 **{label}:** {current_str} (Target: {target_str}) - {diff_str} above target"
    else:
        status = "warning" if ratio > 0.8 else "error"
        message = f"📉 **{label}:** {current_str} (Target: {target_str}) - {diff_str} below target"

    display_status_message(message, status)


__all__ = [
    "get_financial_status_message",
    "display_status_message",
    "display_validation_results",
    "display_progress_indicator",
    "display_comparison_status",
]
