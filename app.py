
from flask import Flask, jsonify, request
from database import init_db, get_db_connection
import sqlite3

app = Flask(__name__)


# =====================================
# HOME API
# =====================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "message": "Welcome to Student Management API"
    }), 200


# =====================================
# API 1: HEALTH CHECK
# =====================================

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "Server is working"
    }), 200


# =====================================
# API 2: CREATE STUDENT (POST)
# =====================================

@app.route("/api/students", methods=["POST"])
def create_student():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Please send valid JSON"
        }), 400

    name = data.get("name")
    email = data.get("email")
    age = data.get("age")
    course = data.get("course")

    if not all([name, email, course]):
        return jsonify({
            "status": "error",
            "message": "Name, email and course are required"
        }), 400

    if not all(isinstance(v, str) for v in [name, email, course]):
        return jsonify({
            "status": "error",
            "message": "Name, email and course must be text"
        }), 400

    if not all(v.strip() for v in [name, email, course]):
        return jsonify({
            "status": "error",
            "message": "Fields cannot be empty"
        }), 400

    if age is not None and (type(age) is not int or age < 1):
        return jsonify({
            "status": "error",
            "message": "Age must be a positive number"
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students (name, email, age, course)
            VALUES (?, ?, ?, ?)
            """,
            (name.strip(), email.strip(), age, course.strip())
        )

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Student added successfully",
            "student_id": cursor.lastrowid
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "status": "error",
            "message": "This email already exists"
        }), 409

    finally:
        conn.close()


# =====================================
# API 3: GET ALL STUDENTS
# =====================================

@app.route("/api/students", methods=["GET"])
def get_students():

    conn = get_db_connection()

    try:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

        return jsonify({
            "status": "success",
            "total_students": len(students),
            "students": [dict(student) for student in students]
        }), 200

    finally:
        conn.close()


# =====================================
# API 4: GET SINGLE STUDENT
# =====================================

@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):

    conn = get_db_connection()

    try:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "status": "error",
                "message": "Student not found"
            }), 404

        return jsonify({
            "status": "success",
            "student": dict(student)
        }), 200

    finally:
        conn.close()


# =====================================
# API 5: UPDATE STUDENT (PUT)
# =====================================

@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Please send valid JSON"
        }), 400

    name = data.get("name")
    email = data.get("email")
    age = data.get("age")
    course = data.get("course")

    if not all([name, email, course]):
        return jsonify({
            "status": "error",
            "message": "Name, email and course are required"
        }), 400

    if not all(isinstance(v, str) for v in [name, email, course]):
        return jsonify({
            "status": "error",
            "message": "Name, email and course must be text"
        }), 400

    if not all(v.strip() for v in [name, email, course]):
        return jsonify({
            "status": "error",
            "message": "Fields cannot be empty"
        }), 400

    if age is not None and (type(age) is not int or age < 1):
        return jsonify({
            "status": "error",
            "message": "Age must be a positive number"
        }), 400

    conn = get_db_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        if existing is None:
            return jsonify({
                "status": "error",
                "message": "Student not found"
            }), 404

        conn.execute(
            """
            UPDATE students
            SET name = ?, email = ?, age = ?, course = ?
            WHERE id = ?
            """,
            (name.strip(), email.strip(), age, course.strip(), student_id)
        )

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Student updated successfully",
            "student_id": student_id
        }), 200

    except sqlite3.IntegrityError:
        return jsonify({
            "status": "error",
            "message": "This email already exists"
        }), 409

    finally:
        conn.close()


# =====================================
# API 6: PATCH STUDENT
# =====================================

@app.route("/api/students/<int:student_id>", methods=["PATCH"])
def patch_student(student_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "status": "error",
            "message": "Please provide JSON data"
        }), 400

    allowed_fields = {"name", "email", "age", "course"}

    if not set(data).issubset(allowed_fields):
        return jsonify({
            "status": "error",
            "message": "Invalid field provided"
        }), 400

    for field in ("name", "email", "course"):
        if field in data:
            if not isinstance(data[field], str) or not data[field].strip():
                return jsonify({
                    "status": "error",
                    "message": f"{field} must be non-empty text"
                }), 400

    if "age" in data:
        if data["age"] is not None and (
            type(data["age"]) is not int or data["age"] < 1
        ):
            return jsonify({
                "status": "error",
                "message": "Age must be a positive number"
            }), 400

    conn = get_db_connection()

    try:
        student = conn.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "status": "error",
                "message": "Student not found"
            }), 404

        updates = {
            key: value.strip() if isinstance(value, str) else value
            for key, value in data.items()
        }

        set_clause = ", ".join(
            f"{field} = ?" for field in updates
        )

        values = list(updates.values()) + [student_id]

        conn.execute(
            f"UPDATE students SET {set_clause} WHERE id = ?",
            values
        )

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Student partially updated successfully",
            "student_id": student_id,
            "updated_fields": list(updates.keys())
        }), 200

    except sqlite3.IntegrityError:
        return jsonify({
            "status": "error",
            "message": "This email already exists"
        }), 409

    finally:
        conn.close()


# =====================================
# API 7: DELETE STUDENT
# =====================================

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):

    conn = get_db_connection()

    try:
        student = conn.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "status": "error",
                "message": "Student not found"
            }), 404

        conn.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Student deleted successfully",
            "student_id": student_id
        }), 200

    finally:
        conn.close()


# =====================================
# API 8: SEARCH STUDENTS
# =====================================

@app.route("/api/students/search", methods=["GET"])
def search_students():

    search_query = request.args.get("q", "").strip()

    if not search_query:
        return jsonify({
            "status": "error",
            "message": "Please provide a search query"
        }), 400

    conn = get_db_connection()

    try:
        search_value = f"%{search_query}%"

        students = conn.execute(
            """
            SELECT * FROM students
            WHERE name LIKE ?
            OR email LIKE ?
            OR course LIKE ?
            ORDER BY id DESC
            """,
            (search_value, search_value, search_value)
        ).fetchall()

        return jsonify({
            "status": "success",
            "search_query": search_query,
            "total_results": len(students),
            "students": [dict(student) for student in students]
        }), 200

    finally:
        conn.close()


# =====================================
# API 9: COUNT STUDENTS
# =====================================

@app.route("/api/students/count", methods=["GET"])
def count_students():

    conn = get_db_connection()

    try:
        result = conn.execute(
            "SELECT COUNT(*) AS total FROM students"
        ).fetchone()

        return jsonify({
            "status": "success",
            "total_students": result["total"],
            "message": "Student count fetched successfully"
        }), 200

    finally:
        conn.close()


# =====================================
# API 10: CREATE COURSE
# =====================================

@app.route("/api/courses", methods=["POST"])
def create_course():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Please send valid JSON"
        }), 400

    course_name = data.get("course_name")
    description = data.get("description", "")
    duration = data.get("duration", "")

    if not isinstance(course_name, str) or not course_name.strip():
        return jsonify({
            "status": "error",
            "message": "Course name is required"
        }), 400

    if not isinstance(description, str) or not isinstance(duration, str):
        return jsonify({
            "status": "error",
            "message": "Description and duration must be text"
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO courses (course_name, description, duration)
            VALUES (?, ?, ?)
            """,
            (course_name.strip(), description.strip(), duration.strip())
        )

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Course added successfully",
            "course_id": cursor.lastrowid
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "status": "error",
            "message": "This course already exists"
        }), 409

    finally:
        conn.close()


