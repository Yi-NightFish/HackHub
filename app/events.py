from app import *
from app.models import *
from flask import render_template, session, request, redirect, url_for
from sqlalchemy import select
from functools import reduce
from app.routes import login_required
import datetime as dt
from forms import EventForm

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

VALID_STATUSES = ["open", "ongoing", "cancelled", "completed"]
VALID_TABS = ["overview", "participants", "teams", "solo"]

# Main
@app.route("/explore")
def explore():
    search_query = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "all")
    sort_by = request.args.get("sort", "newest")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    deadline = request.args.get("deadline", "")
    page = request.args.get("page", 1, type=int)
    current_user = get_current_user()

    if search_query:
        history = session.get("search_history", [])
        if search_query in history:
            history.remove(search_query) #remove old one
        history.insert(0, search_query) #add to front
        session["search_history"] = history[:5]  # Keep only last 5 unique searches
        session.modified = True # tell flask is updated

    query = Event.query.join(User, Event.organizer_id == User.id)

    if search_query:
        query = query.filter(Event.title.ilike(f"%{search_query}%") | Event.description.ilike(f"%{search_query}%") | User.name.ilike(f"%{search_query}%"))
    if status_filter != "all":
        if status_filter == 'completed':
            query = query.filter((Event.end_time < dt.datetime.now()) & (Event.cancelled != True))
        elif status_filter == 'ongoing':
            query = query.filter(((Event.deadline <= dt.datetime.now()) & (Event.end_time >= dt.datetime.now()) & (Event.cancelled != True)))
        elif status_filter == 'open':
            query = query.filter((Event.deadline > dt.datetime.now()) & (Event.cancelled != True))
        elif status_filter == 'cancelled':
            query = query.filter((Event.cancelled == True))
    if start_date:
        query = query.filter(Event.start_time >= start_date)
    if end_date:
        query = query.filter(Event.end_time <= end_date)
    if deadline :
        query = query.filter(Event.deadline <= deadline)
    if sort_by == "newest":
        query = query.order_by(Event.start_time.desc())
    elif sort_by == "oldest":
        query = query.order_by(Event.end_time.asc())
    elif sort_by == "title_asc":
        query = query.order_by(Event.title.asc())
    else:
        query = query.order_by(Event.date.asc())

    paginate = query.paginate(page=page, per_page=12, error_out=False)
    events = paginate.items
    if request.headers.get("HX-Request"):
        return render_template("partials/event_list.html", events = events, search_query = search_query, paginate = paginate or None)
    return render_template(
                        "explore.html", 
                        events = events, 
                        search_query = search_query, 
                        status_filter = status_filter, 
                        current_user = current_user, 
                        sort_by = sort_by, 
                        paginate = paginate, 
                        history = session.get("search_history", [])
    )

@app.route("/event/<event_id>", methods = ["GET", "POST"])
def event_detail(event_id):
    if request.method == "GET":
        active_tab = request.args.get("tab") if request.args.get("tab") in VALID_TABS else "overview"
        event = db.session.get(Event, event_id)
        current_user = get_current_user()

        def get_participants():
            return list(map(lambda participant: participant.user, event.participants))

        participants = get_participants()
        teams = [team for team in event.teams if Participation.query.filter_by(team_id = team.id).count() < team.max_members] if event else []
        
        # Get soloists (participants without a team)
        soloists = [p.user for p in Participation.query.filter_by(event_id=event_id, team_id=None).all()] if event else []

        if active_tab == "overview":
            enrolled = False
            if current_user:
                enrolled = current_user in participants
            no_participant = len(event.participants)
            return render_template(
                "event_detail.html", 
                event = event, 
                current_user = current_user, 
                no_participant = no_participant,
                active_tab = active_tab,
                enrolled = enrolled
            )
        elif active_tab == "participants":
            if not current_user:
                return redirect(url_for("login", next = request.url))
            return render_template(
                "event_detail.html", 
                event = event, 
                current_user = current_user,
                active_tab = active_tab,
                participants = participants
            )
        elif active_tab == "teams":
            return render_template(
                "event_detail.html",
                event = event,
                current_user = current_user,
                active_tab = active_tab,
                teams = teams
            )
        elif active_tab == "solo":
            leader_team = None
            leader_team_member_count = 0
            leader_team_full = False
            if current_user:
                leader_team = Team.query.filter_by(event_id = event_id, leader_id = current_user.id).first()
                if leader_team:
                    leader_team_member_count = Participation.query.filter_by(team_id = leader_team.id).count()
                    leader_team_full = leader_team_member_count >= leader_team.max_members
            return render_template(
                "event_detail.html",
                event = event,
                current_user = current_user,
                active_tab = active_tab,
                soloists = soloists,
                leader_team = leader_team,
                leader_team_member_count = leader_team_member_count,
                leader_team_full = leader_team_full
            )
    else:
        user_id = request.form.get("user-id")
        participation = Participation(
            user_id = user_id,
            event_id = event_id,
            team_id = None
        )
        db.session.add(participation)
        db.session.commit()
        return redirect(request.url)
    
