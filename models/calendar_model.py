# models/calendar_model.py
from pydantic import BaseModel, Field, validator
from datetime import datetime

class CreateEventInput(BaseModel):
    topic: str
    start_time: datetime
    end_time: datetime

    @validator("end_time")
    def ensure_end_after_start(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v
