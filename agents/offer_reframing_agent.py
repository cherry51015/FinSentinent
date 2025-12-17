from tools.offer_tool import get_preapproved_offer
from utils.logger import log
from tools.customer_tool import get_customer_profile
from utils.emi_calculator import calculate_emi


def offer_reframing_decision(customer_id: str, rejection_reason: str) -> dict:
    """
    Attempts to recover a rejected loan by intelligently reframing the offer
    based on the user's dissatisfaction reason.
    """

    reframing_payload = {
        "customer_id": customer_id,
        "reframed": False,
        "reason": rejection_reason,
        "suggested_options": [],
        "message": None,
        "escalation_available": True
    }

    customer = get_customer_profile(customer_id)
    offer = get_preapproved_offer(customer_id)
    salary = customer["monthly_salary"]

    pre_limit = offer["pre_approved_limit"]
    interest_rate = offer["interest_rate"]

    # 🔹 Case 1: EMI too high
    if rejection_reason == "EMI exceeds 50% of monthly salary":
        # Option 1: Reduce amount
        reduced_amount = int(pre_limit * 1.2)
        reduced_emi = calculate_emi(
            reduced_amount,
            interest_rate,
            offer["max_tenure_months"]
        )

        # Option 2: Increase tenure
        extended_tenure = offer["max_tenure_months"] + 12
        extended_emi = calculate_emi(
            pre_limit,
            interest_rate,
            extended_tenure
        )

        reframing_payload["suggested_options"] = [
            {
                "option": "Reduce Loan Amount",
                "amount": reduced_amount,
                "tenure_months": offer["max_tenure_months"],
                "estimated_emi": reduced_emi
            },
            {
                "option": "Extend Tenure",
                "amount": pre_limit,
                "tenure_months": extended_tenure,
                "estimated_emi": extended_emi
            }
        ]

        reframing_payload["message"] = (
            "Your EMI was higher than recommended for your income. "
            "Here are safer alternatives that may work better for you."
        )
        reframing_payload["reframed"] = True
        return reframing_payload

    # 🔹 Case 2: Requested amount exceeds policy
    if rejection_reason == "Requested amount exceeds 2x pre-approved limit":
        safe_amount = pre_limit
        safe_emi = calculate_emi(
            safe_amount,
            interest_rate,
            offer["max_tenure_months"]
        )

        reframing_payload["suggested_options"] = [
            {
                "option": "Apply for Safe Amount",
                "amount": safe_amount,
                "tenure_months": offer["max_tenure_months"],
                "estimated_emi": safe_emi
            }
        ]

        reframing_payload["message"] = (
            "The requested amount is beyond our policy limits. "
            "You can proceed with a safe pre-approved amount now and "
            "be eligible for a top-up later."
        )
        reframing_payload["reframed"] = True
        return reframing_payload

    # 🔹 Case 3: Low credit score (non-recoverable)
    if rejection_reason == "Credit score below acceptable threshold":
        reframing_payload["message"] = (
            "Your current credit score does not meet our eligibility criteria. "
            "You may improve your score and reapply in the future."
        )
        reframing_payload["reframed"] = False
        reframing_payload["escalation_available"] = True
        return reframing_payload

    # 🔹 Default fallback
    reframing_payload["message"] = (
        "We could not find an alternative plan automatically. "
        "You may choose to speak with a Tata Capital representative."
    )
    log("Offer Reframing Agent", f"Default fallback: {rejection_reason}")
    return reframing_payload
