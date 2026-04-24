# UST-pythonweb-hw-06 — Домашня робота №6

SQLAlchemy + Alembic + PostgreSQL: модель «університет» (групи, студенти,
викладачі, предмети, оцінки), міграції, seed та 10 вибірок + 2 додаткові
+ CLI CRUD над усіма моделями.

## Схема бази даних

- **groups** — `id`, `name (unique)`
- **teachers** — `id`, `fullname`
- **subjects** — `id`, `name`, `teacher_id → teachers.id`
- **students** — `id`, `fullname`, `group_id → groups.id`
- **grades** — `id`, `grade`, `grade_date`, `student_id → students.id`,
  `subject_id → subjects.id`

Звʼязки описані через `relationship` / `back_populates` з `ondelete=CASCADE`.

## Запуск контейнера PostgreSQL

```bash
docker run --name studentOleksandr -p 5432:5432 \
    -e POSTGRES_PASSWORD=<ваш_пароль> -d postgres
```

## Конфігурація секретів (`.env`)

Реальні креди БД не живуть у коді й не комітяться в репозиторій.
`connect.py` читає їх із файлу `.env` через `python-dotenv`.

```bash
cp .env.example .env
# відредагуйте .env, пропишіть свої POSTGRES_USER / POSTGRES_PASSWORD / ...
```

Підтримувані змінні (див. `.env.example`):

- `DATABASE_URL` — готовий URL, має пріоритет;
- або окремо: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`,
  `POSTGRES_PORT`, `POSTGRES_DB`.

Файл `.env` у `.gitignore` — комітьте лише `.env.example`.
`alembic.ini` містить плейсхолдерний URL; справжнє значення підставляє
`migrations/env.py` з `connect.url_to_db`.

## Встановлення залежностей

```bash
uv sync
```

## Міграції Alembic

```bash
# згенерувати нову ревізію з моделей
uv run alembic revision --autogenerate -m "init schema"

# застосувати всі міграції
uv run alembic upgrade head

# відкотити все
uv run alembic downgrade base
```

## Наповнення БД

```bash
uv run python seed.py
```

Генерує: 3 групи, 5 викладачів, 8 предметів, 45 студентів, ~3800 оцінок
через `Faker("uk_UA")` і сесію SQLAlchemy.

## Вибірки

```bash
uv run python my_select.py
```

Файл `my_select.py` містить:

| Функція    | Опис |
| ---------- | ---- |
| `select_1`  | 5 студентів із найбільшим середнім балом з усіх предметів |
| `select_2`  | студент із найвищим середнім балом з певного предмета |
| `select_3`  | середній бал у групах з певного предмета |
| `select_4`  | середній бал на потоці (по всій таблиці оцінок) |
| `select_5`  | курси, які читає певний викладач |
| `select_6`  | список студентів у певній групі |
| `select_7`  | оцінки студентів у групі з певного предмета |
| `select_8`  | середній бал, який ставить певний викладач зі своїх предметів |
| `select_9`  | курси, які відвідує певний студент |
| `select_10` | курси, які певному студенту читає певний викладач |
| `select_11` *(доп.)* | середній бал, який певний викладач ставить певному студенту |
| `select_12` *(доп.)* | оцінки студентів у групі з предмета на останньому занятті |

## CLI CRUD (доп. завдання, частина 2)

```bash
# створення
uv run python main.py -a create -m Teacher -n 'Boris Jonson'
uv run python main.py -a create -m Group -n 'AD-999'
uv run python main.py -a create -m Subject -n 'Математика' -t 1
uv run python main.py -a create -m Student -n 'Петро Іваненко' -g 1
uv run python main.py -a create -m Grade --student 1 --subject 1 --grade 10

# перегляд
uv run python main.py -a list -m Teacher
uv run python main.py -a get  -m Teacher --id 3

# оновлення
uv run python main.py -a update -m Teacher --id 3 -n 'Andry Bezos'
uv run python main.py -a update -m Student --id 5 -n 'Оновлене ПІБ' -g 2

# видалення
uv run python main.py -a remove -m Teacher --id 3
```

Підтримувані моделі: `Teacher`, `Group`, `Subject`, `Student`, `Grade`.
Підтримувані дії: `create`, `list`, `get`, `update`, `remove`.

## Структура проєкту

```
homework_6/
├── alembic.ini
├── connect.py
├── main.py                 # CLI CRUD (argparse)
├── models.py               # моделі SQLAlchemy
├── my_select.py            # 10 + 2 запити через session
├── pyproject.toml
├── README.md
├── seed.py                 # Faker + session.add_all + commit
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── *_init_schema.py
└── .venv/                  # створюється uv, не комітити
```
