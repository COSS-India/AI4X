import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from db.PostgreSQLBaseModel import PostgreSQLBaseModel


class Session(PostgreSQLBaseModel):
    user_id: UUID
    type: str
    timestamp: datetime.datetime
