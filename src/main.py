from fastapi import FastAPI, status, Request, HTTPException 
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.api.routes import router


app = FastAPI(
    title='Pereval API',
    description='SkillFactory API project',
    version='1.0.0'
)

app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    '''
    Handle pydantic validation errors.

    Args:
        request: HTTP request.
        exc: Validation exception instance.

    Returns:
        JSONResponse: Formatted error response, may 
            include status, message, state and id.
    '''
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
async def http_exception_handler(
    request: Request, 
    exc: HTTPException
) -> JSONResponse:
    '''
    Handle HTTP errors.

    Args:
        request: HTTP request.
        exc: HTTP exception instance.

    Returns:
        JSONResponse: Formatted error response.
    '''
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )
