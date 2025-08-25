"""
Debt payoff calculator module.
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import List, Tuple, Dict
from ..utils.models import Liability as Debt  # Using the shared model


@dataclass
class DebtPayoffParameters:
    debts: List[Debt]
    extra_payment: float


def get_user_input() -> Tuple[DebtPayoffParameters, bool]:
    """Get user input for debt payoff calculation."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def calculate_snowball_payoff(params: DebtPayoffParameters) -> Tuple[Dict[str, List[float]], float, int]:
    """Calculate debt payoff using the snowball method (smallest balance first)."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def calculate_avalanche_payoff(params: DebtPayoffParameters) -> Tuple[Dict[str, List[float]], float, int]:
    """Calculate debt payoff using the avalanche method (highest interest first)."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def calculate_payoff(params: DebtPayoffParameters, ordered_debts: List[Debt]) -> Tuple[Dict[str, List[float]], float, int]:
    """Calculate debt payoff progression."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def create_payoff_graph(snowball_data: Dict[str, List[float]],
                        avalanche_data: Dict[str, List[float]],
                        months: int) -> go.Figure:
    """Create a comparison graph of both payoff methods."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def display_results(snowball_results: Tuple[Dict[str, List[float]], float, int],
                    avalanche_results: Tuple[Dict[str, List[float]], float, int]):
    """Display the comparison results."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)


def show_debt_payoff_calculator():
    """Main function to show the debt payoff calculator."""
    # Rest of the existing code remains the same
    ...  # (keeping existing implementation)
