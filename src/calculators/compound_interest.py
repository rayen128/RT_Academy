import streamlit as st
import plotly.graph_objects as go
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Sequence, Optional


@dataclass
class InvestmentParameters:
    principal: float
    interest_rate: float
    monthly_contribution: float
    goal_amount: float
    time_years: int
    compounds_per_year: int


def get_user_input() -> Tuple[InvestmentParameters, bool]:
    """Get user input from Streamlit widgets and return investment parameters."""

    # Simple mode by default
    principal = st.number_input(
        'Startbedrag (€)', min_value=0.0, value=1000.0, step=100.0)
    monthly_contribution = st.number_input(
        'Maandelijkse inleg (€)', min_value=0.0, value=100.0, step=10.0)

    # Default values for simple mode
    interest_rate = 7.0  # 7% default return
    compounds_per_year = 1  # Yearly compounding
    goal_amount = 0.0  # No goal
    time_years = 30  # 30 years by default

    # Advanced mode toggle
    advanced_mode = st.checkbox('Geavanceerde instellingen')

    if advanced_mode:
        col1, col2 = st.columns(2)
        with col1:
            interest_rate = st.number_input(
                'Jaarlijkse rentevoet (%)', min_value=0.0, max_value=100.0, value=7.0, step=0.1)
            compounds_per_year = st.selectbox('Samenstellingsfrequentie',
                                              ['Jaarlijks', 'Halfjaarlijks', 'Per kwartaal', 'Maandelijks'], index=0)
        with col2:
            goal_amount = st.number_input(
                'Doelbedrag (€)', min_value=0.0, value=0.0, step=1000.0)
            time_years = st.number_input(
                'Tijd (jaren)', min_value=0, value=30, step=1)

        # Convert compounding frequency to number
        frequency_dict = {
            'Jaarlijks': 1,
            'Halfjaarlijks': 2,
            'Per kwartaal': 4,
            'Maandelijks': 12
        }
        compounds_per_year = frequency_dict[compounds_per_year]

    calculate_button = st.button('Bereken')

    params = InvestmentParameters(
        principal=principal,
        interest_rate=interest_rate,
        monthly_contribution=monthly_contribution,
        goal_amount=goal_amount,
        time_years=time_years,
        compounds_per_year=compounds_per_year
    )

    return params, calculate_button


def calculate_investment_growth(params: InvestmentParameters) -> Tuple[Sequence[float], float, float]:
    """Calculate investment growth over time with compound interest.

    Args:
        params (InvestmentParameters): Investment parameters including principal,
            interest rate, monthly contributions, and time period.

    Returns:
        Tuple[Sequence[float], float, float]: A tuple containing:
            - List of investment values over time (monthly)
            - Total contributions (principal + monthly contributions)
            - Total interest earned (final amount - total contributions)

    Example:
        >>> params = InvestmentParameters(
        ...     principal=1000,
        ...     interest_rate=7,
        ...     monthly_contribution=100,
        ...     goal_amount=0,
        ...     time_years=30,
        ...     compounds_per_year=1
        ... )
        >>> values, contributions, interest = calculate_investment_growth(params)
        >>> len(values)  # One value per month plus initial
        361
    """
    rate = params.interest_rate / 100
    monthly_rate = rate / 12
    months = int(params.time_years * 12)

    values = []
    total_contributions = params.principal
    current_amount = params.principal

    for month in range(months + 1):
        values.append(current_amount)
        if month < months:
            current_amount = (
                current_amount + params.monthly_contribution) * (1 + monthly_rate)
            total_contributions += params.monthly_contribution

    final_amount = values[-1]
    interest_earned = final_amount - total_contributions

    return values, total_contributions, interest_earned


