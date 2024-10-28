class NotFoundException(Exception):
    def __init__(self, detail: str = "Not found."):
        self.detail = detail

class UnauthorizedException(Exception):
    def __init__(self, detail: str = "Unauthorized. Access Denied."):
        self.detail = detail

class AccessDeniedException(Exception):
    def __init__(self, detail: str = "Access denied."):
        self.detail = detail

class SourceTimeoutException(Exception):
    def __init__(self, detail: str = "Source timeout exceeded."):
        self.detail = detail

class SourceUnavailableException(Exception):
    def __init__(self, detail: str = "Source is not available."):
        self.detail = detail

class ConflictException(Exception):
    def __init__(self, detail: str = "Conflict."):
        self.detail = detail

class UnhandledException(Exception):
    def __init__(self, status_code: int = 500, detail: str = "Unknown error occurred."):
        self.status_code = status_code
        self.detail = detail
