import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from bson import ObjectId

from db.MongoBaseModel import MongoBaseModel


class Session(MongoBaseModel):
    user_id: UUID
    type: str
    timestamp: datetime.datetime
