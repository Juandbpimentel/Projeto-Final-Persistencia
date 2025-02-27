# logging_utils.py
from fastapi import Request
import logging
import logging.config
import yaml
from fastapi.responses import JSONResponse

from app.error_response import ErrorResponse

class IgnoreWatchfilesFilter(logging.Filter):
    def filter(self, record):
        return "watchfiles.main" not in record.name

def setup_logging(config_path='configs.yml'):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file.read())
        logging_config = {
            'version': 1,
            'formatters': {
                'default': {
                    'format': config['configs']['logging']['format'],
                },
            },
            'filters': {
                'ignore_watchfiles': {
                    '()': IgnoreWatchfilesFilter,
                },
            },
            'handlers': {
                'file': {
                    'class': 'logging.FileHandler',
                    'formatter': 'default',
                    'filename': config['configs']['logging']['filename'],
                    'filters': ['ignore_watchfiles'],
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                    'filters': ['ignore_watchfiles'],
                },
            },
            'root': {
                'level': config['configs']['logging']['level'].upper(),
                'handlers': ['file', 'console'],
            },
        }
        logging.config.dictConfig(logging_config)

async def log_exceptions_middleware(request: Request, call_next):
    try:
        logging.info(f"Request {request.method} {request.url} received, body: {await request.body()}")
        response = await call_next(request)
        logging.info(f"Request {request.method} {request.url} processed: {response.status_code}")
        return response
    except Exception as exc:
        if not isinstance(exc, ErrorResponse):
            logging.error(f"Unhandled error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error", "error": str(exc)}
            )
        exc = ErrorResponse(exc.status_code, exc.message)
        return exc.to_json_response()