@app.route("/event/<event_id>/invite-soloists", methods=["POST"])
@login_required
def invite_soloists(event_id):
    current_user = get_current_user()
    team = Team.query.filter_by(event_id = event_id, leader_id = current_user.id).first()
    if not team:
        return "Only team leaders can invite soloists"

    if Participation.query.filter_by(team_id = team.id).count() >= team.max_members:
        return "Your team is already full"

    selected_ids = request.form.getlist("soloist_ids")
    if not selected_ids:
        return "Select at least one soloist to invite"

    invited_any = False
    for user_id in selected_ids:
        participation = Participation.query.filter_by(event_id = event_id, user_id = user_id, team_id = None).first()
        if not participation:
            continue
        existing_request = TeamJoinRequest.query.filter_by(team_id = team.id, user_id = user_id, status = "Pending").first()
        if existing_request:
            continue
        if Participation.query.filter_by(team_id = team.id).count() >= team.max_members:
            break
        join_request = TeamJoinRequest(team_id = team.id, user_id = user_id, status = "Pending")
        db.session.add(join_request)
        invited_any = True

    if invited_any:
        db.session.commit()

    return redirect(url_for("event_detail", event_id = event_id, tab = "solo"))

@app.route("/unroll/<event_id>")
@login_required
def unroll(event_id):
    participation = Participation.query.filter_by(event_id = event_id, user_id = get_current_user().id).first()
    print(participation)
    db.session.delete(participation)
    db.session.commit()
    return redirect(url_for("event_detail", event_id = event_id))

@app.route("/event/<event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    event = db.session.get(Event, event_id)
    current_user = get_current_user()
    
    if not event:
        return "Event not found", 404
    
    # Check if current user is the organizer
    if event.organizer_id != session["user_id"]:
        return "Unauthorized: Only the event organizer can edit this event", 403
    
    form = EventForm()
    
    if request.method == "GET":
        # Populate form with existing event data
        form.title.data = event.title
        form.description.data = event.description
        form.start_time.data = event.start_time
        form.end_time.data = event.end_time
        form.deadline.data = event.deadline
    
    if form.validate_on_submit():
        # Validate that end_time is after start_time
        if form.end_time.data <= form.start_time.data:
            form.end_time.errors = ["End time must be after start time"]
            return render_template("edit_event.html", form=form, event=event, current_user=current_user)
        
        # Validate that deadline is before start_time
        if form.deadline.data >= form.start_time.data:
            form.deadline.errors = ["Deadline must be before start time"]
            return render_template("edit_event.html", form=form, event=event, current_user=current_user)
        
        # Update event details
        event.title = form.title.data
        event.description = form.description.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.deadline = form.deadline.data
        
        db.session.commit()
        return redirect(url_for("event_detail", event_id=event.id))
    
    return render_template("edit_event.html", form=form, event=event, current_user=current_user)