def calculate_years_to_goal(values: Sequence[float], goal_amount: float) -> Optional[float]:
    """Calculate how many years it will take to reach the goal amount.

    Args:
        values (Sequence[float]): List of investment values over time (monthly)
        goal_amount (float): Target investment amount to reach

    Returns:
        Optional[float]: Number of years needed to reach goal, or None if goal
            is not reached within the given time period

    Example:
        >>> values = [1000, 1200, 1400, 1600]  # Monthly values
        >>> calculate_years_to_goal(values, 1500)
        0.25  # Takes 3 months (0.25 years) to reach 1500
    """
    if values[-1] >= goal_amount:
        for i, value in enumerate(values):
            if value >= goal_amount:
                return i / 12
    return None


def display_results(values: Sequence[float],
                    total_contributions: float,
                    interest_earned: float,
                    goal_amount: float) -> None:
    """Display the investment calculation results in Streamlit.

    Args:
        values (Sequence[float]): List of investment values over time
        total_contributions (float): Sum of principal and all contributions
        interest_earned (float): Total interest earned on the investment
        goal_amount (float): Target investment amount (0 for no goal)

    Returns:
        None: This function updates the Streamlit UI directly

    Note:
        This function uses Streamlit's metric and success/warning components
        to display results in a user-friendly format.
    """
    final_amount = values[-1]
    years_to_goal = calculate_years_to_goal(values, goal_amount)

    st.write('### Resultaten')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Eindbedrag', f'€{final_amount:,.2f}')
    with col2:
        st.metric('Totaal ingelegd', f'€{total_contributions:,.2f}')
    with col3:
        st.metric('Verdiende rente', f'€{interest_earned:,.2f}')

    # Display goal achievement message
    if years_to_goal:
        st.success(
            f'Je bereikt je doel van €{goal_amount:,.2f} in {years_to_goal:.1f} jaar!')
    elif goal_amount > 0:
        st.warning(
            'Met de huidige instellingen wordt je doel niet bereikt binnen de gegeven periode.')


def create_investment_graph(values: Sequence[float],
                            time_years: int,
                            goal_amount: float) -> go.Figure:
    """Create an interactive plot showing investment growth over time.

    Args:
        values (Sequence[float]): List of investment values over time
        time_years (int): Total investment period in years
        goal_amount (float): Target investment amount (0 for no goal)

    Returns:
        go.Figure: A Plotly figure object containing the investment growth
            visualization with optional goal line

    Note:
        The graph includes:
        - Area plot showing investment growth
        - Optional horizontal line for goal amount
        - Hover information for values
        - Properly formatted axis labels and currency values
    """
    years = np.linspace(0, time_years, len(values))

    fig = go.Figure()

    # Add investment growth line
    fig.add_trace(go.Scatter(
        x=years,
        y=values,
        name='Totaal bedrag',
        fill='tozeroy'
    ))

    # Add goal line if goal is set
    if goal_amount > 0:
        fig.add_hline(
            y=goal_amount,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Doel: €{goal_amount:,.0f}",
            annotation_position="right"
        )

    # Customize the graph
    fig.update_layout(
        title='Groei van investering over tijd',
        xaxis_title='Jaren',
        yaxis_title='Bedrag (€)',
        hovermode='x',
        showlegend=True,
        yaxis_tickprefix='€'
    )

    return fig


def show_compound_interest_calculator() -> None:
    """Display and run the compound interest calculator in Streamlit.

    This is the main entry point for the compound interest calculator.
    It creates an expander section in the Streamlit UI containing:
    1. Input form (simple or advanced mode)
    2. Calculation button
    3. Results display
    4. Interactive growth visualization

    The calculator supports two modes:
    - Simple: Only principal and monthly contribution
    - Advanced: All parameters including interest rate and goal amount

    Returns:
        None: This function updates the Streamlit UI directly
    """
    with st.expander("💰 Samengestelde Interest Calculator", expanded=False):
        params, calculate_clicked = get_user_input()

        if calculate_clicked:
            # Calculate investment growth
            values, total_contributions, interest_earned = calculate_investment_growth(
                params)

            # Display results and graph
            display_results(values, total_contributions,
                            interest_earned, params.goal_amount)
            fig = create_investment_graph(
                values, params.time_years, params.goal_amount)
            st.plotly_chart(fig, use_container_width=True)
