"""
Database models: User and Workout.

Each Workout belongs to exactly one User via a `user_id` foreign key, which
is how per-user access control is enforced at the query level in app.py.
"""
from datetime import date as date_cls

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

from config import bcrypt, db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)

    workouts = db.relationship(
        "Workout", back_populates="user", cascade="all, delete-orphan"
    )

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed directly.")

    @password_hash.setter
    def password_hash(self, password):
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        hashed = bcrypt.generate_password_hash(password.encode("utf-8"))
        self._password_hash = hashed.decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode("utf-8"))

    @validates("username")
    def validate_username(self, key, username):
        if not username or not username.strip():
            raise ValueError("Username must not be empty.")
        return username.strip()

    def to_dict(self):
        return {"id": self.id, "username": self.username}

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    duration_minutes = db.Column(db.Integer)
    date = db.Column(db.Date, default=date_cls.today)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="workouts")

    @validates("title")
    def validate_title(self, key, title):
        if not title or not title.strip():
            raise ValueError("Title is required.")
        return title.strip()

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Duration (minutes) must be a positive number.")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "date": self.date.isoformat() if self.date else None,
            "user_id": self.user_id,
        }

    def __repr__(self):
        return f"<Workout {self.id}: {self.title}>"
