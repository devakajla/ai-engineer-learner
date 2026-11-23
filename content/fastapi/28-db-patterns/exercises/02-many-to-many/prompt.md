# Students and courses

A student can join many courses, and a course has many students. That is **many-to-many**. With SQLAlchemy 2.0 (no FastAPI), write:

- `class Base(DeclarativeBase)`
- a link table `enrollments` (a `Table`) with `student_id` and `course_id`. Together they are the **primary key**, so the same pair cannot be stored twice.
- model `Student` → `students`: `id`, `name` (required)
- model `Course` → `courses`: `id`, `title` (required)
- relationships `Student.courses` and `Course.students`, linked with `secondary=enrollments`

Functions that take a `Session`:

- `add_student(session, name) -> Student` and `add_course(session, title) -> Course` (commit + refresh)
- `enroll(session, student_id, course_id) -> bool`: `True` when added, `False` when the student already has the course. `LookupError` if either id is missing.
- `courses_of(session, student_id) -> list[str]`: course titles, sorted
- `students_in(session, course_id) -> list[str]`: student names, sorted
- `popularity(session) -> list[tuple[str, int]]`: every course with its number of students, most students first, ties by title. A course with no students shows `0`.

**Think first:** Why can a many-to-many link not be a single column on one of the two tables?

**Hint:** `Table("enrollments", Base.metadata, Column("student_id", ForeignKey("students.id"), primary_key=True), ...)`, `relationship(secondary=enrollments, back_populates=...)`. For `popularity` use `outerjoin` and `func.count(enrollments.c.student_id)` with `group_by`.
