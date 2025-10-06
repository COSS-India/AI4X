from db.PostgreSQLBaseModel import PostgreSQLBaseModel
from pydantic import EmailStr
from schema.auth.common import RoleType


class User(PostgreSQLBaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleType
