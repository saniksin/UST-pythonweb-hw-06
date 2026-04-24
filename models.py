"""Моделі SQLAlchemy для домашнього завдання №6.

Схема бази даних:
    - groups      (groups.id, groups.name)
    - teachers    (teachers.id, teachers.fullname)
    - subjects    (subjects.id, subjects.name, teacher_id -> teachers.id)
    - students    (students.id, students.fullname, group_id -> groups.id)
    - grades      (grades.id, grade, grade_date,
                   student_id -> students.id, subject_id -> subjects.id)
"""
from datetime import datetime

from sqlalchemy import ForeignKey, String, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    students: Mapped[list["Student"]] = relationship(
        back_populates="group", cascade="all, delete"
    )

    def __repr__(self) -> str:
        return f"<Group id={self.id} name={self.name!r}>"


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(150), nullable=False)

    subjects: Mapped[list["Subject"]] = relationship(
        back_populates="teacher", cascade="all, delete"
    )

    def __repr__(self) -> str:
        return f"<Teacher id={self.id} fullname={self.fullname!r}>"


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False
    )

    teacher: Mapped["Teacher"] = relationship(back_populates="subjects")
    grades: Mapped[list["Grade"]] = relationship(
        back_populates="subject", cascade="all, delete"
    )

    def __repr__(self) -> str:
        return f"<Subject id={self.id} name={self.name!r} teacher_id={self.teacher_id}>"


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(150), nullable=False)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )

    group: Mapped["Group"] = relationship(back_populates="students")
    grades: Mapped[list["Grade"]] = relationship(
        back_populates="student", cascade="all, delete"
    )

    def __repr__(self) -> str:
        return f"<Student id={self.id} fullname={self.fullname!r} group_id={self.group_id}>"


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    grade_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )

    student: Mapped["Student"] = relationship(back_populates="grades")
    subject: Mapped["Subject"] = relationship(back_populates="grades")

    def __repr__(self) -> str:
        return (
            f"<Grade id={self.id} grade={self.grade} "
            f"student_id={self.student_id} subject_id={self.subject_id} "
            f"date={self.grade_date:%Y-%m-%d}>"
        )
