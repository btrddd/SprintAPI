from fastapi import (
    FastAPI, status, Request, HTTPException, Path
)
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
import re

from db.db_worker import DatabaseWorker


class SubmitDataErrorResponse(BaseModel):
    status: str
    message: str 
    id: None


class GetPerevalErrorResponse(BaseModel):
    status: str
    message: str


class UserRequestModel(BaseModel):
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


class UserResponseModel(BaseModel):
    id: int
    email: str
    fam: str
    name: str
    otc: Optional[str]
    phone: str


class CoordsRequestModel(BaseModel):
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
    

class CoordsResponseModel(BaseModel):
    id: int
    latitude: float
    longitude: float
    height: int


class LevelsRequestModel(BaseModel):
    winter: Optional[str]
    summer: Optional[str]
    autumn: Optional[str]
    spring: Optional[str]


class LevelsResponseModel(BaseModel):
    id: int
    winter: Optional[str]
    summer: Optional[str]
    autumn: Optional[str]
    spring: Optional[str]


class ImageRequestModel(BaseModel):
    data: str
    title: str


class ImageResponseModel(BaseModel):
    id: int
    date_added: str
    data: str
    title: str
    pereval_id: int


class PerevalRequestModel(BaseModel):
    beauty_title: str
    title: str
    other_titles: Optional[str]
    connect: Optional[str]
    add_time: str
    user: UserRequestModel
    coords: CoordsRequestModel
    level: LevelsRequestModel
    images: list[ImageRequestModel]

    @field_validator('add_time')
    @classmethod
    def validate_date_time(cls, date_time):
        try:
            datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError('Incorrect "add_time" value')
        return date_time         


class PerevalResponseModel(BaseModel):
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


class PatchPerevalRequestModel(BaseModel):
    id: int
    beauty_title: Optional[str]
    title: Optional[str]
    other_titles: Optional[str]
    connect: Optional[str]
    coords: Optional[CoordsRequestModel]
    level: Optional[LevelsRequestModel]
    images: Optional[List[ImageRequestModel]]


class PatchPerevalResponseModel(BaseModel):
    state: int
    message: Optional[str]


class SubmitDataResponseModel(BaseModel):
    status: int
    message: Optional[str]
    id: Optional[int]


app = FastAPI(
    title='Pereval API',
    description='SkillFactory API project',
    version='1.0.0'
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    path = request.url.path
    error = exc.errors()[0]

    if path == '/submitData':
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                'status': status.HTTP_422_UNPROCESSABLE_CONTENT,
                'message': f'Error: {error["msg"]}; loc: {error["loc"]}',
                'id': None
            }
        )
    elif path.startswith('/submitData/'):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                'status': status.HTTP_422_UNPROCESSABLE_CONTENT,
                'message': f'Error: {error["msg"]}',
            }
        )


@app.post(
    path='/submitData', 
    response_model=SubmitDataResponseModel,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            'model': SubmitDataErrorResponse,
            'description': 'ValidationError'
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': SubmitDataErrorResponse,
            'description': 'Internal server error'
        }
    }
)
async def submit_data(
    request: PerevalRequestModel
) -> SubmitDataResponseModel:
    request_dict = request.model_dump()
    
    try:
        db_worker = DatabaseWorker()
        db_worker.connect()
        pereval_id = db_worker.add_pereval(request_dict)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': ex,
                'id': None
            }
        )
    finally:
        db_worker.disconnect()
    
    if not pereval_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Error saving to database',
                'id': None
            }
        )
    
    return SubmitDataResponseModel(
        status=status.HTTP_200_OK,
        message=None,
        id=pereval_id
    )


@app.get(
    path='/submitData/{id}', 
    response_model=PerevalResponseModel,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            'model': GetPerevalErrorResponse,
            'description': 'ValidationError'
        },
        status.HTTP_404_NOT_FOUND: {
            'model': GetPerevalErrorResponse,
            'description': 'Not found'
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': GetPerevalErrorResponse,
            'description': 'Internal server error'
        }
    }
)
async def get_pereval_by_id(id: int = Path(
        description='Unique database pereval id',
        ge=1
    )
):
    try:
        db_worker = DatabaseWorker()
        db_worker.connect()
        pereval_data = db_worker.get_pereval_by_id(id)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': ex
            }
        )
    finally:
        db_worker.disconnect()
        
    if pereval_data:
        return PerevalResponseModel(**pereval_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'status': status.HTTP_404_NOT_FOUND,
                'message': f'Object with id = {id} not found'
            }
        )