class NotFoundException(Exception):
    def __init__(self, detail: str = "Source was not found."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail


class UnauthorizedException(Exception):
    def __init__(self, detail: str = "Unauthorized. Provided credentials or token have expired or invalid."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail


class AccessDeniedException(Exception):
    def __init__(self, detail: str = "Access was denied. Provided credentials or token do not have access to this source."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail


class SourceTimeoutException(Exception):
    def __init__(self, detail: str = "Source timeout exceeded. We are working on this issue."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail


class SourceUnavailableException(Exception):
    def __init__(self, detail: str = "Source is not available. We are working on this issue."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail


class ConflictException(Exception):
    def __init__(self, detail: str = "Conflict. Apparently, similar records are already presented in the database."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail


class UnhandledException(Exception):
    def __init__(self, status_code: int = 500, detail: str = "Unknown error occurred. We are working on this issue."):
        self.status_code = status_code
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail
