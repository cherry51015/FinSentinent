from tools.customer_tool import get_customer_profile
from tools.offer_tool import get_preapproved_offer
from tools.loan_request_tool import get_loan_request
from utils.emi_calculator import calculate_emi


def sales_engagement(customer_id: str) -> dict:
    """
    Handles loan discovery, initial persuasion, and offer explanation.
    Returns a structured sales context for Master Agent.
    """

    sales_payload = {
        "customer_id": customer_id,
        "proceed": True,
        "message": None,
        "proposed_offer": None
    }

    # 1️⃣ Fetch customer & request details
    customer = get_customer_profile(customer_id)
    loan_request = get_loan_request(customer_id)
    offer = get_preapproved_offer(customer_id)

    requested_amount = loan_request["requested_amount"]
    tenure = loan_request["requested_tenure_months"]

    # 2️⃣ EMI calculation for transparency
    estimated_emi = calculate_emi(
        requested_amount,
        offer["interest_rate"],
        tenure
    )

    # 3️⃣ Prepare sales explanation
    sales_payload["message"] = (
        f"Based on your profile, you are eligible to explore a personal loan of "
        f"₹{requested_amount:,} for {tenure} months at an interest rate of "
        f"{offer['interest_rate']}%. Your estimated EMI would be approximately "
        f"₹{estimated_emi:,} per month."
    )

    # 4️⃣ Attach offer details
    sales_payload["proposed_offer"] = {
        "requested_amount": requested_amount,
        "tenure_months": tenure,
        "interest_rate": offer["interest_rate"],
        "estimated_emi": estimated_emi,
        "pre_approved_limit": offer["pre_approved_limit"],
        "offer_type": offer["offer_type"]
    }

    # 5️⃣ Soft persuasion logic (enterprise-safe)
    if requested_amount > offer["pre_approved_limit"]:
        sales_payload["message"] += (
            " This amount is higher than your pre-approved limit, "
            "but we can still evaluate it further with a few additional checks."
        )

    return sales_payload
