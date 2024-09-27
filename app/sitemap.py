import asgi_sitemaps

from app.database import async_session_maker
from sqlalchemy import select
from app.models import Book
from app.config import settings


domain = f"{settings.HOST}:{settings.HTTP_PORT}"


class Sitemap(asgi_sitemaps.Sitemap):
    async def items(self):
        query = select(Book)
        async with async_session_maker() as session:
            run = True
            offset = 0
            while run:
                result_from_db = await session.execute(query.offset(offset).limit(20))
                run = False
                for item in result_from_db.scalars():
                    id_ = item.id
                    run = True
                    yield f'book/{id_}'
                offset += 20
            return

    def location(self, item: str):
        return item

    def changefreq(self, item: str):
        return "monthly"


sitemap = asgi_sitemaps.SitemapApp(Sitemap(), domain=domain)