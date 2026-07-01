from datetime import datetime
from typing import Optional, Literal, List

from pydantic import BaseModel, EmailStr


class BaseErrorResponse(BaseModel):
    '''
    Base error response model.
    '''
    status: str
    message: str


class SubmitDataErrorResponse(BaseModel):
    '''
    Error response model for POST /submitData endpoint.
    '''
    status: str
    message: str
    id: None


class PatchPerevalErrorResponse(BaseModel):
    '''
    Error response model for PATCH /submitData/{id} endpoint.
    '''
    state: Literal[0]
    message: Optional[str]


class UserResponseModel(BaseModel):
    '''
    User data model for response.
    '''
    id: int
    email: EmailStr
    fam: str
    name: str
    otc: Optional[str]
    phone: str


class CoordsResponseModel(BaseModel):
    '''
    Coordinates model for response.
    '''
    id: int
    latitude: float
    longitude: float
    height: int


class LevelsResponseModel(BaseModel):
    '''
    Difficulty levels model for response.
    '''
    id: int
    winter: Optional[str]
    summer: Optional[str]
    autumn: Optional[str]
    spring: Optional[str]


class ImageResponseModel(BaseModel):
    '''
    Image model for response.
    '''
    id: int
    date_added: str
    data: str
    title: str
    pereval_id: int


class PerevalResponseModel(BaseModel):
    '''
    Complete pereval model for response.
    '''
    id: int
    beauty_title: str
    title: str
    other_titles: Optional[str]
    connect: Optional[str]
    status: str
    date_added: datetime
    add_time: datetime
    user: UserResponseModel
    coords : CoordsResponseModel
    levels: LevelsResponseModel
    images: List[ImageResponseModel]


class PatchPerevalResponseModel(BaseModel):
    '''
    Success response model for PATCH /submitData/{id} endpoint.
    '''
    state: Literal[1]
    message: None


class SubmitDataResponseModel(BaseModel):
    '''
    Success response model for POST /submitData endpoint.
    '''
    status: int
    message: Optional[str]
    id: Optional[int]
