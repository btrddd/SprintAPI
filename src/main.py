from fastapi import FastAPI, status, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re

from db.db_worker import DatabaseWorker


class UserModel(BaseModel):
    email: EmailStr
    fam: str
    name: str
    otc: Optional[str]
    phone: str

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, phone):
        if bool(re.match(r'^\+?[0-9\s\-\(\)]{10,20}$', phone)):
            return phone
        raise ValueError('Incorrect "phone" value')
    

class CoordsModel(BaseModel):
    latitude: str
    longitude: str
    height: str

    @field_validator('latitude', 'longitude', 'height')
    @classmethod
    def validate_coords(cls, coord):
        try:
            float(coord)
        except ValueError:
            raise ValueError(f'Incorrect coordinate value')
        return coord


class LevelModel(BaseModel):
    winter: Optional[str]
    summer: Optional[str]
    autumn: Optional[str]
    spring: Optional[str]


class ImageModel(BaseModel):
    data: str
    title: str


class SubmitDataRequest(BaseModel):
    beauty_title: str
    title: str
    other_titles: Optional[str]
    connect: Optional[str]
    add_time: str
    user: UserModel
    coords: CoordsModel
    level: LevelModel
    images: list[ImageModel]

    @field_validator('add_time')
    @classmethod
    def validate_date_time(cls, date_time):
        try:
            datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError('Incorrect "add_time" value')
        return date_time         


class SubmitDataResponse(BaseModel):
    status: int
    message: Optional[str]
    id: Optional[int]


app = FastAPI(
    title='Pereval API',
    description='SkillFactory API project',
    version='1.0.0'
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'status': exc.status_code,
            'message': exc.detail,
            'id': None
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    error = exc.errors()[0]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'status': status.HTTP_400_BAD_REQUEST,
            'message': f'Error: {error["msg"]}; loc: {error["loc"]}',
            'id': None
        }
    )


@app.post('/submit', response_model=SubmitDataResponse)
async def submitData(request: SubmitDataRequest) -> SubmitDataResponse:
    request_dict = request.model_dump()
    
    try:
        db_worker = DatabaseWorker()
        db_worker.connect()
        pereval_id = db_worker.add_pereval(request_dict)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ex
        )
    finally:
        db_worker.disconnect()
    
    if not pereval_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error saving to database'
        )
    
    return SubmitDataResponse(
        status=status.HTTP_200_OK,
        message=None,
        id=pereval_id
    )