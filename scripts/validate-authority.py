import yaml
import os

def validate_lending():
    # 1. Load your Authority Limits
    profile_path = 'authority/loaner-profile.yaml'
    ledger_path = 'authority/ledgers/richard-loaner-ledger.yaml'

    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f)
    
    with open(ledger_path, 'r') as f:
        ledger = yaml.safe_load(f)

    # 2. Extract Perimeters
    total_cap = profile['loaner_profile']['lending_capacity']['max_outstanding_principal']
    single_max = profile['loaner_profile']['lending_capacity']['max_single_loan_amount']
    
    current_total = 0
    
    print(f"--- GitDigital Authority Validation ---")
    
    # 3. Check each active loan
    for loan in ledger['active_loans']:
        amount = loan['principal']
        current_total += amount
        
        # Check Single Loan Cap
        if amount > single_max:
            print(f"❌ ERROR: Loan {loan['loan_id']} exceeds single loan cap of ${single_max}")
            return False
            
    # 4. Check Total Capacity
    if current_total > total_cap:
        print(f"❌ ERROR: Total outstanding (${current_total}) exceeds total cap of ${total_cap}")
        return False

    print(f"✅ VALID: Current utilization ${current_total} / ${total_cap}")
    print(f"✅ Remaining Capacity: ${total_cap - current_total}")
    return True

if __name__ == "__main__":
    if validate_lending():
        exit(0)
    else:
        exit(1)
