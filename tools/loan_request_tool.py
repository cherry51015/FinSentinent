"""Loan request helpers."""

from data.loan_requests import loan_requests


def get_loan_request(customer_id: str) -> dict:
    """Return the loan request for a given customer id, if any."""
    return loan_requests.get(customer_id)


__all__ = ["get_loan_request"]
