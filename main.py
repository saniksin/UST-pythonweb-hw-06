"""CLI для CRUD операцій над усіма моделями (додаткове завдання, частина 2).

Приклади виконання:

    # Створення
    uv run python main.py -a create -m Teacher -n 'Boris Jonson'
    uv run python main.py -a create -m Group -n 'AD-101'
    uv run python main.py -a create -m Subject -n 'Математика' -t 1
    uv run python main.py -a create -m Student -n 'Петро Іваненко' -g 1
    uv run python main.py -a create -m Grade --student 1 --subject 1 --grade 10

    # Перегляд
    uv run python main.py -a list -m Teacher
    uv run python main.py -a list -m Student
    uv run python main.py -a get  -m Teacher --id 3

    # Оновлення
    uv run python main.py -a update -m Teacher --id 3 -n 'Andry Bezos'
    uv run python main.py -a update -m Student --id 5 -n 'Оновлене ПІБ' -g 2

    # Видалення
    uv run python main.py -a remove -m Teacher --id 3
"""
from __future__ import annotations

import argparse
from datetime import datetime

from connect import DBSession
from models import Base, Grade, Group, Student, Subject, Teacher


MODEL_MAP: dict[str, type[Base]] = {
    "Teacher": Teacher,
    "Group": Group,
    "Subject": Subject,
    "Student": Student,
    "Grade": Grade,
}


# --- Рендеринг ------------------------------------------------------------

def _render(obj) -> str:
    if isinstance(obj, Teacher):
        return f"[{obj.id}] Teacher: {obj.fullname}"
    if isinstance(obj, Group):
        return f"[{obj.id}] Group: {obj.name}"
    if isinstance(obj, Subject):
        return f"[{obj.id}] Subject: {obj.name} (teacher_id={obj.teacher_id})"
    if isinstance(obj, Student):
        return f"[{obj.id}] Student: {obj.fullname} (group_id={obj.group_id})"
    if isinstance(obj, Grade):
        return (
            f"[{obj.id}] Grade: {obj.grade}  "
            f"student_id={obj.student_id} subject_id={obj.subject_id} "
            f"date={obj.grade_date:%Y-%m-%d %H:%M}"
        )
    return repr(obj)


# --- CRUD ------------------------------------------------------------------

def _build_kwargs(model: type[Base], args: argparse.Namespace) -> dict:
    """Побудувати словник полів з аргументів CLI відповідно до моделі."""
    if model is Teacher:
        data = {}
        if args.name is not None:
            data["fullname"] = args.name
        return data
    if model is Group:
        data = {}
        if args.name is not None:
            data["name"] = args.name
        return data
    if model is Subject:
        data = {}
        if args.name is not None:
            data["name"] = args.name
        if args.teacher is not None:
            data["teacher_id"] = args.teacher
        return data
    if model is Student:
        data = {}
        if args.name is not None:
            data["fullname"] = args.name
        if args.group is not None:
            data["group_id"] = args.group
        return data
    if model is Grade:
        data = {}
        if args.grade is not None:
            data["grade"] = args.grade
        if args.student is not None:
            data["student_id"] = args.student
        if args.subject is not None:
            data["subject_id"] = args.subject
        if args.date is not None:
            data["grade_date"] = datetime.fromisoformat(args.date)
        return data
    raise ValueError(f"Unsupported model: {model}")


def action_create(session, model: type[Base], args) -> None:
    data = _build_kwargs(model, args)
    if not data:
        raise SystemExit("Для create потрібно вказати поля моделі.")
    obj = model(**data)
    session.add(obj)
    session.commit()
    print(f"[create] {_render(obj)}")


def action_list(session, model: type[Base], args) -> None:
    items = session.query(model).order_by(model.id).all()
    if not items:
        print("(порожньо)")
        return
    for obj in items:
        print(_render(obj))


def action_get(session, model: type[Base], args) -> None:
    if args.id is None:
        raise SystemExit("Для get потрібен --id.")
    obj = session.get(model, args.id)
    if obj is None:
        raise SystemExit(f"{model.__name__} id={args.id} не знайдено.")
    print(_render(obj))


def action_update(session, model: type[Base], args) -> None:
    if args.id is None:
        raise SystemExit("Для update потрібен --id.")
    obj = session.get(model, args.id)
    if obj is None:
        raise SystemExit(f"{model.__name__} id={args.id} не знайдено.")
    data = _build_kwargs(model, args)
    if not data:
        raise SystemExit("Не вказано жодного поля для оновлення.")
    for key, value in data.items():
        setattr(obj, key, value)
    session.commit()
    print(f"[update] {_render(obj)}")


def action_remove(session, model: type[Base], args) -> None:
    if args.id is None:
        raise SystemExit("Для remove потрібен --id.")
    obj = session.get(model, args.id)
    if obj is None:
        raise SystemExit(f"{model.__name__} id={args.id} не знайдено.")
    session.delete(obj)
    session.commit()
    print(f"[remove] {model.__name__} id={args.id} видалено.")


ACTIONS = {
    "create": action_create,
    "list": action_list,
    "get": action_get,
    "update": action_update,
    "remove": action_remove,
}


# --- argparse --------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI для CRUD над Teacher/Group/Subject/Student/Grade"
    )
    parser.add_argument(
        "-a", "--action", required=True, choices=ACTIONS.keys(),
        help="CRUD операція: create / list / get / update / remove",
    )
    parser.add_argument(
        "-m", "--model", required=True, choices=MODEL_MAP.keys(),
        help="модель, над якою виконується операція",
    )
    parser.add_argument("--id", type=int, help="первинний ключ запису")
    parser.add_argument("-n", "--name", help="ім'я / ПІБ / назва")
    parser.add_argument(
        "-g", "--group", type=int, help="group_id (для Student)"
    )
    parser.add_argument(
        "-t", "--teacher", type=int, help="teacher_id (для Subject)"
    )
    parser.add_argument(
        "--student", type=int, help="student_id (для Grade)"
    )
    parser.add_argument(
        "--subject", type=int, help="subject_id (для Grade)"
    )
    parser.add_argument(
        "--grade", type=int, help="значення оцінки (для Grade)"
    )
    parser.add_argument(
        "-d", "--date",
        help="дата оцінки в ISO (для Grade). Напр. 2026-04-24T10:30",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    model = MODEL_MAP[args.model]
    action = ACTIONS[args.action]
    session = DBSession()
    try:
        action(session, model, args)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
