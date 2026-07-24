# Workout Log API

A secure Flask REST API backend for a personal workout-tracking app. Users
sign up, log in, and manage their own private log of workouts. Authentication
is **session-based** (server-side cookie session, not JWT) — it pairs with
the **sessions client** from the provided frontend repo.

## Project Description

Every workout belongs to exactly one user. All resource routes require an
active login session, and every query is scoped to `user_id == current
user`, so no user can view, edit, or delete another user's data. Passwords
are hashed with `flask-bcrypt` and never stored or returned in plain text.

**Stack:** Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-RESTful,
Flask-Bcrypt, Flask-CORS, SQLite, Faker (for seeding).

## Project Structure 

```
workout-log-api/
├── Pipfile
├── README.md
└── server/
    ├── app.py            # routes (auth + workouts)
    ├── config.py         # Flask app, db, bcrypt, api, CORS setup
    ├── models.py         # User and Workout models
    ├── seed.py           # database seed script
    ├── app.db            # SQLite database (created after migration)
    └── migrations/       # Flask-Migrate migration history
```

## Installation

1. Install dependencies:
   ```bash
   pipenv install
   pipenv shell
   ```
2. Set the Flask app entry point (from inside `server/`, or set the path
   from the project root — examples below assume you `cd server` first):
   ```bash
   cd server
   export FLASK_APP=app.py        # Windows (cmd): set FLASK_APP=app.py
   ```
3. Create and apply the database migrations:
   ```bash
   flask db init        # only needed the very first time
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
4. Seed the database with example users and workouts:
   ```bash
   python seed.py
   ```
   This creates 5 users (all with password `password123`) and several
   workouts each, so you can log in immediately and see data.

## Running the App

From inside `server/`:
```bash
flask run --port 5555
```
The API will be available at `http://127.0.0.1:5555`.

To connect the provided frontend, use the **sessions** version of the client
app and point its API base URL at `http://127.0.0.1:5555`. By default CORS
allows requests from `http://localhost:3000`; override with the
`FRONTEND_ORIGIN` environment variable if your frontend runs elsewhere.

## Endpoints

### Auth

| Method | Route            | Description                                          | Auth required |
|--------|------------------|-------------------------------------------------------|----------------|
| POST   | `/signup`        | Create a new user (`username`, `password`), logs them in | No |
| POST   | `/login`         | Log in with `username` and `password`                | No |
| DELETE | `/logout`        | Clear the current session                             | Yes |
| GET    | `/check_session` | Return the currently logged-in user, or 401           | Yes |

### Workouts

| Method | Route             | Description                                                   | Auth required |
|--------|-------------------|-----------------------------------------------------------------|----------------|
| GET    | `/workouts`       | Paginated list of **your** workouts. Query params: `page` (default 1), `per_page` (default 10) | Yes |
| POST   | `/workouts`       | Create a workout: `title` (required), `description`, `duration_minutes`, `date` (`YYYY-MM-DD`) | Yes |
| GET    | `/workouts/<id>`  | Get a single workout you own                                    | Yes |
| PATCH  | `/workouts/<id>`  | Update a workout you own (any subset of the fields above)        | Yes |
| DELETE | `/workouts/<id>`  | Delete a workout you own                                        | Yes |

All `/workouts` routes return `401 Not authorized` if there's no active
session, and `404 Workout not found` if you try to access, edit, or delete
a workout that either doesn't exist or belongs to another user (the two
cases are indistinguishable on purpose, so users can't probe for the
existence of other people's records).

### Example: paginated response

```json
{
  "workouts": [ { "id": 1, "title": "Leg Day", "description": "...", "duration_minutes": 45, "date": "2026-07-20", "user_id": 3 } ],
  "page": 1,
  "per_page": 10,
  "total": 6,
  "pages": 1
}
```

## Data Model

**User**
- `id`
- `username` (unique, required)
- `_password_hash` (bcrypt hash, never exposed via the API)

**Workout**
- `id`
- `title` (required)
- `description`
- `duration_minutes`
- `date`
- `user_id` (foreign key → `users.id`)
