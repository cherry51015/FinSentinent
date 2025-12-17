import streamlit as st

from agents.master_agent import master_agent_run
from data.customers import customers
from data.loan_requests import loan_requests
from utils.logger import init_logs, log

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Agentic AI – Tata Capital Personal Loan",
    layout="wide"
)

# -------------------------------
# Global UI Styling (BFSI Look)
# -------------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #0F2A44;
}
section[data-testid="stSidebar"] {
    background-color: #F5F7FA;
}
div[data-testid="stAlert"] {
    border-radius: 8px;
}
button[kind="primary"] {
    background-color: #0F2A44;
    color: white;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Init Agent Logs
# -------------------------------
init_logs()

# -------------------------------
# Loan Journey Steps
# -------------------------------
LOAN_STEPS = [
    "Conversation",
    "Sales Review",
    "KYC Check",
    "Underwriting",
    "Decision",
    "Sanction"
]

def show_progress(current_step: int):
    progress = int((current_step / (len(LOAN_STEPS) - 1)) * 100)
    st.progress(progress)

    cols = st.columns(len(LOAN_STEPS))
    for i, step in enumerate(LOAN_STEPS):
        if i <= current_step:
            cols[i].markdown(f"**✅ {step}**")
        else:
            cols[i].markdown(f"⬜ {step}")

# -------------------------------
# Header
# -------------------------------
st.title("Agentic AI Personal Loan Assistant")
st.caption("End-to-end AI-driven personal loan journey for Tata Capital")

# -------------------------------
# Sidebar – Customer Selection
# -------------------------------
st.sidebar.header("Customer Selection")

customer_id = st.sidebar.selectbox(
    "Select Customer ID",
    list(customers.keys())
)

customer = customers[customer_id]
loan_request = loan_requests[customer_id]

st.sidebar.subheader("Customer Profile")
st.sidebar.write(f"**Name:** {customer['name']}")
st.sidebar.write(f"**City:** {customer['city']}")
st.sidebar.write(f"**Employment:** {customer['employment_type']}")
st.sidebar.write(f"**Monthly Salary:** ₹{customer['monthly_salary']:,}")

st.sidebar.subheader("Requested Loan")
st.sidebar.write(f"**Amount:** ₹{loan_request['requested_amount']:,}")
st.sidebar.write(f"**Tenure:** {loan_request['requested_tenure_months']} months")
st.sidebar.write(f"**Purpose:** {loan_request['loan_purpose']}")

# -------------------------------
# Agent Logs Panel
# -------------------------------
st.sidebar.divider()
st.sidebar.subheader("🧠 Agent Activity Log")

for entry in st.session_state.agent_logs:
    st.sidebar.markdown(
        f"**[{entry['time']}] {entry['agent']}**  \n{entry['message']}"
    )

# -------------------------------
# Main Content
# -------------------------------
st.markdown("### Conversation")

st.markdown(
    f"""
    **Customer:**  
    I am looking for a personal loan of **₹{loan_request['requested_amount']:,}**
    for **{loan_request['requested_tenure_months']} months**.
    """
)

if st.button("Start Agentic Loan Journey", type="primary"):
    log("Master Agent", "Loan journey initiated")
    show_progress(0)

    with st.spinner("Master Agent orchestrating the loan journey..."):
        result = master_agent_run(customer_id)

    st.divider()

    # -------------------------------
    # Sales Agent
    # -------------------------------
    if result.get("sales_context"):
        show_progress(1)
        log("Sales Agent", "Prepared loan proposal and EMI estimate")

        st.markdown("### Sales Review")
        col1, col2 = st.columns([2, 1])

        with col1:
            st.info(result["sales_context"]["message"])

        with col2:
            st.markdown("**Offer Summary**")
            st.json(result["sales_context"]["proposed_offer"])

    # -------------------------------
    # Underwriting Agent
    # -------------------------------
    if result.get("underwriting_result"):
        show_progress(3)
        uw = result["underwriting_result"]
        log("Underwriting Agent", f"Decision computed: {uw['decision']}")

        st.markdown("### Underwriting")
        st.write(f"**Decision:** {uw['decision']}")
        st.write(f"**Reason:** {uw['reason']}")

        if uw.get("emi"):
            st.write(f"**Calculated EMI:** ₹{uw['emi']:,}")

    # -------------------------------
    # Reframing Agent
    # -------------------------------
    if result.get("reframing_result"):
        show_progress(4)
        reframing = result["reframing_result"]
        log("Offer Reframing Agent", "Generated recovery options")

        st.markdown("### Offer Reframing")
        st.warning(reframing["message"])

        for option in reframing["suggested_options"]:
            st.markdown("—")
            st.write(f"**Option:** {option['option']}")
            st.write(f"Amount: ₹{option['amount']:,}")
            st.write(f"Tenure: {option['tenure_months']} months")
            st.write(f"Estimated EMI: ₹{option['estimated_emi']:,}")

        st.divider()
        st.markdown("### Human Assistance")

        if st.button("Request Human Assistance", type="primary"):
            log("Sales Agent (Human Override)", "User requested human escalation")
            st.success(
                "A Tata Capital sales executive has been notified and will contact you shortly."
            )

    # -------------------------------
    # Sanction Letter
    # -------------------------------
    if result.get("sanction_letter"):
        show_progress(5)
        log("Sanction Letter Agent", "Sanction letter generated")

        st.markdown("### Sanction Letter")
        st.success(result["final_message"])

        with open(result["sanction_letter"], "rb") as file:
            st.download_button(
                label="Download Sanction Letter",
                data=file,
                file_name=result["sanction_letter"],
                mime="application/pdf"
            )

    # -------------------------------
    # Final Message (Non-Approval)
    # -------------------------------
    if result.get("final_message") and not result.get("sanction_letter"):
        st.markdown("### Final Message")
        st.info(result["final_message"])
