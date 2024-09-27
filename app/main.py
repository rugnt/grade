import asgi_sitemaps
import logging
import sys

from fastapi_validation_i18n import I18nMiddleware, i18n_exception_handler
from app.sitemap import sitemap
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from starlette.routing import Route, Router
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound
from app.auth.router import router as auth_router
from app.books.routers import router as books_router
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles
from jose.exceptions import JWTError


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(auth_router)
app.include_router(books_router)

app.mount('/sitemap.xml', sitemap)

app.add_middleware(I18nMiddleware, locale_path='locale', fallback_locale=('en-US',))


@app.exception_handler(NoResultFound)
async def handler_not_result_error(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


@app.exception_handler(JWTError)
async def handler_unauthorization(request, exc):
    return JSONResponse(status_code=401, content={"detail": "Unauthorization"})


app.add_exception_handler(
    RequestValidationError,
    i18n_exception_handler
)
