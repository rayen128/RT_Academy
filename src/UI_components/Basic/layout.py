"""Layout Components for RT Academy Financial Calculators.

This module provides structural and organizational components for creating
consistent layouts across financial calculator interfaces. Components focus
on content organization and responsive design patterns.

Components
----------
- display_two_column_layout: Side-by-side content organization
- display_expandable_section: Collapsible content sections
- display_content_container: Standardized content containers

Dependencies
------------
- streamlit: Web UI framework
- typing: Type hints
"""

from typing import Callable, Optional

import streamlit as st


def display_two_column_layout(
    left_content_func: Callable,
    right_content_func: Callable,
    left_title: Optional[str] = None,
    right_title: Optional[str] = None,
    column_ratio: tuple = (1, 1),
) -> None:
    """Display content in a standardized two-column layout.

    Creates a responsive two-column layout with optional titles and
    customizable column ratios. Ideal for comparing data or showing
    related information side-by-side.

    Parameters
    ----------
    left_content_func : Callable
        Function to render left column content (no parameters)
    right_content_func : Callable
        Function to render right column content (no parameters)
    left_title : Optional[str], optional
        Title for left column, by default None
    right_title : Optional[str], optional
        Title for right column, by default None
    column_ratio : tuple, optional
        Ratio of column widths (left, right), by default (1, 1)
        Examples: (1, 1) = equal, (2, 1) = left twice as wide

    Example
    -------
    >>> def show_income_chart():
    ...     st.bar_chart(income_data)

    >>> def show_expense_chart():
    ...     st.bar_chart(expense_data)

    >>> display_two_column_layout(
    ...     show_income_chart,
    ...     show_expense_chart,
    ...     left_title="Monthly Income",
    ...     right_title="Monthly Expenses",
    ...     column_ratio=(2, 3)  # Expenses chart slightly wider
    ... )
    """
    col1, col2 = st.columns(column_ratio)

    with col1:
        if left_title:
            st.write(f"**{left_title}**")
        left_content_func()

    with col2:
        if right_title:
            st.write(f"**{right_title}**")
        right_content_func()


def display_expandable_section(
    title: str, content_func: Callable, expanded: bool = False, icon: str = "📊"
) -> None:
    """Display content in an expandable section.

    Creates a collapsible section that helps organize content and
    reduce visual clutter. Useful for optional or advanced features.

    Parameters
    ----------
    title : str
        Section title displayed in the expander header
    content_func : Callable
        Function to render section content (no parameters)
    expanded : bool, optional
        Whether section starts expanded, by default False
    icon : str, optional
        Icon for section title, by default "📊"

    Example
    -------
    >>> def show_advanced_options():
    ...     st.slider("Risk Tolerance", 1, 10, 5)
    ...     st.selectbox(
    ...         "Investment Strategy", ["Conservative", "Moderate", "Aggressive"]
    ...     )

    >>> display_expandable_section(
    ...     "Advanced Settings",
    ...     show_advanced_options,
    ...     expanded=False,
    ...     icon="⚙️"
    ... )

    >>> def show_calculation_details():
    ...     st.write("Detailed calculation breakdown...")
    ...     st.json(calculation_data)

    >>> display_expandable_section(
    ...     "Calculation Details",
    ...     show_calculation_details,
    ...     expanded=True,
    ...     icon="🔍"
    ... )
    """
    with st.expander(f"{icon} {title}", expanded=expanded):
        content_func()


def display_content_container(
    content_func: Callable,
    container_type: str = "container",
    border: bool = False,
    height: Optional[int] = None,
) -> None:
    """Display content in a standardized container.

    Creates consistent content containers with optional styling
    and size constraints. Helps maintain visual consistency.

    Parameters
    ----------
    content_func : Callable
        Function to render container content (no parameters)
    container_type : str, optional
        Type of container, by default "container"
        Options: "container", "empty", "sidebar"
    border : bool, optional
        Whether to show container border, by default False
    height : Optional[int], optional
        Fixed container height in pixels, by default None

    Example
    -------
    >>> def show_summary():
    ...     st.write("Financial Summary")
    ...     st.metric("Total", "€10,000")

    >>> display_content_container(
    ...     show_summary,
    ...     container_type="container",
    ...     border=True,
    ...     height=200
    ... )
    """
    if container_type == "container":
        container = st.container(border=border, height=height)
    elif container_type == "empty":
        container = st.empty()
    else:
        container = st.container(border=border, height=height)

    with container:
        content_func()


