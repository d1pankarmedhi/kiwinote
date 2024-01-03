from pydantic import BaseModel, Field, EmailStr

class Note(BaseModel):
    title: str
    body: str


class UserSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)



