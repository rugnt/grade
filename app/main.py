
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_validation_i18n import I18nMiddleware, i18n_exception_handler
from jose.exceptions import JWTError
from sqlalchemy.exc import NoResultFound

from app.auth.router import router as auth_router
from app.books.routers import router as books_router
from app.sitemap import sitemap


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(auth_router)
app.include_router(books_router)

app.mount('/sitemap.xml', sitemap)


@app.exception_handler(NoResultFound)
async def handler_not_result_error(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


@app.exception_handler(JWTError)
async def handler_unauthorization(request, exc):
    return JSONResponse(status_code=401, content={"detail": "Unauthorization"})
