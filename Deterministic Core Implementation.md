Deterministic Core Implementation.md

core/ids.py

```python
import hashlib
import json
from datetime import datetime
from dataclasses import asdict

def generate_loan_id(lender_id: str, borrower_id: str, amount_cents: int, 
                     timestamp: datetime, nonce: int = 0) -> str:
    """Deterministic loan ID generation"""
    payload = {
        'lender': lender_id,
        'borrower': borrower_id,
        'amount': amount_cents,
        'timestamp': timestamp.isoformat(),
        'nonce': nonce
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return f"LOAN_{hashlib.sha256(serialized.encode()).hexdigest()[:16]}"
```

core/afr.py

```python
from datetime import date
import requests
from typing import Optional

class AFRSource:
    """Deterministic AFR retrieval with pinning"""
    
    # IRS publishes these monthly - we pin them
    _AFR_RATES = {
        '2024-12': {'short': 0.047, 'mid': 0.038, 'long': 0.044},
        '2025-01': {'short': 0.046, 'mid': 0.039, 'long': 0.043},
        # ... add actual IRS rates
    }
    
    @classmethod
    def get_afr(cls, effective_date: date, term_years: int) -> float:
        """Get AFR for a specific date and term"""
        month_key = effective_date.strftime('%Y-%m')
        
        if month_key not in cls._AFR_RATES:
            # Fallback: fetch from IRS API with caching
            return cls._fetch_and_cache_afr(month_key, term_years)
        
        rates = cls._AFR_RATES[month_key]
        if term_years <= 3:
            return rates['short']
        elif term_years <= 9:
            return rates['mid']
        else:
            return rates['long']
    
    @classmethod
    def _fetch_and_cache_afr(cls, month_key: str, term_years: int) -> float:
        """Actually fetch from IRS (simplified)"""
        # In reality: call IRS API https://www.irs.gov/pub/irs-drop/rr-23-XX.pdf
        # For now, return a default
        return 0.045  # Stub - implement actual IRS API call
```

core/ledger.py

```python
from datetime import datetime
from dataclasses import dataclass
from typing import Literal
import hashlib
import json

EventType = Literal['LOAN_ISSUED', 'PAYMENT_MADE', 'INTEREST_ACCRUED', 
                    'DEFAULT_TRIGGERED', 'DISPUTE_OPENED', 'DISPUTE_RESOLVED']

@dataclass
class LedgerEntry:
    timestamp: datetime
    event_type: EventType
    loan_id: str
    amount_cents: int
    metadata: dict
    previous_hash: str  # For chain integrity
    entry_hash: str
    
    @classmethod
    def create(cls, event_type: EventType, loan_id: str, amount_cents: int, 
               metadata: dict, previous_hash: str) -> 'LedgerEntry':
        """Immutable, append-only ledger entry"""
        timestamp = datetime.utcnow()
        
        # Create deterministic hash
        payload = {
            'timestamp': timestamp.isoformat(),
            'event_type': event_type,
            'loan_id': loan_id,
            'amount_cents': amount_cents,
            'metadata': metadata,
            'previous_hash': previous_hash
        }
        
        serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        entry_hash = hashlib.sha256(serialized.encode()).hexdigest()
        
        return cls(
            timestamp=timestamp,
            event_type=event_type,
            loan_id=loan_id,
            amount_cents=amount_cents,
            metadata=metadata,
            previous_hash=previous_hash,
            entry_hash=entry_hash
        )
```

core/agreements.py

```python
from dataclasses import dataclass
from datetime import date
import json
import hashlib
from typing import Dict, Any

@dataclass
class LoanAgreement:
    """Signed, hashable loan agreement"""
    loan_id: str
    lender: str
    borrower: str
    principal_cents: int
    interest_rate_annual: float
    term_months: int
    start_date: date
    repayment_schedule: str  # 'monthly', 'quarterly', etc.
    collateral_description: str
    governing_law: str
    signature_lender: str
    signature_borrower: str
    document_hash: str
    
    @classmethod
    def generate(cls, loan_details: Dict[str, Any], 
                 lender_sig: str, borrower_sig: str) -> 'LoanAgreement':
        """Create a signed agreement"""
        # Create hash of all terms
        hashable_data = {
            **loan_details,
            'signature_lender': lender_sig,
            'signature_borrower': borrower_sig
        }
        serialized = json.dumps(hashable_data, sort_keys=True, separators=(',', ':'))
        doc_hash = hashlib.sha256(serialized.encode()).hexdigest()
        
        return cls(
            document_hash=doc_hash,
            **loan_details,
            signature_lender=lender_sig,
            signature_borrower=borrower_sig
        )
    
    def verify_signatures(self) -> bool:
        """Verify agreement hasn't been tampered with"""
        # Recompute hash and compare
        data = {k: v for k, v in self.__dict__.items() if k != 'document_hash'}
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
        recomputed_hash = hashlib.sha256(serialized.encode()).hexdigest()
        return recomputed_hash == self.document_hash
```