def display_category_navigation(
    categories: list,
    current_category_idx: int,
    progress_data: dict,
    on_category_change_key: str = "category_nav",
) -> Optional[int]:
    """Display an interactive category navigation panel.

    Creates a sidebar or section showing all categories with their progress
    and allows direct navigation between categories.

    Parameters
    ----------
    categories : list
        List of category objects with name, description, icon attributes
    current_category_idx : int
        Index of currently active category
    progress_data : dict
        Dictionary mapping category names to progress information
    on_category_change_key : str
        Unique key for the navigation component

    Returns
    -------
    Optional[int]
        New category index if changed, None if no change
    """
    st.subheader("📋 Categorie Overzicht")

    # Calculate overall progress
    total_categories = len(categories)
    completed_categories = sum(
        1
        for cat in categories
        if hasattr(progress_data.get(cat.name, {}), "completed")
        and progress_data.get(cat.name, {}).completed
    )
    overall_progress = (
        completed_categories / total_categories if total_categories > 0 else 0
    )

    # Show overall progress
    st.progress(
        overall_progress,
        text=f"Voortgang: {completed_categories}/{total_categories} categorieën voltooid",
    )

    st.write("---")

    # Create navigation buttons for each category
    for idx, category in enumerate(categories):
        category_progress = progress_data.get(category.name)
        is_completed = category_progress.completed if category_progress else False
        is_current = idx == current_category_idx

        # Determine status icon and color
        if is_completed:
            status_icon = "✅"
            status_text = "Voltooid"
        elif is_current:
            status_icon = "🔄"
            status_text = "Actief"
        else:
            status_icon = "⏳"
            status_text = "Wachtend"

        # Create button layout
        col1, col2 = st.columns([4, 1])

        with col1:
            # Create button with category info
            button_text = f"{category.icon} {category.name}"
            if st.button(
                button_text,
                key=f"{on_category_change_key}_cat_{idx}",
                type="primary" if is_current else "secondary",
                disabled=is_current,
                use_container_width=True,
            ):
                return idx

        with col2:
            st.write(f"{status_icon}")

        # Show category description and progress details
        if is_current:
            st.caption(f"📝 {category.description}")

            # Show question progress within category
            if hasattr(category, "questions") and category_progress:
                current_q = category_progress.current_question
                total_q = len(category.questions)
                if total_q > 0:
                    q_progress = current_q / total_q
                    st.progress(q_progress, text=f"Vraag {current_q + 1}/{total_q}")
        elif not is_current:
            with st.expander(f"📋 Details van {category.name}", expanded=False):
                st.caption(f"📝 {category.description}")
                st.caption(f"Status: {status_text}")

    return None


def display_question_navigation(
    questions: list,
    current_question_idx: int,
    category_name: str,
    navigation_key: str = "question_nav",
) -> Optional[int]:
    """Display navigation for questions within a category.

    Creates a horizontal navigation bar showing question numbers
    and allowing direct navigation to specific questions.

    Parameters
    ----------
    questions : list
        List of question objects
    current_question_idx : int
        Index of currently active question
    category_name : str
        Name of the current category
    navigation_key : str
        Unique key for the navigation component

    Returns
    -------
    Optional[int]
        New question index if changed, None if no change
    """
    if len(questions) <= 1:
        return None

    st.subheader(f"🔢 Vragennavigatie - {category_name}")

    # Create question number buttons
    # Max 10 columns to prevent overflow
    cols = st.columns(min(len(questions), 10))

    for idx, question in enumerate(questions):
        col_idx = idx % 10  # Wrap to next row if more than 10 questions
        if idx > 0 and col_idx == 0:
            # Create new row
            cols = st.columns(min(len(questions) - idx, 10))

        with cols[col_idx]:
            is_current = idx == current_question_idx
            button_text = f"{idx + 1}"

            if st.button(
                button_text,
                key=f"{navigation_key}_{category_name}_q_{idx}",
                type="primary" if is_current else "secondary",
                disabled=is_current,
                use_container_width=True,
                help=f"Ga naar vraag {idx + 1}: {question.text[:50]}...",
            ):
                return idx

    return None


def display_tabs_layout(tab_configs: list, _default_tab: int = 0) -> None:
    """Display content in a tabbed layout.

    Creates a tabbed interface for organizing related content.
    Each tab can contain different content and functionality.

    Parameters
    ----------
    tab_configs : list
        List of tab configuration dictionaries containing:
        - 'label': Tab display name
        - 'content_func': Function to render tab content
        - 'icon': Optional icon for tab (included in label)
    default_tab : int, optional
        Index of default active tab, by default 0

    Example
    -------
    >>> def show_overview():
    ...     st.write("Financial overview content")

    >>> def show_details():
    ...     st.write("Detailed analysis content")

    >>> tab_configs = [
    ...     {'label': '📊 Overview', 'content_func': show_overview},
    ...     {'label': '🔍 Details', 'content_func': show_details}
    ... ]
    >>> display_tabs_layout(tab_configs, default_tab=0)
    """
    if not tab_configs:
        return

    tab_labels = [config["label"] for config in tab_configs]
    tabs = st.tabs(tab_labels)

    for _, (tab, config) in enumerate(zip(tabs, tab_configs)):
        with tab:
            config["content_func"]()


__all__ = [
    "display_two_column_layout",
    "display_expandable_section",
    "display_content_container",
    "display_tabs_layout",
]
