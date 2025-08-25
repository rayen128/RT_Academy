"""
Compound interest calculator module.
"""
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
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def calculate_investment_growth(params: InvestmentParameters) -> Tuple[List[float], float, float]:
    """Calculate investment growth over time."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def calculate_years_to_goal(values: List[float], goal_amount: float) -> float:
    """Calculate how many years it will take to reach the goal amount."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def display_results(values: List[float], total_contributions: float, interest_earned: float, goal_amount: float):
    """Display the calculation results in Streamlit."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def create_investment_graph(values: List[float], time_years: int, goal_amount: float) -> go.Figure:
    """Create an interactive plot showing investment growth over time."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def show_compound_interest_calculator():
    """Main function to show the compound interest calculator."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)
