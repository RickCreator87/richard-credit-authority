# Pseudo-logic for your Validation Engine
if total_outstanding > total_authorized_cap:
    raise Exception("GOVERNANCE VIOATION: Lending Cap Exceeded")
if new_loan_amount > single_loan_max:
    raise Exception("GOVERNANCE VIOLATION: Single Loan Limit Exceeded")
