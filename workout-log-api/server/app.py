"""
API routes.

Auth:    POST /signup, POST /login, DELETE /logout, GET /check_session
Resource: GET/POST /workouts, GET/PATCH/DELETE /workouts/<id>

All /workouts routes require an active session and are scoped to the
logged-in user's own records only.
"""
from datetime import datetime
from functools import wraps

from flask import make_response, request, session
from flask_restful import Resource

from config import api, app, db
from models import User, Workout


def login_required(f):
    """Reject requests with no logged-in user before the route body runs."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return {"error": "Not authorized"}, 401
        return f(*args, **kwargs)

    return wrapper


def parse_date(value):
    """Parse an 'YYYY-MM-DD' string into a date, or raise ValueError."""
    return datetime.strptime(value, "%Y-%m-%d").date()


#  Auth 

class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "Username and password are required."}, 422

        if User.query.filter_by(username=username).first():
            return {"error": "Username is already taken."}, 422

        try:
            user = User(username=username)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"error": str(e)}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password or ""):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"error": "Invalid username or password."}, 401


class Logout(Resource):
    def delete(self):
        if not session.get("user_id"):
            return {"error": "Not authorized"}, 401
        session["user_id"] = None
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user = User.query.get(session.get("user_id"))
        if user:
            return user.to_dict(), 200
        return {"error": "Not authorized"}, 401


# Workouts 

class Workouts(Resource):
    @login_required
    def get(self):
        """Paginated list of the current user's workouts.
        Query params: page (default 1), per_page (default 10)."""
        try:
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 10, type=int)
        except (TypeError, ValueError):
            return {"error": "page and per_page must be integers."}, 422

        pagination = (
            Workout.query.filter_by(user_id=session["user_id"])
            .order_by(Workout.date.desc(), Workout.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            "workouts": [w.to_dict() for w in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    @login_required
    def post(self):
        data = request.get_json() or {}
        try:
            workout_date = parse_date(data["date"]) if data.get("date") else None
            workout = Workout(
                title=data.get("title"),
                description=data.get("description"),
                duration_minutes=data.get("duration_minutes"),
                date=workout_date or datetime.utcnow().date(),
                user_id=session["user_id"],
            )
            db.session.add(workout)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"error": str(e)}, 422

        return workout.to_dict(), 201


class WorkoutByID(Resource):
    def _get_owned_workout(self, id):
        """Only returns the workout if it belongs to the current user."""
        return Workout.query.filter_by(id=id, user_id=session["user_id"]).first()

    @login_required
    def get(self, id):
        workout = self._get_owned_workout(id)
        if not workout:
            return {"error": "Workout not found."}, 404
        return workout.to_dict(), 200

    @login_required
    def patch(self, id):
        workout = self._get_owned_workout(id)
        if not workout:
            return {"error": "Workout not found."}, 404

        data = request.get_json() or {}
        try:
            for field in ("title", "description", "duration_minutes"):
                if field in data:
                    setattr(workout, field, data[field])
            if "date" in data and data["date"]:
                workout.date = parse_date(data["date"])
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"error": str(e)}, 422

        return workout.to_dict(), 200

    @login_required
    def delete(self, id):
        workout = self._get_owned_workout(id)
        if not workout:
            return {"error": "Workout not found."}, 404

        db.session.delete(workout)
        db.session.commit()
        return {}, 204


api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Workouts, "/workouts")
api.add_resource(WorkoutByID, "/workouts/<int:id>")


@app.route("/")
def index():
    return make_response({"message": "Workout Log API is running."}, 200)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
