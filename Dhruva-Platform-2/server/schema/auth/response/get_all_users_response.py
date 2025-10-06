from pydantic import BaseModel, EmailStr
from uuid import UUID


class GetUsersResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
