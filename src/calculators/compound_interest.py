import streamlit as st
import plotly.graph_objects as go
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


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

    col1, col2 = st.columns(2)
    with col1:
        principal = st.number_input(
            'Startbedrag (€)', min_value=0.0, value=1000.0, step=100.0)
        interest_rate = st.number_input(
            'Jaarlijkse rentevoet (%)', min_value=0.0, max_value=100.0, value=5.0, step=0.1)
        monthly_contribution = st.number_input(
            'Maandelijkse inleg (€)', min_value=0.0, value=100.0, step=10.0)
    with col2:
        goal_amount = st.number_input(
            'Doelbedrag (€)', min_value=0.0, value=10000.0, step=1000.0)
        time_years = st.number_input(
            'Tijd (jaren)', min_value=0, value=5, step=1)
        compounds_per_year = st.selectbox('Samenstellingsfrequentie',
                                          ['Jaarlijks', 'Halfjaarlijks', 'Per kwartaal', 'Maandelijks'], index=0)

    # Convert compounding frequency to number
    frequency_dict = {
        'Jaarlijks': 1,
        'Halfjaarlijks': 2,
        'Per kwartaal': 4,
        'Maandelijks': 12
    }

    calculate_button = st.button('Bereken')

    params = InvestmentParameters(
        principal=principal,
        interest_rate=interest_rate,
        monthly_contribution=monthly_contribution,
        goal_amount=goal_amount,
        time_years=time_years,
        compounds_per_year=frequency_dict[compounds_per_year]
    )

    return params, calculate_button


def calculate_investment_growth(params: InvestmentParameters) -> Tuple[List[float], float, float]:
    """Calculate investment growth over time.

    Returns:
        Tuple containing:
        - List of values over time
        - Total contributions
        - Interest earned
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


def calculate_years_to_goal(values: List[float], goal_amount: float) -> float:
    """Calculate how many years it will take to reach the goal amount."""
    if values[-1] >= goal_amount:
        for i, value in enumerate(values):
            if value >= goal_amount:
                return i / 12
    return None


def display_results(values: List[float], total_contributions: float, interest_earned: float, goal_amount: float):
    """Display the calculation results in Streamlit."""
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


def create_investment_graph(values: List[float], time_years: int, goal_amount: float) -> go.Figure:
    """Create an interactive plot showing investment growth over time."""
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


def show_compound_interest_calculator():
    """Main function to show the compound interest calculator."""
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
