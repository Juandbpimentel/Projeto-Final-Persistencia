# logging_utils.py
from fastapi import Request
import logging
import logging.config
import yaml
from fastapi.responses import JSONResponse

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
            'handlers': {
                'file': {
                    'class': 'logging.FileHandler',
                    'formatter': 'default',
                    'filename': config['configs']['logging']['filename'],
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
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
        response = await call_next(request)
        return response
    except Exception as exc:
        logging.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )