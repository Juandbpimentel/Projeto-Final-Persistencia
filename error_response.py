from fastapi.responses import JSONResponse
import traceback

class ErrorResponse(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

    def to_json_response(self):
        return JSONResponse(
            status_code=self.status_code,
            content={
                "detail": self.message,
                "error_trace": "".join(traceback.format_exception(None, self, self.__traceback__))
            }
        )