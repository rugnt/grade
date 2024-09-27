import hashlib
import csv
import os

from fastapi import Request, APIRouter, Depends, UploadFile, File, Body, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Annotated

from fastapi_localization import TranslateJsonResponse
from app.database import get_db
from app.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from app.models import Book, Category, User
from app.books.schemas import BookSchema
from sqlalchemy.orm import joinedload
from PIL import Image
from app.celery_app import send_email_message
from app.secret import oauth2_scheme
from app.schemas import Payload
from app.books.schemas import BookOutputSchema


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def books(request: Request):
    return templates.TemplateResponse(
        name='books.html', context={'request': request, 'books': ['']}
    )


async def add_book_in_db(
    db: AsyncSession,
    title: str,
    description: str,
    rating: int,
    category_id: int,
    user_id: str,
    file: UploadFile
):
    query = insert(Book).values({
        'title': title,
        'description': description,
        'rating': rating,
        'category_id': category_id,
        'user_id': user_id
    }).returning(Book.id)
    result_from_db = await db.execute(query)
    id_ = result_from_db.scalar_one()
    filetype = file.filename.split('.')[-1]
    image = Image.open(file.file).resize((240, 300))
    filename = f'{hashlib.md5(title.encode()).hexdigest()}{id_}.{filetype}'
    path = os.path.join(
        'media',
        filename
    )
    user_query = select(User).where(User.id == user_id)
    user = await db.execute(user_query)

    send_email_message.delay(f'Вы добавили книгу с названием {title}', user.scalar_one().email)

    await db.execute(update(Book).values({'filename': filename}).where(Book.id == id_))
    logger.info(f'Добавлена книга {title} пользователем {user_id}')
    image.save(path)


@router.get("/api/books", response_class=TranslateJsonResponse, response_model=BookOutputSchema)
async def api_books(
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
    category: str | None = None,
    name: str | None = None,
):
    query = select(Book).options(joinedload(Book.category))

    if len(category or "") > 2:
        query = query.where(Book.category.has(Category.title == category))

    if len(name or "") > 2:
        query = query.where(Book.title.ilike(f'%{name}%'))

    result_from_db = await db.execute(query)

    return {'items': [{
        'id': book.id,
        'title': book.title,
        'description': book.description,
        'rating': book.rating,
        'category': book.category.title,
        'image_url': str(request.url_for('media', path=f'{book.filename}')),
        'detail_url': f'book/{book.id}',
    }
        for book in result_from_db.scalars()
    ]}


@router.get("/book/{id_}", response_class=HTMLResponse)
async def book_detail(request: Request, id_: int, db: Annotated[AsyncSession, Depends(get_db)]):
    book_from_db = await db.execute(select(Book).options(joinedload(Book.category)).where(Book.id == id_))
    book = book_from_db.scalar_one()
    image_url = str(request.url_for('media', path=f'{book.filename}'))
    return templates.TemplateResponse(
        name='detail.html',
        context={'request': request, 'book': book, 'image_url': image_url}
    )


@router.post("/add")
async def add_book(
    db: Annotated[AsyncSession, Depends(get_db)],
    file: Annotated[UploadFile, File(...)],
    token: Annotated[str, Depends(oauth2_scheme)],
    book: BookSchema = Form(...) ,
) -> dict:
    payload = Payload.get_payload_from_token(token)
    await add_book_in_db(
        db,
        book.title,
        book.description,
        book.rating,
        book.category_id,
        payload.user_id,
        file,
    )
    await db.commit()
    return {'success': True}


@router.post("/books/load")
async def upload_csv(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
    file: UploadFile = File(None),
    image: UploadFile = File(None),
):
    user_id = Payload.get_payload_from_token(token).user_id
    contents = await file.read()
    csv_data = contents.decode('utf-8').splitlines()
    csv_reader = csv.reader(csv_data, dialect='excel', delimiter=';')

    for row in csv_reader:
        category_query = insert(Category).values({
            'title': row[3].lower()
        }).on_conflict_do_update(index_elements=['title'], set_={'title': row[3]}).returning(Category.id)
        category_from_db = await db.execute(category_query)

        await add_book_in_db(
            db,
            row[0],
            row[1],
            int(row[2]),
            category_from_db.scalar_one(),
            user_id,
            image,
        )

    await db.commit()

