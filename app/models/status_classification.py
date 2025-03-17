from pydantic import BaseModel, conlist
from typing import List, Dict, Optional


class StatusClassificationRequest(BaseModel):
    statuses: conlist(str, min_length=1, max_length=100)
    llm: Optional[str] = "gpt"


class StatusClassificationResponse(BaseModel):
    status_name: str
    status_type: str
    substatus_type: Optional[str] = None


class StatusClassificationAPIResponse(BaseModel):
    classified_statuses: List[StatusClassificationResponse]
    tokens_used: Dict[str, int]
