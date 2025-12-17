"""Sanction letter generation agent."""

import os
from datetime import datetime

from utils.logger import log


def generate_sanction_letter(
    customer_id: str,
    customer_name: str,
    approved_amount: float,
    tenure_months: int,
) -> str:
    """
    Create a simple sanction letter file and return its path.

    We use a plain-text payload with a .pdf extension for quick download.
    """
    folder = "sanction_letters"
    os.makedirs(folder, exist_ok=True)

    file_name = f"sanction_letter_{customer_id}.pdf"
    file_path = os.path.join(folder, file_name)

    issued_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = (
        "Tata Capital Personal Loan Sanction Letter\n"
        "-----------------------------------------\n"
        f"Customer ID : {customer_id}\n"
        f"Customer    : {customer_name}\n"
        f"Approved Amt: ₹{approved_amount:,}\n"
        f"Tenure      : {tenure_months} months\n"
        f"Issued On   : {issued_on}\n"
        "\n"
        "Congratulations! Your personal loan has been approved subject to "
        "standard terms and conditions.\n"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    log("Sanction Agent", f"Generated sanction letter at {file_path}")
    return file_path


__all__ = ["generate_sanction_letter"]
