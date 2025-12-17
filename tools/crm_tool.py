from data.crm import crm_kyc_records

def get_kyc_status(customer_id: str) -> dict:
    """
    Fetch KYC verification details from CRM
    """
    return crm_kyc_records.get(customer_id)

def is_kyc_verified(customer_id: str) -> bool:
    """
    Returns True if KYC is fully verified
    """
    record = get_kyc_status(customer_id)
    if not record:
        return False
    return record["kyc_status"] == "VERIFIED"
