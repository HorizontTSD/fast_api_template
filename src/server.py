# src/server.py
import logging
from typing import Annotated

# import pandas as pd
import uvicorn
from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.core.configuration.config import settings
from src.core.token import verify_token
from src.models.schemes import HellowRequest
from src.utils.greeting import hellow_names

logger = logging.getLogger(__name__)

app = FastAPI(
    docs_url="/template_fast_api/v1/",
    openapi_url='/template_fast_api/v1/openapi.json',
    dependencies=[Depends(verify_token)] if settings.VERIFY_TOKEN else []
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins_urls(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/template_fast_api/v1/greetings")
async def inputation(body: Annotated[
    HellowRequest, Body(
        example={"names": ['Sasha', 'Nikita', 'Kristina']})]):
    try:
        names = body.names
        if names:
            res = hellow_names(names)
            return res
        else:
            logger.error("Something happened during creation of the search table")
            raise HTTPException(
                status_code=400,
                detail="Bad Request",
                headers={"X-Error": "Something happened during creation of the search table"},
            )
    except Exception as ApplicationError:
        logger.error(ApplicationError.__repr__())
        raise HTTPException(
            status_code=400,
            detail="Unknown Error",
            headers={"X-Error": f"{ApplicationError.__repr__()}"},
        )


@app.get("/")
def read_root():
    return {"message": "Welcome to the indicators System API"}


if __name__ == "__main__":
    try:
        logger.info(f"Starting server on http://{settings.HOST}:{settings.PORT}")
        uvicorn.run(
            "server:app",
            host=settings.HOST,
            port=settings.PORT,
            workers=4,
            log_level="debug",
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")