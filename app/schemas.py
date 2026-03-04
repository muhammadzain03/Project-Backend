# API request/response models

from pydantic import BaseModel


class UserSignup(BaseModel):
    username: str
    email: str
    password: str
    pictureURL: str
    userDescriptionURL: str


class UserLogin(BaseModel):
    username: str
    password: str