from app import *
from app.models import *
from flask import render_template, session, request
from sqlalchemy import select
from functools import reduce
import re

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
    name = request.args.get("name").strip(" ")
    status = status if status in VALID_STATUSES else "all"
    if status == "open":
        events = db.session.scalars(select(Event).where(Event.start_time > now()).where(Event.cancelled == False)).all()
    elif status == "all":
        events = db.session.scalars(select(Event)).all()
    elif status == "cancelled":
        events = db.session.scalars(select(Event).where(Event.cancelled == True)).all()
    elif status == "closed":
        events = db.session.scalars(select(Event).where(Event.end_time < now()).where(Event.cancelled == False)).all()
    else:
        events = db.session.scalars(select(Event).where(Event.start_time < now()).where(Event.end_time > now()).where(Event.cancelled == False)).all()
    events = filter(
        lambda event: name.lower() in event.title.lower(),
        events
    )
    return render_template("events.html", 
                           events = events, 
                           current_user = get_current_user(), 
                           current_time = now(),
                           selected_status = status
    )

@app.route("/event/<event_id>")
def event_detail(event_id):
    event = db.session.get(Event, event_id)
    no_participant = reduce(lambda total, team : total + len(team.members), event.teams, 0)
    return render_template("event_detail.html", 
                           event = event, 
                           current_user = get_current_user(), 
                           no_participant = no_participant
    )