# =====================================
# API 11: GET ALL COURSES
# =====================================

@app.route("/api/courses", methods=["GET"])
def get_courses():

    conn = get_db_connection()

    try:
        courses = conn.execute(
            "SELECT * FROM courses ORDER BY id DESC"
        ).fetchall()

        return jsonify({
            "status": "success",
            "total_courses": len(courses),
            "courses": [dict(course) for course in courses]
        }), 200

    finally:
        conn.close()


# =====================================
# API 12: GET SINGLE COURSE BY ID
# =====================================

@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_single_course(course_id):

    conn = get_db_connection()

    try:
        course = conn.execute(
            "SELECT * FROM courses WHERE id = ?",
            (course_id,)
        ).fetchone()

        if course is None:
            return jsonify({
                "status": "error",
                "message": "Course not found"
            }), 404

        return jsonify({
            "status": "success",
            "course": dict(course)
        }), 200

    finally:
        conn.close()


# =====================================
# API 13: STUDENT & COURSE STATISTICS
# =====================================

@app.route("/api/stats", methods=["GET"])
def get_statistics():

    conn = get_db_connection()

    try:
        student_count = conn.execute(
            "SELECT COUNT(*) AS total FROM students"
        ).fetchone()["total"]

        course_count = conn.execute(
            "SELECT COUNT(*) AS total FROM courses"
        ).fetchone()["total"]

        course_stats = conn.execute(
            """
            SELECT course, COUNT(*) AS total_students
            FROM students
            GROUP BY course
            ORDER BY course
            """
        ).fetchall()

        return jsonify({
            "status": "success",
            "statistics": {
                "total_students": student_count,
                "total_courses": course_count,
                "students_by_course": [
                    dict(row) for row in course_stats
                ]
            },
            "message": "Statistics fetched successfully"
        }), 200

    finally:
        conn.close()


# =====================================
# RUN FLASK SERVER
# =====================================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)
