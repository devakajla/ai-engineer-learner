from sqlalchemy import Column, ForeignKey, String, Table, desc, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


enrollments = Table(
    "enrollments",
    Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    courses: Mapped[list["Course"]] = relationship(secondary=enrollments, back_populates="students")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    students: Mapped[list[Student]] = relationship(secondary=enrollments, back_populates="courses")


def add_student(session: Session, name: str) -> Student:
    student = Student(name=name)
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def add_course(session: Session, title: str) -> Course:
    course = Course(title=title)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


def enroll(session: Session, student_id: int, course_id: int) -> bool:
    student = session.get(Student, student_id)
    course = session.get(Course, course_id)
    if student is None or course is None:
        raise LookupError("student or course not found")
    if course in student.courses:
        return False
    student.courses.append(course)
    session.commit()
    return True


def courses_of(session: Session, student_id: int) -> list[str]:
    student = session.get(Student, student_id)
    if student is None:
        raise LookupError("student not found")
    return sorted(c.title for c in student.courses)


def students_in(session: Session, course_id: int) -> list[str]:
    course = session.get(Course, course_id)
    if course is None:
        raise LookupError("course not found")
    return sorted(s.name for s in course.students)


def popularity(session: Session) -> list[tuple[str, int]]:
    count = func.count(enrollments.c.student_id)
    rows = session.execute(
        select(Course.title, count)
        .outerjoin(enrollments, enrollments.c.course_id == Course.id)
        .group_by(Course.id)
        .order_by(desc(count), Course.title)
    )
    return [(title, n) for title, n in rows]
