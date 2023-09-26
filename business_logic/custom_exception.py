from fastapi import HTTPException


class ForwardTaskException(HTTPException):
    def __init__(self, detail):
        self.detail = detail
        super().__init__(status_code=561, detail=detail)
