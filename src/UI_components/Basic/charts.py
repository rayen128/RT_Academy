"""Chart Components for RT Academy Financial Calculators.

This module provides chart visualization components with integrated status
messaging and financial context. Components combine Plotly charts with
contextual financial insights and status indicators.

Components
----------
- display_chart_with_status: Charts with conditional status messages
- create_financial_bar_chart: Standardized financial bar charts
- create_financial_line_chart: Time-series financial charts
- display_chart_comparison: Side-by-side chart comparisons

Dependencies
------------
- streamlit: Web UI framework
- plotly.graph_objects: Chart creation
- typing: Type hints
"""

from typing import Dict, List, Optional, Tuple, Union

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .status import display_status_message, get_financial_status_message


def display_chart_with_status(
    title: str,
    figure: go.Figure,
    value: float,
    positive_message: str,
    negative_message: str,
    neutral_message: str,
    currency: str = "€",
) -> None:
    """Display a chart with conditional status message below.

    Creates a professional chart display with contextual status messaging
    based on calculated financial values. Ideal for showing insights
    alongside visualizations.

    Parameters
    ----------
    title : str
        Chart title displayed above the chart
    figure : go.Figure
        Plotly figure object to display
    value : float
        Value to evaluate for status message generation
    positive_message : str
        Message template for positive values (use {value} placeholder)
    negative_message : str
        Message template for negative values (use {value} placeholder)
    neutral_message : str
        Message for zero/neutral values (no placeholder)
    currency : str, optional
        Currency symbol for value formatting, by default "€"

    Example
    -------
    >>> import plotly.graph_objects as go
    >>> fig = go.Figure(go.Bar(
    ...     x=["Income", "Expenses"],
    ...     y=[3000, 2500],
    ...     marker_color=["green", "red"]
    ... ))
    >>> fig.update_layout(title="Monthly Cash Flow")

    >>> display_chart_with_status(
    ...     "Monthly Financial Overview",
    ...     fig,
    ...     500.0,  # Income - Expenses
    ...     "✅ Great! You save {value} monthly",
    ...     "⚠️ Alert: You overspend {value} monthly",
    ...     "💡 You break even - consider increasing income"
    ... )
    """
    st.write(f"**{title}**")
    st.plotly_chart(figure, use_container_width=True)

    # Generate and display status message
    message, status_type = get_financial_status_message(
        value, positive_message, negative_message, neutral_message, currency
    )
    display_status_message(message, status_type)


