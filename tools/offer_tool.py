"""Loan offer utilities."""

from data.offers import offers


def get_preapproved_offer(customer_id: str) -> dict:
    """Return the pre-approved offer for a customer id, if any."""
    return offers.get(customer_id)


__all__ = ["get_preapproved_offer"]
