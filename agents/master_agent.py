from agents.sales_agent import sales_engagement
from agents.underwriting_agent import underwriting_decision
from agents.offer_reframing_agent import offer_reframing_decision
from agents.sanction_agent import generate_sanction_letter
from tools.crm_tool import is_kyc_verified
from tools.customer_tool import get_customer_profile
from tools.loan_request_tool import get_loan_request


def master_agent_run(customer_id: str) -> dict:
    """
    Master Agent orchestrates the entire loan journey
    from conversation to sanction letter.
    """

    orchestration_trace = {
        "customer_id": customer_id,
        "status": None,
        "sales_context": None,
        "underwriting_result": None,
        "reframing_result": None,
        "sanction_letter": None,
        "final_message": None
    }

    # 1️⃣ Load customer context
    customer = get_customer_profile(customer_id)
    loan_request = get_loan_request(customer_id)

    # 2️⃣ KYC Verification
    if not is_kyc_verified(customer_id):
        orchestration_trace.update({
            "status": "KYC_INCOMPLETE",
            "final_message": (
                "Your KYC details are incomplete. "
                "Please update your address details to proceed."
            )
        })
        return orchestration_trace

    # 3️⃣ Sales Engagement
    sales_context = sales_engagement(customer_id)
    orchestration_trace["sales_context"] = sales_context

    # 4️⃣ Underwriting Decision
    underwriting_result = underwriting_decision(customer_id)
    orchestration_trace["underwriting_result"] = underwriting_result

    # 5️⃣ Decision Routing
    decision = underwriting_result["decision"]

    # ✅ Case A: Approved
    if decision == "APPROVED":
        sanction_file = generate_sanction_letter(
            customer_id=customer_id,
            customer_name=customer["name"],
            approved_amount=loan_request["requested_amount"],
            tenure_months=loan_request["requested_tenure_months"]
        )

        orchestration_trace.update({
            "status": "APPROVED",
            "sanction_letter": sanction_file,
            "final_message": (
                "Congratulations! Your personal loan has been approved. "
                "Please find your sanction letter attached."
            )
        })
        return orchestration_trace

    # ⏳ Case B: Salary Slip Required
    if decision == "PENDING":
        orchestration_trace.update({
            "status": "SALARY_SLIP_REQUIRED",
            "final_message": (
                "To proceed further, please upload your latest salary slip "
                "for eligibility verification."
            )
        })
        return orchestration_trace

    # ❌ Case C: Rejected → Reframing
    if decision == "REJECTED":
        reframing = offer_reframing_decision(
            customer_id,
            underwriting_result["reason"]
        )

        orchestration_trace.update({
            "status": "REFRAMING_INITIATED",
            "reframing_result": reframing,
            "final_message": reframing["message"]
        })
        return orchestration_trace

    # 🛑 Fallback
    orchestration_trace.update({
        "status": "EXIT",
        "final_message": (
            "Thank you for your interest. "
            "Please reach out to Tata Capital support for further assistance."
        )
    })
    return orchestration_trace