def create_financial_bar_chart(
    categories: List[str],
    values: List[float],
    title: str,
    colors: Optional[List[str]] = None,
    currency: str = "€",
    show_values: bool = True,
) -> go.Figure:
    """Create a standardized financial bar chart.

    Creates consistent bar charts for financial data with proper formatting,
    colors, and value display options.

    Parameters
    ----------
    categories : List[str]
        Category labels for x-axis (e.g., ["Income", "Expenses", "Savings"])
    values : List[float]
        Monetary values for each category
    title : str
        Chart title
    colors : Optional[List[str]], optional
        Custom colors for bars, by default uses financial color scheme
    currency : str, optional
        Currency symbol for formatting, by default "€"
    show_values : bool, optional
        Whether to show values on bars, by default True

    Returns
    -------
    go.Figure
        Configured Plotly figure ready for display

    Example
    -------
    >>> categories = ["Monthly Income", "Fixed Expenses", "Variable Expenses", "Savings"]
    >>> values = [3000.0, 1200.0, 800.0, 500.0]
    >>> fig = create_financial_bar_chart(
    ...     categories,
    ...     values,
    ...     "Monthly Budget Breakdown",
    ...     colors=["#2E8B57", "#DC143C", "#FF6347", "#4169E1"]
    ... )
    >>> st.plotly_chart(fig, use_container_width=True)
    """
    # Default financial color scheme
    if colors is None:
        default_colors = [
            "#2E8B57",
            "#DC143C",
            "#FF6347",
            "#4169E1",
            "#8A2BE2",
            "#20B2AA",
        ]
        colors = default_colors[: len(categories)]

    # Format values for display
    text_values = [f"{currency}{v:,.0f}" for v in values] if show_values else None

    fig = go.Figure(
        data=[
            go.Bar(
                x=categories,
                y=values,
                text=text_values,
                textposition="auto",
                marker_color=colors,
                hovertemplate=f"<b>%{{x}}</b><br>{currency}%{{y:,.2f}}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=title,
        xaxis_title="Category",
        yaxis_title=f"Amount ({currency})",
        yaxis=dict(tickformat=f"{currency},.0f"),
        showlegend=False,
        height=400,
    )

    return fig


def create_financial_line_chart(
    x_values: List[Union[str, int, float]],
    y_values: List[float],
    title: str,
    x_label: str = "Time",
    y_label: str = "Amount",
    currency: str = "€",
    line_color: str = "#2E8B57",
) -> go.Figure:
    """Create a standardized financial line chart for time series data.

    Creates consistent line charts for tracking financial metrics over time
    with proper formatting and hover information.

    Parameters
    ----------
    x_values : List[Union[str, int, float]]
        X-axis values (time periods, months, years, etc.)
    y_values : List[float]
        Y-axis monetary values
    title : str
        Chart title
    x_label : str, optional
        X-axis label, by default "Time"
    y_label : str, optional
        Y-axis label, by default "Amount"
    currency : str, optional
        Currency symbol for formatting, by default "€"
    line_color : str, optional
        Line color in hex format, by default "#2E8B57" (forest green)

    Returns
    -------
    go.Figure
        Configured Plotly figure ready for display

    Example
    -------
    >>> months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    >>> savings = [500, 750, 600, 900, 800, 1000]
    >>> fig = create_financial_line_chart(
    ...     months,
    ...     savings,
    ...     "Monthly Savings Progress",
    ...     x_label="Month",
    ...     y_label="Savings Amount",
    ...     line_color="#4169E1"
    ... )
    >>> st.plotly_chart(fig, use_container_width=True)
    """
    fig = go.Figure(
        data=[
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines+markers",
                line=dict(color=line_color, width=3),
                marker=dict(size=8, color=line_color),
                hovertemplate=f"<b>%{{x}}</b><br>{currency}%{{y:,.2f}}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=f"{y_label} ({currency})",
        yaxis=dict(tickformat=f"{currency},.0f"),
        height=400,
    )

    return fig


def create_financial_pie_chart(
    labels: List[str],
    values: List[float],
    title: str,
    colors: Optional[List[str]] = None,
    currency: str = "€",
) -> go.Figure:
    """Create a standardized financial pie chart for expense/income breakdown.

    Creates consistent pie charts for showing financial category distributions
    with proper formatting and color schemes.

    Parameters
    ----------
    labels : List[str]
        Category labels for pie slices
    values : List[float]
        Monetary values for each category
    title : str
        Chart title
    colors : Optional[List[str]], optional
        Custom colors for pie slices, by default uses financial color scheme
    currency : str, optional
        Currency symbol for formatting, by default "€"

    Returns
    -------
    go.Figure
        Configured Plotly figure ready for display

    Example
    -------
    >>> expense_categories = ["Housing", "Food", "Transportation", "Entertainment", "Savings"]
    >>> expense_amounts = [1200, 400, 300, 200, 500]
    >>> fig = create_financial_pie_chart(
    ...     expense_categories,
    ...     expense_amounts,
    ...     "Monthly Expense Distribution"
    ... )
    >>> st.plotly_chart(fig, use_container_width=True)
    """
    # Default financial color scheme for pie charts
    if colors is None:
        colors = [
            "#2E8B57",
            "#DC143C",
            "#FF6347",
            "#4169E1",
            "#8A2BE2",
            "#20B2AA",
            "#FF1493",
            "#32CD32",
            "#FF4500",
            "#9400D3",
        ][: len(labels)]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.3,  # Creates a donut chart
                marker=dict(colors=colors),
                textinfo="label+percent",
                hovertemplate=f"<b>%{{label}}</b><br>{currency}%{{value:,.2f}}<br>%{{percent}}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=title,
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5),
    )

    return fig


def display_chart_comparison(
    chart1: go.Figure,
    chart2: go.Figure,
    title1: str,
    title2: str,
    overall_title: Optional[str] = None,
) -> None:
    """Display two charts side-by-side for comparison.

    Creates a side-by-side comparison layout for related financial charts
    with optional overall title.

    Parameters
    ----------
    chart1 : go.Figure
        Left chart figure
    chart2 : go.Figure
        Right chart figure
    title1 : str
        Title for left chart
    title2 : str
        Title for right chart
    overall_title : Optional[str], optional
        Overall comparison title, by default None

    Example
    -------
    >>> income_chart = create_financial_bar_chart(["Salary", "Freelance"], [3000, 500], "Income")
    >>> expense_chart = create_financial_pie_chart(["Rent", "Food", "Other"], [1200, 400, 400], "Expenses")
    >>> display_chart_comparison(
    ...     income_chart,
    ...     expense_chart,
    ...     "Monthly Income Sources",
    ...     "Monthly Expense Breakdown",
    ...     overall_title="Income vs Expenses Analysis"
    ... )
    """
    if overall_title:
        st.write(f"### {overall_title}")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**{title1}**")
        st.plotly_chart(chart1, use_container_width=True)

    with col2:
        st.write(f"**{title2}**")
        st.plotly_chart(chart2, use_container_width=True)


__all__ = [
    "display_chart_with_status",
    "create_financial_bar_chart",
    "create_financial_line_chart",
    "create_financial_pie_chart",
    "display_chart_comparison",
]
