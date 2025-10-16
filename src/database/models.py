"""Database models and schemas."""

from dataclasses import dataclass


@dataclass
class Asset:
    """Represents a financial asset with name and value."""

    name: str
    value: float


@dataclass
class Liability:
    """Represents a financial liability with name and amount owed."""

    name: str
    amount: float


@dataclass
class MonthlyFlow:
    """Represents a monthly cash flow item (income or expense)."""

    name: str
    amount: float
