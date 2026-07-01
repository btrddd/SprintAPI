import re
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class UserRequestModel(BaseModel):
    '''
    User data model for request validation.
    '''
    email: EmailStr
    fam: str
    name: str
    otc: Optional[str] = None
    phone: str

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, phone: str) -> str:
        '''
        Validate phone number format.

        Args:
            phone: Phone number string.

        Returns:
            str: The validated phone number.

        Raises:
            ValueError: If phone format is invalid.
        '''
        if bool(re.match(r'^\+?[0-9\s\-\(\)]{10,20}$', phone)):
            return phone
        raise ValueError('Incorrect "phone" value')


class CoordsRequestModel(BaseModel):
    '''
    Coordinates model for request validation.
    '''
    latitude: str
    longitude: str
    height: str

    @field_validator('latitude', 'longitude', 'height')
    @classmethod
    def validate_coords(cls, coord: str) -> str:
        '''
        Validate coordinate values.

        Args:
            coord: Coordinate value as string.

        Returns:
            str: The validated coordinate.

        Raises:
            ValueError: If coordinate cannot be converted to float.
        '''
        try:
            float(coord)
        except ValueError:
            raise ValueError(f'Incorrect coordinate value')
        return coord


class CoordsPatchRequestModel(BaseModel):
    '''
    Coordinates model for PATCH request validation.
    All fields are optional to allow partial updates.
    '''
    latitude: str = None
    longitude: str = None
    height: str = None


class LevelsRequestModel(BaseModel):
    '''
    Difficulty levels model for request validation.
    '''
    winter: Optional[str] = None
    summer: Optional[str] = None
    autumn: Optional[str] = None
    spring: Optional[str] = None


class LevelsPatchRequestModel(BaseModel):
    '''
    Difficulty levels model for PATCH request validation.
    All fields are optional to allow partial updates.
    '''
    winter: Optional[str] = None
    summer: Optional[str] = None
    autumn: Optional[str] = None
    spring: Optional[str] = None


class ImageRequestModel(BaseModel):
    '''
    Image data model for request validation.
    '''
    data: str
    title: str


class PerevalRequestModel(BaseModel):
    '''
    Complete pereval data model for POST request validation.
    '''
    beauty_title: str
    title: str
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    add_time: str
    user: UserRequestModel
    coords: CoordsRequestModel
    level: LevelsRequestModel
    images: list[ImageRequestModel]

    @field_validator('add_time')
    @classmethod
    def validate_date_time(cls, date_time: str) -> str:
        '''
        Validate datetime string format.

        Args:
            date_time: Datetime string in format "%Y-%m-%d %H:%M:%S".

        Returns:
            str: The validated datetime string.

        Raises:
            ValueError: If datetime format is invalid.
        '''
        try:
            datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError('Incorrect "add_time" value')
        return date_time


class PatchPerevalRequestModel(BaseModel):
    '''
    Partial update model for PATCH request validation.
    All fields are optional to allow partial updates.
    '''
    beauty_title: Optional[str] = None
    title: Optional[str] = None
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    coords: Optional[CoordsPatchRequestModel] = None
    levels: Optional[LevelsPatchRequestModel] = None
    images: Optional[List[ImageRequestModel]] = None
