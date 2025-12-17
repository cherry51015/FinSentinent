from utils.logger import log
from tools.credit_tool import fetch_credit_score, fetch_risk_band
from tools.offer_tool import get_preapproved_offer
from tools.salary_slip_tool import get_salary_slip, is_salary_eligible
from tools.customer_tool import get_customer_profile
from tools.loan_request_tool import get_loan_request
from utils.emi_calculator import calculate_emi


def underwriting_decision(customer_id: str) -> dict:
    """
    Core underwriting decision logic.
    Returns a structured decision object for explainability.
    """

    decision_payload = {
        "customer_id": customer_id,
        "decision": None,
        "reason": None,
        "next_action": None,
        "emi": None
    }

    # 1️⃣ Fetch required data via tools
    customer = get_customer_profile(customer_id)
    offer = get_preapproved_offer(customer_id)
    loan_request = get_loan_request(customer_id)
    credit_score = fetch_credit_score(customer_id)

    requested_amount = loan_request["requested_amount"]
    tenure = loan_request["requested_tenure_months"]
    salary = customer["monthly_salary"]
    log("Underwriting Agent", f"Fetched credit score: {credit_score}")

    # 2️⃣ Credit score check
    if credit_score < 700:
        decision_payload.update({
            "decision": "REJECTED",
            "reason": "Credit score below acceptable threshold",
            "next_action": "EXIT"
        })
        log("Underwriting Agent", f"Rejected due to low credit score: {credit_score}")
        return decision_payload

    # 3️⃣ Pre-approved limit check
    pre_approved_limit = offer["pre_approved_limit"]

    # Case A: Instant approval
    if requested_amount <= pre_approved_limit:
        emi = calculate_emi(
            requested_amount,
            offer["interest_rate"],
            tenure
        )
        log("Underwriting Agent", f"Calculated EMI: {emi}")
        decision_payload.update({
            "decision": "APPROVED",
            "reason": "Requested amount within pre-approved limit",
            "emi": emi,
            "next_action": "GENERATE_SANCTION_LETTER"
        })
        log("Underwriting Agent", f"Approved due to requested amount within pre-approved limit: {requested_amount}")
        return decision_payload

    # Case B: Salary slip required (≤ 2x pre-approved limit)
    if requested_amount <= 2 * pre_approved_limit:
        salary_slip = get_salary_slip(customer_id)

        if not salary_slip:
            decision_payload.update({
                "decision": "PENDING",
                "reason": "Salary slip required for further evaluation",
                "next_action": "REQUEST_SALARY_SLIP"
            })
            log("Underwriting Agent", f"Rejected due to salary slip not found: {customer_id}")
            return decision_payload

        emi = calculate_emi(
            requested_amount,
            offer["interest_rate"],
            tenure
        )

        if is_salary_eligible(customer_id) and emi <= 0.5 * salary:
            decision_payload.update({
                "decision": "APPROVED",
                "reason": "Salary eligibility satisfied after EMI check",
                "emi": emi,
                "next_action": "GENERATE_SANCTION_LETTER"
            })
            log("Underwriting Agent", f"Approved due to salary eligibility and EMI check: {emi}")
            return decision_payload

        decision_payload.update({
            "decision": "REJECTED",
            "reason": "EMI exceeds 50% of monthly salary",
            "emi": emi,
            "next_action": "OFFER_REFRAMING"
        })
        log("Underwriting Agent", f"Rejected due to EMI exceeding 50% of monthly salary: {emi}")
        return decision_payload

    # Case C: Amount exceeds policy
    decision_payload.update({
        "decision": "REJECTED",
        "reason": "Requested amount exceeds 2x pre-approved limit",
        "next_action": "OFFER_REFRAMING"
    })
    log("Underwriting Agent", f"Rejected due to requested amount exceeding 2x pre-approved limit: {requested_amount}")
    return decision_payload
