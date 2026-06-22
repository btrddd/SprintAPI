from fastapi import FastAPI, status
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
    def validete_coords(cls, coord):
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


def validate_data(data):
    required_fields = ['beauty_title', 'title', 'add_time', 'user', 'coords', 'level', 'images']
    for field in required_fields:
        if field not in data:
            return False, f'Field "{field}" is required and cannot be empty'
        
    required_user_fields = ['email', 'fam', 'name', 'phone']
    for field in required_user_fields:
        if field not in data['user']:
            return False, f'User field "{field}" is required and cannot be empty'
        
    required_coords_fields = ['latitude', 'longitude', 'height']
    for field in required_coords_fields:
        if field not in data['coords']:
            return False, f'Coords field "{field}" is required and cannot be empty'
        
    images = data['images']
    if not images:
        return False, 'There must be at least one image'
    for image in images:
        if 'data' not in image or 'title' not in image:
            return False, 'Each image requires fields "data" and "title"'
        
    return True, None


app = FastAPI(
    title='Pereval API',
    description='SkillFactory API project',
    version='1.0.0'
)


@app.post('/submit', response_model=SubmitDataResponse)
def submitData(request: SubmitDataRequest):
    request_dict = request.model_dump()

    is_valid, error_message = validate_data(request_dict)
    if not is_valid:
        return SubmitDataResponse(
            status=status.HTTP_400_BAD_REQUEST,
            message=error_message,
            id=None
        )
    
    try:
        db_worker = DatabaseWorker()
        db_worker.connect()
        pereval_id = db_worker.add_pereval(request_dict)
    except Exception as ex:
        return SubmitDataResponse(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'Database error: {ex}',
            id=None
        )
    finally:
        db_worker.disconnect()
    
    if not pereval_id:
        return SubmitDataResponse(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message='Error saving to database',
            id=None
        )
    
    return SubmitDataResponse(
        status=status.HTTP_200_OK,
        message=None,
        id=pereval_id
    )