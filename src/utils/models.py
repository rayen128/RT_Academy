"""Shared data models for financial calculations."""

from dataclasses import dataclass


@dataclass
class MonthlyFlow:
    """Represents a monthly cash flow item with name and amount."""

    name: str
    amount: float


@dataclass
class Asset:
    """Represents a financial asset with name and value."""

    name: str
    value: float


@dataclass
class Liability:
    """Represents a financial liability with name and amount."""

    name: str
    amount: float
