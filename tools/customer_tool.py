from data.customers import customers

def get_customer_profile(customer_id: str) -> dict:
    """
    Fetch basic customer profile details
    """
    return customers.get(customer_id)
