from typing import Dict

from fastapi import APIRouter, status, Query, Path
from fastapi.exceptions import HTTPException

from src.db.db_worker import DatabaseWorker
from src.models.requests import (
    PerevalRequestModel,
    PatchPerevalRequestModel
)
from src.models.responses import (
    BaseErrorResponse,
    SubmitDataErrorResponse,
    PatchPerevalErrorResponse,
    SubmitDataResponseModel,
    PerevalResponseModel,
    PatchPerevalResponseModel
)


router = APIRouter()


@router.post(
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
    '''
    Create a new pereval record. 
    
    Enpoint adds all pereval data (include user`s data, 
    coordinates, diff levels, images) to the database.

    Args: 
        request: Pereval request model.
    
    Returns:
        SubmitDataResponseModel: Contains http status, error 
            message and id of new record.

    Raises:
        HTTPException: If validation fails or db error occurs.
    '''
    request_dict = request.model_dump()
    
    try:
        db_worker = DatabaseWorker()
        db_worker.connect()

        pereval_id = db_worker.add_pereval(request_dict)

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
        if db_worker:
            db_worker.disconnect()


@router.get(
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
        description='Unique identifier of the pereval',
        ge=1
    )
) -> PerevalResponseModel:
    '''
    Retrieve a pereval by it`s id.

    Args:
        id: Unique identifier of the pereval.

    Returns:
        PerevalResponseModel: Pereval data with all related entities.

    Raises:
        HTTPException: If pereval isn`t found or db error occurs.
    '''
    try:
        db_worker = DatabaseWorker()
        db_worker.connect()

        pereval_data = db_worker.get_pereval_by_id(id)

        if not pereval_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f'Object with id = {id} not found'
                }
            )
        
        return PerevalResponseModel(**pereval_data)

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': ex
            }
        )
    
    finally:
        if db_worker:
            db_worker.disconnect()


@router.patch(
    path='/submitData/{id}',
    response_model=PatchPerevalResponseModel,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            'model': PatchPerevalErrorResponse,
            'description': 'Validation error'
        },
        status.HTTP_404_NOT_FOUND: {
            'model': PatchPerevalErrorResponse,
            'description': 'Not found'
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': PatchPerevalErrorResponse,
            'description': 'Bad request'
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
        description='Unique identifier of the pereval',
        ge=1
    )
) -> PatchPerevalResponseModel:
    '''
    Particuly update a pereval record.

    Can`t update pereval with status other than "new".
    Only field that are provided in the request will be updated.

    Args:
        request: Patch data request model with optional fields.
        id: Unique identifier of the pereval.

    Returns:
        PatchPerevalResponseModel: Contains state (1-success, 0-error) 
            and error message.

    Raises:
        HTTPException: If any operation fails.
    '''
    request_dict = request.model_dump(exclude_unset=True)

    if not request_dict:
        return PatchPerevalResponseModel(
            state=1,
            message=message
        )

    try:
        db_worker = DatabaseWorker()
        db_worker.connect()

        pereval = db_worker.get_pereval_by_id(id)

        if not pereval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    'state': 0,
                    'message': f'Pereval with id = {id} not found'
                }
            )

        if pereval['status'] != 'new':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    'state': 0,
                    'message': f'Can`t update pereval with status other than "new"'
                }
            )

        state, message = db_worker.update_pereval(pereval, request_dict)

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
        if db_worker:
            db_worker.disconnect()


@router.get(
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
        description='User`s Email',
        min_length=5,
        max_length=255
    )
) -> Dict[int, PerevalResponseModel]:
    '''
    Retrieve all perevals created by user.

    Args:
        user_email: User`s Email.

    Returns:
        Dict[int, PerevalResponseModel]: Dictionary mapping indexes
            to pereval data.
    
    Raises:
        HTTPException: If no perevals are found or db error occurs.
    '''
    try: 
        db_worker = DatabaseWorker()
        db_worker.connect()

        pereval_list = db_worker.get_pereval_list_by_email(user_email)

        if not pereval_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f'No objects found created by the user with email {user_email}'
                }
            )
        
        return dict(enumerate(pereval_list, start=1))

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': ex
            }
        )
    
    finally:
        if db_worker:
            db_worker.disconnect()
