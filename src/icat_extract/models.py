from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class InvestigationQueryParams:
    start_date: Optional[datetime]
    instruments: list[str]
    facility: Optional[str] = None
    include_fields: list[str] | None = None
    rb_number: Optional[str] = None
