
# Student Management REST API

A Student Management REST API built using Python, Flask and SQLite.

## Technologies Used

- Python
- Flask
- SQLite Database
- REST API
- Postman

## Features

- Create Student
- Get All Students
- Get Student By ID
- Update Student
- Partial Update Student
- Delete Student
- Search Students
- Count Students
- Create Course
- Get All Courses
- Get Course By ID
- Student Statistics

## Project Structure

Student_API_Project/
│
├── app.py
├── database.py
├── requirements.txt
├── students.db
└── README.md

## Installation

1. Clone the repository.

2. Create virtual environment:

python -m venv .venv

3. Activate environment:

.venv\Scripts\activate

4. Install dependencies:

pip install -r requirements.txt

5. Run application:

python app.py

## API Base URL

http://127.0.0.1:5000

## Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/health | Health Check |
| POST | /api/students | Create Student |
| GET | /api/students | Get All Students |
| GET | /api/students/1 | Get Student |
| PUT | /api/students/1 | Update Student |
| PATCH | /api/students/1 | Partial Update |
| DELETE | /api/students/1 | Delete Student |
| GET | /api/students/search?q=BCA | Search |
| GET | /api/students/count | Count Students |
| POST | /api/courses | Create Course |
| GET | /api/courses | Get Courses |
| GET | /api/courses/1 | Get Course |
| GET | /api/stats | Statistics |

## Author

Piyush Jangid

BCA Student
