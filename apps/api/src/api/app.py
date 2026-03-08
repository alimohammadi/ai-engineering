from fastapi import FastAPI
from api.api.middleware import RequestIDMiddleware
from fastapi.middleware.cors import CQRSMiddleware
from api.api.endpoints import api_router

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


app = FastAPI()
app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CQRSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
