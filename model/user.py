from pydantic import BaseModel

class User(BaseModel):
    username: str 
    fullname: str | None = None
    email: str | None = None
    disabled: bool | None = None