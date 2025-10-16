"""Debt payoff calculator with snowball and avalanche strategies."""

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import plotly.graph_objects as go
import streamlit as st


@dataclass
class Debt:
    """Represents a debt with balance, interest rate, and minimum payment."""

    name: str
    balance: float
    interest_rate: float
    min_payment: float


@dataclass
class DebtPayoffParameters:
    """Parameters for debt payoff calculations."""

    debts: List[Debt]
    extra_payment: float


def get_user_input() -> Tuple[DebtPayoffParameters, bool]:
    """Get user input for debt payoff calculation."""
    debts = []

    col1, col2 = st.columns([3, 1])
    with col1:
        num_debts = st.number_input(
            "Aantal schulden", min_value=1, max_value=10, value=2, step=1
        )
    with col2:
        extra_payment = st.number_input(
            "Extra maandelijks bedrag (€)", min_value=0.0, value=100.0, step=50.0
        )

    st.write("### Voer je schulden in")
    for i in range(int(num_debts)):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input(f"Naam schuld {i + 1}", value=f"Schuld {i + 1}")
        with col2:
            balance = st.number_input(
                f"Openstaand bedrag {i + 1} (€)",
                min_value=0.0,
                value=1000.0 * (i + 1),
                step=100.0,
            )
        with col3:
            rate = st.number_input(
                f"Rente {i + 1} (%)",
                min_value=0.0,
                max_value=100.0,
                value=5.0 + i,
                step=0.1,
            )
        with col4:
            min_payment = st.number_input(
                f"Minimum betaling {i + 1} (€)",
                min_value=max(10.0, balance * 0.01),
                value=max(50.0, balance * 0.02),
                step=10.0,
            )

        debts.append(
            Debt(
                name=name, balance=balance, interest_rate=rate, min_payment=min_payment
            )
        )

    calculate_button = st.button("Vergelijk methodes")

    params = DebtPayoffParameters(debts=debts, extra_payment=extra_payment)

    return params, calculate_button


def calculate_snowball_payoff(
    params: DebtPayoffParameters,
) -> Tuple[Dict[str, List[float]], float, int]:
    """Calculate debt payoff using the snowball method (smallest balance first)."""
    debts = sorted(params.debts, key=lambda x: x.balance)
    return calculate_payoff(params, debts)


def calculate_avalanche_payoff(
    params: DebtPayoffParameters,
) -> Tuple[Dict[str, List[float]], float, int]:
    """Calculate debt payoff using the avalanche method (highest interest first)."""
    debts = sorted(params.debts, key=lambda x: x.interest_rate, reverse=True)
    return calculate_payoff(params, debts)


def calculate_payoff(
    params: DebtPayoffParameters, ordered_debts: List[Debt]
) -> Tuple[Dict[str, List[float]], float, int]:
    """Calculate debt payoff progression."""
    monthly_balances = {debt.name: [debt.balance] for debt in ordered_debts}
    total_paid = 0.0
    months = 0

    # Continue while any debt has a balance
    while any(balances[-1] > 0 for balances in monthly_balances.values()):
        available_payment = params.extra_payment
        new_balances = {}

        # First, make minimum payments on all debts
        for debt in ordered_debts:
            current_balance = monthly_balances[debt.name][-1]
            if current_balance > 0:
                # Calculate interest
                interest = current_balance * (debt.interest_rate / 100 / 12)
                payment = min(current_balance + interest, debt.min_payment)
                new_balance = current_balance + interest - payment
                total_paid += payment
                available_payment = max(
                    0, available_payment - max(0, payment - debt.min_payment)
                )
            else:
                new_balance = 0
            new_balances[debt.name] = new_balance

        # Then, apply extra payment to the first debt with a balance
        for debt in ordered_debts:
            if new_balances[debt.name] > 0 and available_payment > 0:
                payment = min(new_balances[debt.name], available_payment)
                new_balances[debt.name] -= payment
                total_paid += payment
                available_payment -= payment
                break

        # Add new balances to history
        for name, balance in new_balances.items():
            monthly_balances[name].append(balance)

        months += 1
        if months > 360:  # 30 years maximum
            break

    return monthly_balances, total_paid, months


def create_payoff_graph(
    snowball_data: Dict[str, List[float]],
    avalanche_data: Dict[str, List[float]],
    _months: int,  # Unused parameter prefixed with underscore
) -> go.Figure:
    """Create a comparison graph of both payoff methods showing total debt."""
    fig = go.Figure()

    # Safely get the first value list to determine the number of months
    first_snowball_values = list(snowball_data.values())[0] if snowball_data else []
    if not first_snowball_values:
        return fig

    # Calculate total debt for each month for both methods
    snowball_totals = []
    avalanche_totals = []

    for month in range(len(first_snowball_values)):
        try:
            snowball_total = sum(balances[month] for balances in snowball_data.values())
            avalanche_total = sum(
                balances[month] for balances in avalanche_data.values()
            )
            snowball_totals.append(snowball_total)
            avalanche_totals.append(avalanche_total)
        except IndexError:
            break  # Stop if we hit the end of any balance list

    # Convert months to years for x-axis
    years = np.linspace(0, len(snowball_totals) / 12, len(snowball_totals))

    # Add snowball line first
    fig.add_trace(
        go.Scatter(
            x=years,
            y=snowball_totals,
            name="Snowball Methode",
            line={"color": "#2ecc71", "width": 2},  # Groen
            fill="tozeroy",
        )
    )

    # Add avalanche line
    fig.add_trace(
        go.Scatter(
            x=years,
            y=avalanche_totals,
            name="Avalanche Methode",
            line={"color": "#3498db", "width": 2},  # Blauw
        )
    )

    # Update layout with improved styling
    fig.update_layout(
        title="Schuld Aflossing over Tijd",
        xaxis_title="Jaren",
        yaxis_title="Schuld (€)",
        hovermode="x",
        showlegend=True,
        yaxis_tickprefix="€",
    )

    return fig


def display_results(
    snowball_results: Tuple[Dict[str, List[float]], float, int],
    avalanche_results: Tuple[Dict[str, List[float]], float, int],
) -> None:
    """Display the comparison results."""
    _snowball_balances, snowball_total, snowball_months = snowball_results
    _avalanche_balances, avalanche_total, avalanche_months = avalanche_results

    # Display summary metrics
    st.write("### Resultaten")
    col1, col2 = st.columns(2)

    with col1:
        st.write("#### 🏀 Snowball Methode")
        st.metric("Totaal betaald", f"€{snowball_total:,.2f}")
        st.metric("Aantal maanden", f"{snowball_months}")

    with col2:
        st.write("#### 🏔️ Avalanche Methode")
        st.metric("Totaal betaald", f"€{avalanche_total:,.2f}")
        st.metric("Aantal maanden", f"{avalanche_months}")

    # Show which method saves more money
    savings = abs(snowball_total - avalanche_total)
    faster_months = abs(snowball_months - avalanche_months)

    if avalanche_total < snowball_total:
        st.success(
            f"De Avalanche methode bespaart je €{savings:,.2f} "
            f"en is {faster_months} maanden sneller!"
        )
    elif snowball_total < avalanche_total:
        st.success(
            f"De Snowball methode bespaart je €{savings:,.2f} "
            f"en is {faster_months} maanden sneller!"
        )
    else:
        st.info("Beide methodes geven hetzelfde resultaat in dit geval.")


def show_debt_payoff_calculator() -> None:
    """Show the debt payoff calculator."""
    with st.expander(
        "💳 Schuld Aflossing Calculator (Snowball vs. Avalanche)",
        expanded=False,
    ):
        st.write(
            """
        **Snowball Methode**: Betaal de kleinste schuld eerst af
        (motiverender door snelle overwinningen)

        **Avalanche Methode**: Betaal de schuld met hoogste rente eerst af
        (wiskundig optimaal)
        """
        )

        params, calculate_clicked = get_user_input()

        if calculate_clicked and params.debts:  # Check if we have any debts
            try:
                snowball_results = calculate_snowball_payoff(params)
                avalanche_results = calculate_avalanche_payoff(params)

                # Check if we have results
                if snowball_results[0] and avalanche_results[0]:
                    display_results(snowball_results, avalanche_results)

                    # Create and show graph only if we have valid data
                    snowball_balances = snowball_results[0]
                    avalanche_balances = avalanche_results[0]
                    if (
                        snowball_balances
                        and avalanche_balances
                        and len(list(snowball_balances.values())[0]) > 0
                    ):
                        fig = create_payoff_graph(
                            snowball_balances,
                            avalanche_balances,
                            max(snowball_results[2], avalanche_results[2]),
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(
                            "Niet genoeg gegevens om een grafiek te maken. "
                            "Controleer je invoer."
                        )
            except (ValueError, TypeError, ZeroDivisionError):
                st.error(
                    "Er is een fout opgetreden bij het berekenen. "
                    "Controleer je invoer en probeer opnieuw."
                )
