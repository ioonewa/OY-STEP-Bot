from pydantic import BaseModel

from typing import Optional, List
from datetime import datetime

class Settings(BaseModel):
    telegram_id: int
    device: str
    notifications_enabled: bool
    updated_at: datetime