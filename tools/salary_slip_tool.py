"""Salary slip helpers."""

from data.salary_slips import salary_slips


def get_salary_slip(customer_id: str) -> dict:
    """Return the salary slip record for the customer id, if any."""
    return salary_slips.get(customer_id)


def is_salary_eligible(customer_id: str) -> bool:
    """Return True if salary slip marks EMI eligibility within threshold."""
    slip = get_salary_slip(customer_id)
    if not slip:
        return False
    return slip["emi_eligibility"]


__all__ = ["get_salary_slip", "is_salary_eligible"]
