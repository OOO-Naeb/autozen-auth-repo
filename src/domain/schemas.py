from typing import Optional

from pydantic import BaseModel, EmailStr, model_validator


class AccessToken(BaseModel):
    access_token: str


class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(AccessToken, RefreshToken):
    pass


class UserFromDB(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    phone_number: str
    role: str


class UserToDB(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    phone_number: str
    password: str
    role: str

class RegisterRequestForm(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    phone_number: str
    password: str
    role: str

class LoginRequestForm(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: str = ...

    @model_validator(mode='before')
    @classmethod
    def check_is_email_or_phone_number_given(cls, values) -> dict:
        """
        Checks that at least one of the identifiers is provided for authorization: email or phone number BEFORE the serialization.
        This method is a '@model_validator' from Pydantic V2.

        Args:
            values (dict): A dictionary containing the raw data from the query. This field is being automatically filled by Pydantic upon HTTP request.
        Returns:
            values (dict): A dictionary of validated data, ready to be used to create a model object.
        Raises:
            ValueError: If the email and phone number both are not provided.
        """
        email = values.get('email')
        phone_number = values.get('phone_number')

        if not email and not phone_number:
            raise ValueError('Either email or phone number must be provided.')

        return values
