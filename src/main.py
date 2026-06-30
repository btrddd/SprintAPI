from fastapi import (
    FastAPI, status, Request, HTTPException, 
    Path, Query
)
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Literal
from datetime import datetime
import re

from db.db_worker import DatabaseWorker


class BaseErrorResponse(BaseModel):
    status: str
    message: str


class SubmitDataErrorResponse(BaseModel):
    status: str
    message: str
    id: None


class PatchPerevalErrorResponse(BaseModel):
    state: Literal[0]
    message: Optional[str]


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
    email: EmailStr
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
    

class CoordsPatchRequestModel(BaseModel):
    latitude: str = None
    longitude: str = None
    height: str = None


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


class LevelsPatchRequestModel(BaseModel):
    winter: Optional[str] = None
    summer: Optional[str] = None
    autumn: Optional[str] = None
    spring: Optional[str] = None


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
    beauty_title: Optional[str] = None
    title: Optional[str] = None
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    coords: Optional[CoordsPatchRequestModel] = None
    levels: Optional[LevelsPatchRequestModel] = None
    images: Optional[List[ImageRequestModel]] = None


class PatchPerevalResponseModel(BaseModel):
    state: Literal[1]
    message: None


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
    method = request.method
    error = exc.errors()[0]

    if path == '/submitData' and method == 'POST':
        response_content={
            'status': status.HTTP_422_UNPROCESSABLE_CONTENT,
            'message': f'Error: {error["msg"]}; loc: {error["loc"]}',
            'id': None
        }
    elif method == 'PATCH':
        response_content = {
            'state': 0,
            'message': f'Error: {error["msg"]}; loc: {error["loc"]}'
        }
    else:
        response_content={
            'status': status.HTTP_422_UNPROCESSABLE_CONTENT,
            'message': f'Error: {error["msg"]}',
        }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response_content
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
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
            'model': BaseErrorResponse,
            'description': 'Validation error'
        },
        status.HTTP_404_NOT_FOUND: {
            'model': BaseErrorResponse,
            'description': 'Not found'
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': BaseErrorResponse,
            'description': 'Internal server error'
        }
    }
)
async def get_pereval_by_id(
    id: int = Path(
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
    

@app.patch(
    path='/submitData/{id}',
    response_model=PatchPerevalResponseModel,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            'model': PatchPerevalErrorResponse,
            'description': 'Validation error'
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': PatchPerevalErrorResponse,
            'description': 'Internal server error'
        }
    }
)
async def patch_pereval(
    request: PatchPerevalRequestModel,
    id: int = Path(
        description='Unique database pereval id',
        ge=1
    )
):
    request_dict = request.model_dump(exclude_unset=True)

    try:
        db_worker = DatabaseWorker()
        db_worker.connect()
        state, message = db_worker.update_pereval(id, request_dict)

        if state == 1:
            return PatchPerevalResponseModel(
                state=1,
                message=message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    'state': 0,
                    'message': message
                }
            )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                'state': 0,
                'message': str(ex)
            }
        )
    finally:
        db_worker.disconnect()


@app.get(
    path='/submitData/',
    response_model=Dict[int, PerevalResponseModel],
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            'model': BaseErrorResponse,
            'description': 'Validation error'
        },
        status.HTTP_404_NOT_FOUND: {
            'model': BaseErrorResponse,
            'description': 'Not found'
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': BaseErrorResponse,
            'description': 'Internal server error'
        }
    }
)
async def get_user_perevals(
    user_email: str = Query(
        description='User`s Email'
    )
):
    try: 
        db_worker = DatabaseWorker()
        db_worker.connect()
        pereval_list = db_worker.get_pereval_list_by_email(user_email)
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

    if pereval_list:
        return dict(enumerate(pereval_list, start=1))
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'status': status.HTTP_404_NOT_FOUND,
                'message': f'No objects found created by the user with email {user_email}'
            }
        )