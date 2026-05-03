from app import *
from app.models import *
from flask import render_template, session, request
from sqlalchemy import select

# Helper function
def get_user_by_id(user_id):
    return db.session.get(User, user_id)

def get_current_user():
    user_id = session.get("user_id", None)
    if user_id:
        return get_user_by_id(user_id)
    return None

def now():
    return datetime.datetime.now()

#------------------------------------------------------------------------------------------------------------

VALID_STATUSES = ["open", "ongoing", "cancelled", "closed"]

# Main
@app.route("/events")
def events():
    status = request.args.get("status")
    status = status if status in VALID_STATUSES else "all"
    if status == "open":
        events = db.session.scalars(select(Event).where(Event.start_time > now())).all()
    else:
        events = db.session.scalars(select(Event)).all()
    return render_template("events.html", events = events, current_user = get_current_user(), current_time = now())

@app.route("/event/<event_id>")
def event_detail(event_id):
    return render_template("event_detail.html", event = db.session.get(Event, event_id), current_user = get_current_user())