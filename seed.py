"""Наповнення бази даних випадковими даними через Faker.

Обсяги (за ТЗ):
    - 3 групи
    - 3–5 викладачів
    - 5–8 предметів
    - 30–50 студентів
    - до 20 оцінок у кожного студента з усіх предметів

Для запису використовуємо механізм сесій SQLAlchemy.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from faker import Faker

from connect import DBSession
from models import Group, Teacher, Subject, Student, Grade


NUMBER_GROUPS = 3
NUMBER_TEACHERS = 5
NUMBER_SUBJECTS = 8
NUMBER_STUDENTS = 45
MAX_GRADES_PER_STUDENT_PER_SUBJECT = 20
MIN_GRADE = 1
MAX_GRADE = 12  # українська 12-бальна шкала

fake = Faker("uk_UA")


def seed_groups(session) -> list[Group]:
    names = ["AD-101", "AD-102", "AD-103"][:NUMBER_GROUPS]
    groups = [Group(name=n) for n in names]
    session.add_all(groups)
    session.commit()
    return groups


def seed_teachers(session) -> list[Teacher]:
    teachers = [Teacher(fullname=fake.name()) for _ in range(NUMBER_TEACHERS)]
    session.add_all(teachers)
    session.commit()
    return teachers


def seed_subjects(session, teachers: list[Teacher]) -> list[Subject]:
    subject_names = [
        "Математичний аналіз",
        "Лінійна алгебра",
        "Теорія ймовірностей",
        "Програмування на Python",
        "Бази даних",
        "Операційні системи",
        "Алгоритми та структури даних",
        "Веб-технології",
    ][:NUMBER_SUBJECTS]

    # Гарантуємо, що кожен викладач отримає принаймні один предмет:
    # перші len(teachers) предметів розподіляємо по одному на викладача,
    # решту — випадковим чином.
    assigned: list[Teacher] = []
    for i, _ in enumerate(subject_names):
        if i < len(teachers):
            assigned.append(teachers[i])
        else:
            assigned.append(random.choice(teachers))

    subjects = [
        Subject(name=name, teacher=teacher)
        for name, teacher in zip(subject_names, assigned)
    ]
    session.add_all(subjects)
    session.commit()
    return subjects


def seed_students(session, groups: list[Group]) -> list[Student]:
    students = [
        Student(fullname=fake.name(), group=random.choice(groups))
        for _ in range(NUMBER_STUDENTS)
    ]
    session.add_all(students)
    session.commit()
    return students


def seed_grades(
    session, students: list[Student], subjects: list[Subject]
) -> None:
    start_date = datetime(2026, 1, 15)
    end_date = datetime(2026, 4, 24)
    span_days = (end_date - start_date).days

    grades: list[Grade] = []
    for student in students:
        for subject in subjects:
            count = random.randint(1, MAX_GRADES_PER_STUDENT_PER_SUBJECT)
            for _ in range(count):
                grade_value = random.randint(MIN_GRADE, MAX_GRADE)
                grade_date = start_date + timedelta(
                    days=random.randint(0, span_days),
                    hours=random.randint(8, 18),
                    minutes=random.randint(0, 59),
                )
                grades.append(
                    Grade(
                        grade=grade_value,
                        grade_date=grade_date,
                        student=student,
                        subject=subject,
                    )
                )
    session.add_all(grades)
    session.commit()


def main() -> None:
    session = DBSession()
    try:
        print("[seed] groups ...")
        groups = seed_groups(session)
        print(f"         created {len(groups)}")

        print("[seed] teachers ...")
        teachers = seed_teachers(session)
        print(f"         created {len(teachers)}")

        print("[seed] subjects ...")
        subjects = seed_subjects(session, teachers)
        print(f"         created {len(subjects)}")

        print("[seed] students ...")
        students = seed_students(session, groups)
        print(f"         created {len(students)}")

        print("[seed] grades ...")
        seed_grades(session, students, subjects)
        total = session.query(Grade).count()
        print(f"         created {total}")

        print("[seed] done.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
