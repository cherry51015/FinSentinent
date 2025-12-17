from data.credit_bureau import credit_bureau_records

def fetch_credit_score(customer_id: str) -> int:
    """
    Fetch credit score from mock credit bureau
    """
    record = credit_bureau_records.get(customer_id)
    if not record:
        return 0
    return record["credit_score"]

def fetch_risk_band(customer_id: str) -> str:
    """
    Fetch risk band (LOW / MEDIUM / HIGH)
    """
    record = credit_bureau_records.get(customer_id)
    if not record:
        return "UNKNOWN"
    return record["risk_band"]
