"""Simple EMI calculator utility."""

import math


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> int:
    """
    Compute the monthly EMI using the standard reducing balance formula.

    EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    where:
      P = principal
      r = monthly interest rate (annual_rate / 12 / 100)
      n = tenure in months
    """
    if tenure_months <= 0:
        raise ValueError("tenure_months must be positive")

    monthly_rate = annual_rate / 12 / 100

    if monthly_rate == 0:
        return math.ceil(principal / tenure_months)

    factor = (1 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * factor / (factor - 1)
    return math.ceil(emi)


__all__ = ["calculate_emi"]

