"""10 обовʼязкових + 2 додаткових запити до БД.

Усі запити виконуються через механізм сесій SQLAlchemy.

Обовʼязкові:
    select_1  — 5 студентів із найбільшим середнім балом з усіх предметів.
    select_2  — студент із найвищим середнім балом з певного предмета.
    select_3  — середній бал у групах з певного предмета.
    select_4  — середній бал на потоці (по всій таблиці оцінок).
    select_5  — які курси читає певний викладач.
    select_6  — список студентів у певній групі.
    select_7  — оцінки студентів у окремій групі з певного предмета.
    select_8  — середній бал, який ставить певний викладач зі своїх предметів.
    select_9  — список курсів, які відвідує певний студент.
    select_10 — список курсів, які певному студенту читає певний викладач.

Додаткові:
    select_11 — середній бал, який певний викладач ставить певному студентові.
    select_12 — оцінки студентів у певній групі з певного предмета на останньому занятті.
"""

from __future__ import annotations

from sqlalchemy import desc, func, select

from connect import DBSession
from models import Grade, Group, Student, Subject, Teacher


def select_1(session) -> list[tuple[str, float]]:
    """Знайти 5 студентів із найбільшим середнім балом з усіх предметів."""
    stmt = (
        select(
            Student.fullname,
            func.round(func.avg(Grade.grade), 2).label("avg_grade"),
        )
        .join(Grade, Grade.student_id == Student.id)
        .group_by(Student.id)
        .order_by(desc("avg_grade"))
        .limit(5)
    )
    return session.execute(stmt).all()


def select_2(session, subject_name: str) -> tuple[str, float] | None:
    """Знайти студента із найвищим середнім балом з певного предмета."""
    stmt = (
        select(
            Student.fullname,
            func.round(func.avg(Grade.grade), 2).label("avg_grade"),
        )
        .join(Grade, Grade.student_id == Student.id)
        .join(Subject, Subject.id == Grade.subject_id)
        .where(Subject.name == subject_name)
        .group_by(Student.id)
        .order_by(desc("avg_grade"))
        .limit(1)
    )
    return session.execute(stmt).first()


def select_3(session, subject_name: str) -> list[tuple[str, float]]:
    """Знайти середній бал у групах з певного предмета."""
    stmt = (
        select(
            Group.name,
            func.round(func.avg(Grade.grade), 2).label("avg_grade"),
        )
        .join(Student, Student.group_id == Group.id)
        .join(Grade, Grade.student_id == Student.id)
        .join(Subject, Subject.id == Grade.subject_id)
        .where(Subject.name == subject_name)
        .group_by(Group.id)
        .order_by(Group.name)
    )
    return session.execute(stmt).all()


def select_4(session) -> float:
    """Знайти середній бал на потоці (по всій таблиці оцінок)."""
    stmt = select(func.round(func.avg(Grade.grade), 2))
    return session.execute(stmt).scalar()


def select_5(session, teacher_fullname: str) -> list[str]:
    """Знайти які курси читає певний викладач."""
    stmt = (
        select(Subject.name)
        .join(Teacher, Teacher.id == Subject.teacher_id)
        .where(Teacher.fullname == teacher_fullname)
        .order_by(Subject.name)
    )
    return [row[0] for row in session.execute(stmt).all()]


def select_6(session, group_name: str) -> list[str]:
    """Знайти список студентів у певній групі."""
    stmt = (
        select(Student.fullname)
        .join(Group, Group.id == Student.group_id)
        .where(Group.name == group_name)
        .order_by(Student.fullname)
    )
    return [row[0] for row in session.execute(stmt).all()]


def select_7(session, group_name: str, subject_name: str) -> list[tuple[str, int]]:
    """Знайти оцінки студентів у окремій групі з певного предмета."""
    stmt = (
        select(Student.fullname, Grade.grade, Grade.grade_date)
        .join(Grade, Grade.student_id == Student.id)
        .join(Group, Group.id == Student.group_id)
        .join(Subject, Subject.id == Grade.subject_id)
        .where(Group.name == group_name, Subject.name == subject_name)
        .order_by(Student.fullname, Grade.grade_date)
    )
    return session.execute(stmt).all()


def select_8(session, teacher_fullname: str) -> float | None:
    """Знайти середній бал, який ставить певний викладач зі своїх предметів."""
    stmt = (
        select(func.round(func.avg(Grade.grade), 2))
        .join(Subject, Subject.id == Grade.subject_id)
        .join(Teacher, Teacher.id == Subject.teacher_id)
        .where(Teacher.fullname == teacher_fullname)
    )
    return session.execute(stmt).scalar()


def select_9(session, student_fullname: str) -> list[str]:
    """Знайти список курсів, які відвідує певний студент (має хоча б одну оцінку)."""
    stmt = (
        select(Subject.name)
        .join(Grade, Grade.subject_id == Subject.id)
        .join(Student, Student.id == Grade.student_id)
        .where(Student.fullname == student_fullname)
        .distinct()
        .order_by(Subject.name)
    )
    return [row[0] for row in session.execute(stmt).all()]


