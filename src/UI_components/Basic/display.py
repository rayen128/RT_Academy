"""Display Components for RT Academy Financial Calculators.

This module provides visual presentation components including headers,
financial metrics, and information cards. These components focus on
displaying information to users in a consistent, professional manner.

Components
----------
- display_section_header: Consistent section headers with icons
- display_financial_metrics: Financial metrics in formatted columns
- display_info_card: Information cards with styling and icons

Dependencies
------------
- streamlit: Web UI framework
- typing: Type hints
"""

from typing import List, Optional, Tuple

import streamlit as st


def display_section_header(title: str, icon: str = "📊") -> None:
    """Display a consistent section header with icon.

    Creates a standardized section header that maintains visual consistency
    across all financial calculator modules.

    Parameters
    ----------
    title : str
        Section title text
    icon : str, optional
        Icon emoji to display before title, by default "📊"

    Example
    -------
    >>> display_section_header("Financial Overview", "💰")
    # Displays: "### 💰 Financial Overview"

    >>> display_section_header("Monthly Analysis")
    # Displays: "### 📊 Monthly Analysis"
    """
    st.write(f"### {icon} {title}")


def display_financial_metrics(
    metrics: List[Tuple[str, float, Optional[str], Optional[str]]],
) -> None:
    """Display a row of financial metrics in equal-width columns.

    Creates a professional dashboard-style display of financial metrics
    with optional delta indicators for changes or status.

    Parameters
    ----------
    metrics : List[Tuple[str, float, Optional[str], Optional[str]]]
        List of metric tuples containing:
        - label: Metric name/description (e.g., "Total Assets")
        - value: Monetary value to display (e.g., 10000.0)
        - delta: Optional delta text for metric (e.g., "+5%", "Improved")
        - delta_color: Optional delta color ("normal", "inverse", or None)

    Example
    -------
    >>> metrics = [
    ...     ("Total Assets", 15000.0, None, None),
    ...     ("Total Debt", 5000.0, None, None),
    ...     ("Net Worth", 10000.0, "Positive", "normal"),
    ...     ("Monthly Savings", 500.0, "+€100", "normal")
    ... ]
    >>> display_financial_metrics(metrics)
    """
    if not metrics:
        return

    cols = st.columns(len(metrics))
    for i, (label, value, delta, delta_color) in enumerate(metrics):
        with cols[i]:
            if delta and delta_color:
                st.metric(label, f"€{value:,.2f}", delta=delta, delta_color=delta_color)
            else:
                st.metric(label, f"€{value:,.2f}")


def display_info_card(
    title: str, content: str, icon: str = "💡", card_type: str = "info"
) -> None:
    """Display an information card with icon and content.

    Creates styled information cards for tips, warnings, or important
    information. Supports different visual styles based on content type.

    Parameters
    ----------
    title : str
        Card title (e.g., "Financial Tip", "Important Notice")
    content : str
        Card content text (supports markdown formatting)
    icon : str, optional
        Icon emoji to display with title, by default "💡"
    card_type : str, optional
        Card styling type, by default "info"
        Options: 'info', 'success', 'warning', 'error'

    Example
    -------
    >>> display_info_card(
    ...     "Emergency Fund Tip",
    ...     "Aim to save 3-6 months of expenses for unexpected situations.",
    ...     "🚨",
    ...     "success"
    ... )

    >>> display_info_card(
    ...     "High Debt Warning",
    ...     "Your debt-to-income ratio is above recommended levels.",
    ...     "⚠️",
    ...     "warning"
    ... )
    """
    content_with_icon = f"{icon} **{title}**\n\n{content}"

    if card_type == "info":
        st.info(content_with_icon)
    elif card_type == "success":
        st.success(content_with_icon)
    elif card_type == "warning":
        st.warning(content_with_icon)
    elif card_type == "error":
        st.error(content_with_icon)


__all__ = ["display_section_header", "display_financial_metrics", "display_info_card"]
