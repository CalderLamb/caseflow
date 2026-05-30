import uuid
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class MatterOut(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    status: str
    court: Optional[str]
    case_number: Optional[str]
    opened_date: Optional[date]
    sol_date: Optional[date]
    drive_folder_id: Optional[str]
    client_name: str
    open_item_count: int
    total_token_cost: int

    model_config = {"from_attributes": True}


class MatterDetail(MatterOut):
    items: list
    deadlines: list
    documents: list
    chronology: list
    facts: list
    cost_by_month: list