def select_10(session, student_fullname: str, teacher_fullname: str) -> list[str]:
    """Список курсів, які певному студенту читає певний викладач."""
    stmt = (
        select(Subject.name)
        .join(Grade, Grade.subject_id == Subject.id)
        .join(Student, Student.id == Grade.student_id)
        .join(Teacher, Teacher.id == Subject.teacher_id)
        .where(
            Student.fullname == student_fullname,
            Teacher.fullname == teacher_fullname,
        )
        .distinct()
        .order_by(Subject.name)
    )
    return [row[0] for row in session.execute(stmt).all()]


# ----- Додаткові запити -----------------------------------------------------


def select_11(session, student_fullname: str, teacher_fullname: str) -> float | None:
    """Середній бал, який певний викладач ставить певному студентові."""
    stmt = (
        select(func.round(func.avg(Grade.grade), 2))
        .join(Subject, Subject.id == Grade.subject_id)
        .join(Student, Student.id == Grade.student_id)
        .join(Teacher, Teacher.id == Subject.teacher_id)
        .where(
            Student.fullname == student_fullname,
            Teacher.fullname == teacher_fullname,
        )
    )
    return session.execute(stmt).scalar()


def select_12(session, group_name: str, subject_name: str) -> list[tuple[str, int]]:
    """Оцінки студентів у певній групі з певного предмета на останньому занятті.

    «Останнє заняття» визначаємо як максимальну дату ``grade_date`` серед
    оцінок цієї групи з цього предмета (з точністю до дня — беремо всі оцінки,
    виставлені тієї ж календарної дати).
    """
    last_day_stmt = (
        select(func.max(func.date(Grade.grade_date)))
        .join(Student, Student.id == Grade.student_id)
        .join(Group, Group.id == Student.group_id)
        .join(Subject, Subject.id == Grade.subject_id)
        .where(Group.name == group_name, Subject.name == subject_name)
    )
    last_day = session.execute(last_day_stmt).scalar()
    if last_day is None:
        return []

    stmt = (
        select(Student.fullname, Grade.grade, Grade.grade_date)
        .join(Grade, Grade.student_id == Student.id)
        .join(Group, Group.id == Student.group_id)
        .join(Subject, Subject.id == Grade.subject_id)
        .where(
            Group.name == group_name,
            Subject.name == subject_name,
            func.date(Grade.grade_date) == last_day,
        )
        .order_by(Student.fullname)
    )
    return session.execute(stmt).all()


# ----- Демонстрація --------------------------------------------------------

if __name__ == "__main__":
    session = DBSession()
    try:
        teacher = session.query(Teacher).first()
        group = session.query(Group).first()
        subject = session.query(Subject).first()
        student = session.query(Student).first()

        print("=" * 70)
        print("select_1 — TOP-5 студентів за середнім балом:")
        for row in select_1(session):
            print(f"  {row.fullname:30s} {row.avg_grade}")

        print(f"\nselect_2 — найкращий студент з предмета {subject.name!r}:")
        row = select_2(session, subject.name)
        print(f"  {row.fullname} — {row.avg_grade}")

        print(f"\nselect_3 — середній бал у групах з {subject.name!r}:")
        for row in select_3(session, subject.name):
            print(f"  {row.name:8s} {row.avg_grade}")

        print("\nselect_4 — середній бал по всій таблиці:")
        print(f"  {select_4(session)}")

        print(f"\nselect_5 — курси викладача {teacher.fullname!r}:")
        for name in select_5(session, teacher.fullname):
            print(f"  • {name}")

        print(f"\nselect_6 — студенти групи {group.name!r}:")
        for name in select_6(session, group.name)[:5]:
            print(f"  • {name}")
        print("  ...")

        print(
            f"\nselect_7 — оцінки студентів групи {group.name!r} "
            f"з {subject.name!r} (перші 5):"
        )
        for row in select_7(session, group.name, subject.name)[:5]:
            print(f"  {row[0]:30s} {row[1]}  {row[2]:%Y-%m-%d}")

        print(f"\nselect_8 — середній бал викладача {teacher.fullname!r}:")
        print(f"  {select_8(session, teacher.fullname)}")

        print(f"\nselect_9 — курси студента {student.fullname!r}:")
        for name in select_9(session, student.fullname)[:5]:
            print(f"  • {name}")

        print(
            f"\nselect_10 — курси студента {student.fullname!r} "
            f"у викладача {teacher.fullname!r}:"
        )
        for name in select_10(session, student.fullname, teacher.fullname):
            print(f"  • {name}")

        print(
            f"\nselect_11 (додатково) — середній бал, який викладач "
            f"{teacher.fullname!r} ставить студенту {student.fullname!r}:"
        )
        print(f"  {select_11(session, student.fullname, teacher.fullname)}")

        print(
            f"\nselect_12 (додатково) — оцінки групи {group.name!r} "
            f"з {subject.name!r} на останньому занятті:"
        )
        for row in select_12(session, group.name, subject.name):
            print(f"  {row[0]:30s} {row[1]}  {row[2]:%Y-%m-%d %H:%M}")
    finally:
        session.close()
