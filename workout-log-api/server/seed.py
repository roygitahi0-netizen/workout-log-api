"""Seed the database with example users and workouts.

Run with: python seed.py  (or `pipenv run python server/seed.py`)
"""
from datetime import date, timedelta
from random import choice, randint

from faker import Faker

from app import app
from config import db
from models import User, Workout

fake = Faker()

WORKOUT_TITLES = [
    "Leg Day",
    "Push Day",
    "Pull Day",
    "Cardio Blast",
    "Full Body",
    "Core Crusher",
    "Yoga Flow",
    "HIIT Session",
    "Upper Body Strength",
    "Recovery Walk",
]

SEED_PASSWORD = "password123"  


def seed():
    with app.app_context():
        print("Clearing existing data...")
        Workout.query.delete()
        User.query.delete()
        db.session.commit()

        print("Seeding users...")
        users = []
        for _ in range(5):
            user = User(username=fake.unique.user_name())
            user.password_hash = SEED_PASSWORD
            db.session.add(user)
            users.append(user)
        db.session.commit()

        print("Seeding workouts...")
        for user in users:
            for _ in range(randint(3, 8)):
                workout = Workout(
                    title=choice(WORKOUT_TITLES),
                    description=fake.sentence(nb_words=8),
                    duration_minutes=randint(15, 90),
                    date=date.today() - timedelta(days=randint(0, 60)),
                    user_id=user.id,
                )
                db.session.add(workout)
        db.session.commit()

        print(f"Done! Seeded {len(users)} users (password: '{SEED_PASSWORD}') "
              f"and {Workout.query.count()} workouts.")


if __name__ == "__main__":
    seed()
