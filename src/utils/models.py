"""
Shared data models for financial calculations.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class MonthlyFlow:
    """Represents a monthly financial flow (income or expense)."""
    name: str
    amount: float


@dataclass
class Asset:
    """Represents a financial asset."""
    name: str
    value: float


@dataclass
class Liability:
    """Represents a financial liability."""
    name: str
    amount: float
