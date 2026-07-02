class AppError(Exception):
    pass


class DatabaseError(AppError):
    pass


class NotFoundError(AppError):
    pass


class BadRequestError(AppError):
    pass