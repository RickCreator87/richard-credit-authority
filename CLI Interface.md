CLI Interface.md

cli/main.py

```python
import click
from datetime import datetime, date
import json
from pathlib import Path

@click.group()
def cli():
    """Richards Credit Authority CLI"""
    pass

@cli.command()
@click.option('--lender', required=True)
@click.option('--borrower', required=True)
@click.option('--amount', type=int, required=True)
@click.option('--term-months', type=int, required=True)
def issue_loan(lender, borrower, amount, term_months):
    """Issue a new loan"""
    from core.ids import generate_loan_id
    from core.afr import AFRSource
    from core.agreements import LoanAgreement
    
    loan_id = generate_loan_id(
        lender_id=lender,
        borrower_id=borrower,
        amount_cents=amount * 100,
        timestamp=datetime.utcnow()
    )
    
    # Get appropriate AFR
    interest_rate = AFRSource.get_afr(date.today(), term_months // 12)
    
    agreement = LoanAgreement.generate(
        loan_details={
            'loan_id': loan_id,
            'lender': lender,
            'borrower': borrower,
            'principal_cents': amount * 100,
            'interest_rate_annual': interest_rate,
            'term_months': term_months,
            'start_date': date.today().isoformat(),
            'repayment_schedule': 'monthly',
            'collateral_description': 'Promissory note',
            'governing_law': 'Delaware, USA'
        },
        lender_sig=f"LENDER_SIG_{lender}",
        borrower_sig=f"BORROWER_SIG_{borrower}"
    )
    
    # Save to file
    output_path = Path(f"loans/{loan_id}.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(agreement.__dict__, f, indent=2, default=str)
    
    click.echo(f"Loan {loan_id} issued")
    click.echo(f"Document hash: {agreement.document_hash}")

@cli.command()
@click.option('--loan-id', required=True)
@click.option('--amount', type=float, required=True)
def record_payment(loan_id, amount):
    """Record a loan payment"""
    from engine.loan_state import LoanState
    from core.ledger import LedgerEntry
    
    # Load loan state
    state_path = Path(f"state/{loan_id}.json")
    if not state_path.exists():
        click.echo(f"Loan {loan_id} not found")
        return
    
    with open(state_path, 'r') as f:
        state_data = json.load(f)
    
    state = LoanState(**state_data)
    
    # Apply payment
    payment_result = state.apply_payment(
        amount_cents=int(amount * 100),
        payment_date=date.today()
    )
    
    # Create ledger entry
    previous_hash = state.ledger_hashes[-1] if state.ledger_hashes else "GENESIS"
    entry = LedgerEntry.create(
        event_type='PAYMENT_MADE',
        loan_id=loan_id,
        amount_cents=int(amount * 100),
        metadata=payment_result,
        previous_hash=previous_hash
    )
    
    # Update state
    state.ledger_hashes.append(entry.entry_hash)
    
    # Save
    with open(state_path, 'w') as f:
        json.dump(state.__dict__, f, indent=2, default=str)
    
    click.echo(f"Payment recorded: {payment_result}")

if __name__ == '__main__':
    cli()
```
