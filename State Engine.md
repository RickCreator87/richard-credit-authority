State Engine.md

engine/loan_state.py

```python
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional
from decimal import Decimal
import json

@dataclass
class LoanState:
    loan_id: str
    status: str  # 'ACTIVE', 'PAID', 'DEFAULT', 'DISPUTED'
    principal_remaining_cents: int
    interest_accrued_cents: int
    last_accrual_date: date
    payments: List[dict] = field(default_factory=list)
    ledger_hashes: List[str] = field(default_factory=list)
    
    def apply_payment(self, amount_cents: int, payment_date: date) -> dict:
        """Apply payment to loan state"""
        # Interest-first application
        interest_due = self.interest_accrued_cents
        principal_payment = max(0, amount_cents - interest_due)
        
        self.interest_accrued_cents = max(0, self.interest_accrued_cents - amount_cents)
        self.principal_remaining_cents -= principal_payment
        
        if self.principal_remaining_cents <= 0 and self.interest_accrued_cents <= 0:
            self.status = 'PAID'
        
        return {
            'date': payment_date.isoformat(),
            'amount_cents': amount_cents,
            'interest_paid': min(amount_cents, interest_due),
            'principal_paid': principal_payment,
            'principal_remaining': self.principal_remaining_cents
        }
    
    def accrue_interest(self, as_of_date: date, daily_rate: float) -> int:
        """Accrue interest deterministically"""
        days = (as_of_date - self.last_accrual_date).days
        if days <= 0:
            return 0
        
        # Simple interest accrual
        interest_cents = int(
            Decimal(self.principal_remaining_cents) * 
            Decimal(daily_rate) * 
            Decimal(days)
        )
        
        self.interest_accrued_cents += interest_cents
        self.last_accrual_date = as_of_date
        
        return interest_cents
```
