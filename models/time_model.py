# models/time_model.py
from pydantic import BaseModel
from typing import Optional

class GetCurrentTimeInput(BaseModel):
    time_zone: Optional[str] = "UTC"
