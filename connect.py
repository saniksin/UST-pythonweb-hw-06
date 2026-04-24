"""Налаштування з'єднання з базою даних PostgreSQL.

Параметри підключення читаються з оточення (файл ``.env`` підхоплюється
через ``python-dotenv``). Якщо задана змінна ``DATABASE_URL`` — вона
використовується напряму; інакше URL збирається з компонентів
``POSTGRES_USER`` / ``POSTGRES_PASSWORD`` / ``POSTGRES_HOST`` /
``POSTGRES_PORT`` / ``POSTGRES_DB``.

Жодних секретів у коді та VCS — справжні значення лежать у ``.env``
(в ``.gitignore``), шаблон — у ``.env.example``.
"""

from __future__ import annotations

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()


def _build_url() -> str:
    direct = os.getenv("DATABASE_URL")
    if direct:
        return direct

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "postgres")

    if password is None:
        raise RuntimeError(
            "POSTGRES_PASSWORD не задано. Скопіюйте .env.example у .env "
            "та пропишіть справжні значення."
        )

    return f"postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:{port}/{db}"


url_to_db = _build_url()

engine = create_engine(url_to_db, echo=False)
DBSession = sessionmaker(bind=engine)
session = DBSession()
