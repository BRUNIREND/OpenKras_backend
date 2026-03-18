import asyncio

from sqlalchemy import select

from app.database.session import AsyncSessionLocal, engine
from app.models.excursion import Base, Excursion
from app.models.point import Point


async def seed_data():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # 1. Создаем таблицы (в асинхронном режиме)
            # Примечание: В продакшене лучше через Alembic, но для диплома ок
            conn = await engine.connect()
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()
            await conn.close()

            # 2. Проверяем наличие данных
            result = await session.execute(select(Point).limit(1))
            if result.scalars().first():
                print("Данные уже есть.")
                return

            # 3. Создаем точки Красноярска
            p1 = Point(
                title="Краеведческий музей",
                description="Здание в египетском стиле на берегу Енисея.",
                latitude=56.0091,
                longitude=92.8711,
                audio_url="/static/audio/museum.mp3"
            )

            p2 = Point(
                title="Речной вокзал",
                description="Памятник архитектуры сталинского ампира.",
                latitude=56.0085,
                longitude=92.8765,
                audio_url="/static/audio/river_station.mp3"
            )

            # 4. Создаем экскурсию и связываем
            excursion_1 = Excursion(
                title="По набережной Енисея",
                description="Маршрут от музея до Виноградовского моста."
            )

            # В асинхронной SQLAlchemy связи Many-to-Many через .append работают,
            # но нужно убедиться, что объекты добавлены в сессию
            excursion_1.points = [p1, p2]

            session.add(excursion_1)
            # commit произойдет автоматически при выходе из context manager 'begin'

        print("Тестовые данные успешно загружены (Async)!")


if __name__ == "__main__":
    asyncio.run(seed_data())