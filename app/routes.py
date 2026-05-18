from flask import render_template, request, url_for, redirect, session, make_response, current_app
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
import datetime as dt
from flask_mail import Message as MailMessage
import functools
import qrcode
import io
import base64
import os
import json
from werkzeug.utils import secure_filename

from app import app, db, mail
from app.models import *
from app.forms import ProfileForm, TaskForm
from sqlalchemy import select, case, update

#By Wan Yi
# Helper functions
def send_otp(email, purpose):
    otp = str(random.randint(100000, 999999))
    db.session.add(
        OTP(
            email=email,
            code=otp,
            purpose=purpose,
            expiry=dt.datetime.now() + dt.timedelta(minutes=5)
        )
    )
    db.session.commit()
    # msg = Message(
    #     "HackHub OTP",
    #     sender=app.config["MAIL_USERNAME"],
    #     recipients=[email]
    # )
    # msg.body = f"Your OTP is: {otp}"
    # mail.send(msg)

    # Use this to get otp without actually sending to email during development
    print(f"Sent OTP: {otp} -> {email}")
    
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # Check if the user is logged in
        if "user_id" not in session:
            # If not logged in, redirect them to the login page
            return redirect(url_for("login"))
        # If logged in, proceed to the requested page
        return view(**kwargs)
    return wrapped_view

def verify_otp(purpose, session_key):
    email = session.get(session_key)
    if not email:
        return False
    otp = request.form["otp"]
    otp_record = OTP.query.filter_by(
        email=email,
        code=otp,
        purpose=purpose
    ).first()
    if otp_record and otp_record.expiry > dt.datetime.now():
        db.session.delete(otp_record)
        db.session.commit()
        return True
    return False

def add_task_activity(task_id, action):
    user_id = session.get("user_id")
    activity = TaskActivity(
        task_id = task_id,
        user_id = user_id,
        action = action
    )
    db.session.add(activity)

def generate_team_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
        existing_team = Team.query.filter_by(team_code=code).first()
        if not existing_team:
            return code
        
def create_team_for(events = None):
    current_user = db.session.get(User, session["user_id"])
    # events = Event.query.all()
    # Soon Hong: Changed to create teams for joined events
    events = [participation.event for participation in Participation.query.filter_by(user_id = session["user_id"]).all()] if events is None else events
    if request.method == "POST":
        name = request.form.get("name")
        roles = request.form.get("roles")
        motto = request.form.get("motto")
        project_idea = request.form.get("project_idea")
        event_id = request.form.get("event_id")
        max_members = int(request.form.get("max_members"))
        if max_members < 1 or max_members > 6:
            return "Team size must be between 1 and 6"
        new_team = Team(
            name = name,
            roles = roles,
            motto = motto,
            project_idea = project_idea,
            event_id = event_id,
            leader_id = session["user_id"],
            team_code = generate_team_code(),
            max_members = max_members
        )
        db.session.add(new_team)
        db.session.commit()
        # leader = TeamMember(
        #     team_id = new_team.id,
        #     user_id = session["user_id"],
        #     roles = "Leader"
        # )
        # db.session.add(leader)
        # db.session.commit()
        participation = Participation.query.filter_by(
            user_id = session["user_id"],
            event_id = event_id
        ).first()
        participation.team_id = new_team.id
        participation.roles = "Leader"
        db.session.add(participation)
        db.session.commit()
        return redirect(url_for("team_detail", team_id = new_team.id))
    return render_template("create_team.html", events = events, current_user = current_user)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

# Main routes
@app.route("/")
def home():
    return render_template("home.html", current_user = db.session.get(User, session["user_id"]) if session.get("user_id", None) else None)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered"
        hashed_password = generate_password_hash(password)
        session["temp_email"] = email
        session["temp_password"] = hashed_password
        send_otp(email, purpose = "register")
        return redirect(url_for("verify_register"))
    return render_template("register.html")

@app.route("/verify-register", methods=["GET", "POST"])
def verify_register():
    email = session.get("temp_email", None)
    if request.method == "POST":
        if verify_otp("register", "temp_email"):
            password = session.get("temp_password", None)
            user = User(email = email, 
                        password = password, 
                        is_verified = True, 
            )
            db.session.add(user)
            db.session.commit()
            session.pop("temp_email", None)
            session.pop("temp_password", None)
            return redirect(url_for("login"))    
        return "Invalid OTP"
    return render_template("otp_veri.html",  email = email)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            next = request.args.get("next")
            if next:
                return redirect(next)
            return redirect("/dashboard")
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    user_id = session.get("user_id")
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            user.last_seen = dt.datetime.now(dt.UTC).replace(tzinfo=None) - dt.timedelta(minutes=2)  # Set last seen to 2 minutes ago to mark as offline
            db.session.commit()
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    user = db.session.get(User, session["user_id"])
    # return f"Welcome {user.email} ---> ID: {user.id}"
    return redirect("/")

@app.route("/forget", methods=["GET", "POST"])
def forget():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if not user:
            return "User not found"
        session["reset_email"] = email
        send_otp(email, purpose = "reset")
        return redirect("/verify-reset")
    return render_template("forget_ps.html")

@app.route("/verify-reset", methods=["GET", "POST"])
def verify_reset():
    if request.method == "POST":
        if verify_otp("reset", "reset_email"):
            session["reset_verified"] = True
            return redirect("/reset-password")
        return "Invalid / Expired OTP"
    return render_template("otp_veri.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    user_id = session.get("user_id")
    if user_id:
        # Logged-in user
        user = db.session.get(User, user_id)
        if request.method == "POST":
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            if not check_password_hash(user.password, current_password):
                return "Incorrect current password"
            user.password = generate_password_hash(new_password)
            db.session.commit()
            return redirect(url_for("profile", user_id=user_id))
        # Show form with current password field
        return render_template("reset.html", logged_in=True)
    else:
        # Email reset
        if not session.get("reset_verified"):
            return "Not allowed"
        if request.method == "POST":
            new_password = request.form.get("new_password")
            email = session.get("reset_email")
            user = User.query.filter_by(email=email).first()
            user.password = generate_password_hash(new_password)
            db.session.commit()
            session.pop("reset_email", None)
            session.pop("reset_verified", None)
            return redirect(url_for("login"))
        # Show form without current password
        return render_template("reset.html", logged_in=False)

# By Soon Hong
@app.route("/profile/<user_id>", methods = ["GET", "POST"])
@login_required
def profile(user_id):
    profile_page = ProfileForm()
    user = db.session.get(User, user_id)
    if user is None:
        return "User not found"
    
    if profile_page.validate_on_submit():
        if user.id != session["user_id"]:
            return "Unauthorized", 403
        user.name = profile_page.username.data
        user.university = profile_page.university.data
        user.skills = profile_page.skills.data
        user.github_link = profile_page.github_link.data
        db.session.commit()
        new_email = profile_page.email.data

        if new_email != user.email:
            send_otp(new_email, purpose = "update_email")
            session["new_email"] = new_email
            return redirect(url_for("verify_update_email"))
        return redirect(url_for("profile", user_id=user_id))

    # team_member_subquery = select(TeamMember.team_id).where(TeamMember.user_id == user_id).subquery()
    # is_team_members_of = db.session.query(Team.event_id).join(team_member_subquery, Team.id == team_member_subquery.c.team_id).subquery()
    # events = db.session.execute(db.session.query(Event).join(is_team_members_of, is_team_members_of.c.event_id == Event.id)).scalars().all()
    events = list(map(lambda team_membership: team_membership.event, user.team_memberships))
    return render_template("profile.html", 
                           form = profile_page, 
                           user = user, 
                           current_user = db.session.get(User, session["user_id"]),
                           events = events
    )

@app.route("/reset_pwd")
@login_required
def reset_pwd():
    # For logged-in users, allow direct reset without OTP
    return redirect(url_for("reset_password"))

@app.route("/verify-update-email", methods=["GET", "POST"])
@login_required
def verify_update_email():
    new_email = session.get("new_email")
    if request.method == "POST":
        if verify_otp(purpose = "update_email", session_key = "new_email"):
            user = User.query.get(session.get("user_id"))
            user.email = new_email
            db.session.add(user)
            db.session.commit()
            session.pop("new_email")
            return redirect(url_for("profile", user_id = user.id))
        return "Invalid OTP"
    return render_template("otp_veri.html", email = new_email)

# wy - task management system ----------------------------------------------------------------------------
@app.route ("/team/<int:team_id>/tasks", methods = ["GET", "POST"])
@login_required
def tasks(team_id):
    team = db.session.get(Team, team_id)   
    form = TaskForm()
    # team_members = (db.session.query(User).join(TeamMember, TeamMember.user_id == User.id).filter(TeamMember.team_id == team.id).all())
    team_members = list(map(lambda member: member.user, team.members))
    form.assigned_to.choices = [(0, "No user selected")] + [(u.id, u.name or u.email) for u in team_members]
    if form.validate_on_submit():
        assigned_user_id = form.assigned_to.data
        if assigned_user_id == 0:
            assigned_user_id = session["user_id"]  
        task = Task(title = form.title.data, 
                    team_id = team.id,
                    assigned_to = assigned_user_id, 
                    priority = form.priority.data, 
                    description = form.description.data, 
                    deadline = dt.datetime.combine(form.deadline.data, dt.datetime.min.time()), 
                    status = form.status.data, 
                    is_done = (form.status.data == "Complete"))
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("tasks", team_id = team.id))
    status_filter = request.args.get("status", "all")
    # nx
    search_query = request.args.get("searchtasks", "").strip()
    # wy
    now = dt.datetime.now()
    query = Task.query.filter_by(team_id = team.id)
    if status_filter != "all":
        query = query.filter(Task.status == status_filter)
    # nx
    if search_query:
        query = query.filter(Task.title.ilike(f"%{search_query}%") | Task.description.ilike(f"%{search_query}%"))
    # wy
    status_order = case(((Task.is_done == False) & (Task.deadline < now) & (Task.status.in_(["To Do", "In Progress"])), 0), (Task.status == "Wishlist", 1), (Task.status == "To Do", 2), (Task.status == "In Progress", 3), (Task.status == "In Review", 4), (Task.status == "Complete", 5), else_=6)   
    priority_order = case((Task.priority.in_(["High","high"]), 0), (Task.priority.in_(["Medium","medium"]), 1), (Task.priority.in_(["Low","low"]), 2), else_=3)
    query = query.order_by(status_order, priority_order, Task.deadline.asc())
    # tasks = query.all()
        # nx
    tasks_results = query.all()
    if request.headers.get("HX-Request"):
        return render_template("partials/task_list.html", tasks = tasks_results, datetime = dt)
    # wy
    return render_template("tasks.html", form = form, tasks = tasks_results, datetime = dt, status_filter = status_filter, current_user = db.session.get(User, session["user_id"]), team = team)

@app.route("/task/<int:id>/toggle", methods = ["POST"])
@login_required
def toggle_task(id):
    task = db.session.get(Task, id)
    if task is None:
        return "Task not found"
    task.is_done = not task.is_done
    if task.is_done:
        task.status = "Complete"
    else:
        task.status = "To Do"
    db.session.commit()
    return redirect(url_for("tasks", team_id = task.team_id))

@app.route("/task/<int:id>/delete", methods = ["POST"])
@login_required
def delete_task(id):
    task = db.session.get(Task, id)
    if task is None:
        return "Task not found"
    TaskActivity.query.filter_by(task_id = id).delete()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("tasks", team_id = task.team_id))

@app.route("/task/<int:id>/autosave", methods = ["POST"])
@login_required
def autosave_task(id):
    task = db.session.get(Task, id)
    if not task:
        return "Task not found"
    field = request.form.get("field")
    value = request.form.get("value")
    old_value = None
    new_value = None
    if field == "assigned_to":
        old_user = db.session.get(User, task.assigned_to)
        new_user = db.session.get(User, int(value)) if value else None
        old_value = old_user.name if old_user else "No assignee"
        new_value = new_user.name if new_user else "No assignee"
        task.assigned_to = int(value) if value else None
    elif field == "deadline":
        old_value = task.deadline.strftime("%d %b %Y") if task.deadline else "No deadline"
        if value:
            task.deadline = dt.datetime.strptime(value, "%Y-%m-%d")
            new_value = task.deadline.strftime("%d %b %Y")
        else:
            task.deadline = None
            new_value = "No deadline"
    else:
        old_value = getattr(task, field, None)
        new_value = value
        setattr(task, field, value)
        if field == "status":
            task.is_done = (value == "Complete")
    if str(old_value) != str(new_value):
        add_task_activity(
            task.id,
            f"changed {field} from '{old_value}' to '{new_value}'"
        )
    db.session.commit()
    return "Saved"

@app.route("/team/<int:team_id>/task/<int:id>/details", methods = ["GET", "POST"])
@login_required
def task_details(team_id, id):
    task = db.session.get(Task, id)
    if not task:
        return "Task not found"
    # team_members = (db.session.query(User).join(TeamMember, TeamMember.user_id == User.id)
    #                 .filter(TeamMember.team_id == task.team_id).all())
    team_members = list(map(lambda member: member.user, task.team.members))
    subtasks = Subtask.query.filter_by(task_id = id).all()
    if task is None:
        return "Task not found"
    today = dt.date.today()
    for subtask in subtasks:
        if not subtask.is_done and subtask.deadline and subtask.deadline.date() < today:
            subtask.is_overdue = True
        else:
            subtask.is_overdue = False
    if request.method == "POST":
        task.title = request.form.get("title")
        task.description = request.form.get("description")
        task.assigned_to = int(request.form.get("assigned_to"))
        task.priority = request.form.get("priority")
        task.deadline = dt.datetime.strptime(request.form.get("deadline"), "%Y-%m-%d")
        task.status = request.form.get("status")
        task.is_done = task.status == "Complete"
        db.session.commit()
        return redirect(url_for("tasks", team_id = task.team_id))
    return render_template("task_details.html", 
                           task = task,
                           users = team_members,
                           subtasks = subtasks, 
                           team_id = team_id)

@app.route("/team/<int:team_id>/task/<int:id>/add_subtask", methods = ["POST"])
@login_required
def add_subtask(team_id, id):
    title = request.form.get("title")
    assigned_to = request.form.get("assigned_to")
    status = request.form.get("status")
    deadline = request.form.get("deadline")
    priority = request.form.get("priority")
    new_subtask = Subtask(title = title, 
                          assigned_to = int(assigned_to) if assigned_to else None, 
                          status = status, 
                          priority = priority, 
                          deadline = dt.datetime.strptime(deadline, "%Y-%m-%d") 
                          if deadline else None, task_id = id)
    db.session.add(new_subtask)
    db.session.commit()
    return redirect(url_for("task_details", team_id = team_id, id = id))

@app.route("/team/<int:team_id>/subtask/<int:sub_id>/edit", methods = ["POST"])
@login_required
def edit_subtask(team_id, sub_id):
    sub = db.session.get(Subtask, sub_id)
    if not sub:
        return "Subtask not found"
    sub.title = request.form.get("title", sub.title)
    sub.status = request.form.get("status", sub.status)
    sub.priority = request.form.get("priority", sub.priority)
    deadline = request.form.get("deadline")
    if deadline:
        try:
            sub.deadline = dt.datetime.strptime(deadline, "%Y-%m-%d")
        except:
            return "Invalid date format"
    db.session.commit()
    return redirect(url_for("task_details", team_id = team_id, id = sub.task_id))

@app.route("/team/<int:team_id>/subtask/<int:sub_id>/toggle", methods=["POST"])
@login_required
def toggle_subtask(team_id, sub_id):
    subtask = Subtask.query.get(sub_id)
    subtask.is_done = not subtask.is_done
    db.session.commit()
    return redirect(url_for("task_details", team_id = team_id, id = subtask.task_id))
# --------------------------------------------------------------------------------------------------------
# wy - team formation system -----------------------------------------------------------------------------
@app.route("/teams")
@login_required
def teams():
    # nx
    searchteams = request.args.get("searchteams", "").strip()

    # all_teams = Team.query.all()
    query = Team.query
    if searchteams:
        query = query.filter(Team.name.ilike(f"%{searchteams}%"))
    all_teams = query.all()
    # wy
    current_user = db.session.get(User, session["user_id"])
    # joined_team_ids = [
    #     member.team_id
    #     for member in TeamMember.query.filter_by(user_id = session["user_id"]).all()]
    joined_team_ids = [participation.team_id for participation in Participation.query.filter_by(user_id = session["user_id"]).filter(Participation.team_id != None).all()]
    # nx
    if request.headers.get("HX-Request"):
        return render_template("/partials/team_list.html", teams = all_teams, current_user = current_user, joined_team_ids = joined_team_ids)
    # wy
    return render_template("teams.html",
                           teams = all_teams,
                           current_user = current_user,
                           joined_team_ids = joined_team_ids)

@app.route("/team/create", methods = ["GET", "POST"])
@login_required
def create_team():
    return create_team_for()

@app.route("/team/<int:team_id>/request", methods = ["POST"])
@login_required
def request_join_team(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    # existing_member = Participation.query.filter_by(team_id = team.id, user_id = session["user_id"]).first()
    existing_member = Participation.query.filter_by(team_id = team.id, user_id = session["user_id"]).first()
    if existing_member:
        return redirect(url_for("team_detail", team_id = team.id))
    # SH: handle the case where the user request to join a team but has not enrolled in the event
    joined_event = Participation.query.filter_by(user_id = session["user_id"], event_id = team.event_id).first()
    if not joined_event:
        redirect_url = url_for("event_detail", event_id = team.event_id)
        response = make_response()
        response.headers["HX-Redirect"] = redirect_url
        return response
    existing_request = TeamJoinRequest.query.filter_by(team_id = team.id, 
                                                       user_id = session["user_id"],
                                                       status = "Pending").first()
    if existing_request:
        if request.headers.get("HX-Request"):
            return  """ <div class="team-actions" id="join-action"> 
                    <button disabled>Request Sent</button>
                    </div>"""
        return "Request already sent"
    # if TeamMember.query.filter_by(team_id = team.id).count() >= team.max_members:
    if Participation.query.filter_by(team_id = team.id).count() >= team.max_members:
        return "This team is already full"
    
    join_request = TeamJoinRequest(team_id = team.id, user_id = session["user_id"], status = "Pending")
    db.session.add(join_request)
    db.session.commit()
    # return redirect(url_for("team_detail", team_id = team.id))
    return """ <div class = "team-actions" id = "join-action">
            <button disabled>Request Sent</button>
            </div>"""

@app.route("/team/<int:team_id>")
@login_required
def team_detail(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    current_user = db.session.get(User, session["user_id"])
    is_member = Participation.query.filter_by(team_id = team.id,
                                           user_id = session["user_id"]).first() is not None
    participation = Participation.query.filter_by(user_id = session["user_id"]).first()
    member_of_other_team = False if not participation else participation.team_id is not None
    pending_requests = []
    if team.leader_id == session["user_id"]:
        pending_requests = TeamJoinRequest.query.filter_by(team_id = team.id, status = "Pending").all()
    invite_link = url_for("team_detail", team_id = team.id, _external = True)
    qr = qrcode.make(invite_link)
    buffer = io.BytesIO()
    qr.save(buffer, format = "PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    qr_code = f"data:image/png;base64, {qr_base64}"
    existing_request = TeamJoinRequest.query.filter_by(team_id = team.id,
                                                       user_id = session["user_id"],
                                                       status = "Pending").first()
    return render_template(
                        "team_detail.html",
                        team = team,
                        current_user = current_user,
                        is_member = is_member,
                        pending_requests = pending_requests,
                        invite_link = invite_link,
                        qr_code = qr_code,
                        existing_request = existing_request,
                        member_of_other_team = member_of_other_team
    )
    
@app.route("/team/request/<int:request_id>/approve", methods = ["POST"])
@login_required
def approve_join_request(request_id):
    join_request = db.session.get(TeamJoinRequest, request_id)
    if not join_request:
        return "Request not found"
    team = join_request.team
    if team.leader_id != session["user_id"]:
        return "Only leader can approve requests"
    # member_count = TeamMember.query.filter_by(team_id = team.id).count()
    member_count = Participation.query.filter_by(team_id = team.id).count()
    if member_count >= team.max_members:
        return "This team is already full"
    # new_member = TeamMember(team_id = team.id, user_id = join_request.user_id, roles = "Member")
    print(request_id, join_request.user_id, team.event_id)
    participation = Participation.query.filter_by(user_id = join_request.user_id, event_id = team.event_id).first()
    if participation.team_id is not None:
        return "User already in a team"
    participation.team_id = team.id 
    join_request.status = "Approved"
    # db.session.add(new_member)
    db.session.add(participation)
    db.session.add(join_request)
    db.session.commit()
    # return redirect(url_for("team_detail", team_id = team.id))
    return "Approved"

@app.route("/team/request/<int:request_id>/reject", methods = ["POST"])
@login_required
def reject_join_request(request_id):
    join_request = db.session.get(TeamJoinRequest, request_id)
    if not join_request:
        return "Request not found"
    team = join_request.team
    if team.leader_id != session["user_id"]:
        return "Only leader can reject requests"
    join_request.status = "Rejected"
    db.session.commit()
    # return redirect(url_for("team_detail", team_id = team.id))
    return "Rejected"

@app.route("/team/<int:team_id>/change-leader", methods = ["POST"])
@login_required
def change_leader(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    if team.leader_id != session["user_id"]:
        return "Only leader can change leader"
    new_leader_id = int(request.form.get("new_leader_id"))
    # new_leader_member = TeamMember.query.filter_by(team_id = team.id, user_id = new_leader_id).first()
    new_leader_member = Participation.query.filter_by(team_id = team.id, user_id = new_leader_id).first()
    if not new_leader_member:
        return "New leader must be a team member"
    # old_leader_member = TeamMember.query.filter_by(team_id = team.id, 
    #                                                user_id = session["user_id"]).first()
    old_leader_member = Participation.query.filter_by(team_id = team.id, 
                                                   user_id = session["user_id"]).first()
    if old_leader_member:
        old_leader_member.roles = "Member"
    new_leader_member.roles = "Leader"
    team.leader_id = new_leader_id
    db.session.commit()
    return redirect(url_for("team_detail", team_id = team.id))

@app.route("/team/<int:team_id>/leave", methods = ["POST"])
@login_required
def leave_team(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    if team.leader_id == session["user_id"]:
        return "You are the leader. Please transfer leader position before leaving."
    # member = TeamMember.query.filter_by(team_id=team.id, user_id = session["user_id"]).first()
    member = Participation.query.filter_by(team_id=team.id, user_id = session["user_id"]).first()
    if not member:
        return "You are not in this team"
    member.team_id = None
    # db.session.delete(member)
    db.session.add(member)
    db.session.commit()
    return redirect(url_for("teams"))

@app.route("/team/<int:team_id>/delete", methods=["POST"])
@login_required
def delete_team(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    if team.leader_id != session["user_id"]:
        return "Only leader can delete this team"
    TeamJoinRequest.query.filter_by(team_id = team.id).delete()
    # TeamMember.query.filter_by(team_id = team.id).delete()
    update_participation = update(Participation).where(Participation.team_id == team_id).values(team_id = None)
    db.session.execute(update_participation)
    db.session.commit()
    tasks = Task.query.filter_by(team_id = team.id).all()
    for task in tasks:
        TaskActivity.query.filter_by(task_id = task.id).delete()
        Subtask.query.filter_by(task_id = task.id).delete()
        db.session.delete(task)
    db.session.delete(team)
    db.session.commit()
    return redirect(url_for("teams"))

@app.route("/team/<int:team_id>/remove/<int:user_id>", methods = ["POST"])
@login_required
def remove_member(team_id, user_id):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    if team.leader_id != session["user_id"]:
        return "Only leader can remove members"
    if user_id == team.leader_id:
        return "Cannot remove the leader"
    # member = TeamMember.query.filter_by(team_id = team.id, user_id = user_id).first()
    member = Participation.query.filter_by(team_id = team.id, user_id = user_id).first()
    if member:
        # db.session.delete(member)
        # db.session.commit()
        member.team_id = None
        db.session.add(member)
        db.session.commit()
    # return redirect(url_for("team_detail", team_id = team.id))
    # SH: 这个return "" 是对的， 那个member的div就不见了
    return ""

@app.route("/team/<int:team_id>/autosave", methods = ["POST"])
@login_required
def autosave_team(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    if team.leader_id != session["user_id"]:
        return "Unauthorized"
    field = request.form.get("field")
    value = request.form.get("value")
    if field == "name":
        team.name = value
    elif field == "motto":
        team.motto = value
    elif field == "roles":
        team.roles = value
    elif field == "project_idea":
        team.project_idea = value
    elif field == "max_members":
        value = int(value)
        if value < len(team.members):
            return "Max members cannot be less than current members"
        if value < 1 or value > 6:
            return "Team size must be between 1 and 6"
        team.max_members = value
    else:
        return "Invalid field"
    db.session.commit()
    return "Saved"

@app.route("/team/create/<int:event_id>", methods = ["GET", "POST"])
@login_required
def create_team_for_event(event_id):
    return create_team_for(events= [db.session.get(Event, event_id)])

#------------------------------------------------------------------------------------------------------
# nx - chat system
@app.route("/chat")
@login_required
def chat_home():
    current_user_id = session.get("user_id")
    # find all msg i send or receive
    all_my_messages = Message.query.filter((Message.sender_id == current_user_id) | (Message.receiver_id == current_user_id)).all()
    # find all user ids i have interacted
    interacted_user_ids = set()
    for msg in all_my_messages:
        if msg.sender_id != current_user_id:
            interacted_user_ids.add(msg.sender_id)
        if msg.receiver_id != current_user_id:
            interacted_user_ids.add(msg.receiver_id)
    # find hidden user
    hidden_relationships = ChatVisibility.query.filter_by(user_id = current_user_id, is_hidden = True).all()
    hidden_user_ids = {rel.other_user_id for rel in hidden_relationships}
    # find final user ids after excluding hidden users
    final_user_ids = interacted_user_ids - hidden_user_ids
    # show users i have chatted with and not hidden, with whom I can click to see the chat history
    users = User.query.filter(User.id.in_(final_user_ids)).all() if final_user_ids else []
    hidden_user= User.query.filter(User.id.in_(hidden_user_ids)).all() if hidden_user_ids else []

    return render_template("chat_home.html", users = users, hidden_user_ids = hidden_user_ids, hidden_user = hidden_user)

@app.route("/chat/<int:user_id>")
@login_required
def chat(user_id):
    current_user_id = session.get("user_id")
    current_user = db.session.get(User, current_user_id)
    other_user = db.session.get(User, user_id)
    # add visibility filter: only show messages after the time when I choose to see this chat (handle the case where I clear chat but not delete, then new msg comes in, I should be able to see the new msg but not the old msg before clear)
    visibility = ChatVisibility.query.filter_by(user_id = current_user_id, other_user_id = user_id).first()
    visible_time = visibility.visible_since if visibility else dt.datetime.min
    messages = Message.query.filter((((Message.sender_id == current_user_id) & (Message.receiver_id == user_id)) | 
                                    ((Message.sender_id == user_id) & (Message.receiver_id == current_user_id))) & (Message.timestamp >= visible_time)
    ).order_by(Message.timestamp.asc()).all()

    return render_template("chat.html",messages = messages, other_user = other_user, current_user_id=current_user_id, current_user = current_user)

@app.route("/hide_user/<int:user_id>")
@login_required
def hide_user(user_id):
    current_user_id = session.get("user_id")
    visibility = ChatVisibility.query.filter_by(user_id = current_user_id, other_user_id = user_id).first()
    if not visibility:
        visibility = ChatVisibility(user_id = current_user_id, other_user_id = user_id, is_hidden = True)
        db.session.add(visibility)
        visibility.is_hidden = True
    else:
        visibility.is_hidden = not visibility.is_hidden
    db.session.commit()
    return redirect(url_for("chat_home"))
    
@app.route("/send_message", methods=["POST"])
@login_required
def send_message():
    # get msg and sender_id
    content = request.form["message"]
    sender_id = session.get("user_id")
    receiver_id = request.form["user_id"]
    other_user = db.session.get(User, receiver_id)
    # receiver_id = 2 if sender_id == 1 else 1  #user1/2互发消息
    new_message = Message(message = content, sender_id = sender_id, receiver_id = receiver_id) #timestamp会自动生成/存数据库
    db.session.add(new_message)
    db.session.commit()

    visibility = ChatVisibility.query.filter_by(user_id = sender_id, other_user_id = receiver_id).first()
    visible_time = visibility.visible_since if visibility else dt.datetime.min

    # return redirect(url_for("chat", user_id=sender_id)) #发完消息回聊天界面，user_id不变
    # messages = Message.query.filter(((Message.sender_id == sender_id) & (Message.deleted_by_sender == False)) | ((Message.receiver_id == sender_id) & (Message.deleted_by_receiver == False))).order_by(Message.timestamp.asc()).all()
    messages = Message.query.filter((((Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)) | ((Message.sender_id == receiver_id) & (Message.receiver_id == sender_id))) & (Message.timestamp >= visible_time)).order_by(Message.timestamp.asc()).all()
    return render_template("message.html", messages = messages, current_user_id = sender_id, other_user = other_user) #只返回新消息，前端htmx负责更新页面
    
@app.route("/clear/<int:user_id>")
@login_required
def clear_messages(user_id):
    current_user_id = session.get("user_id")
    # update visibility to now, so that when I query messages I only see messages after I clear, the old messages before clear are still in database but not visible (soft delete)
    my_visibility = ChatVisibility.query.filter_by(user_id = current_user_id, other_user_id = user_id).first()
    if not my_visibility:
        my_visibility = ChatVisibility(user_id = current_user_id, other_user_id = user_id)
        db.session.add(my_visibility)
    my_visibility.visible_since = dt.datetime.now()
    db.session.commit()
    their_visibility = ChatVisibility.query.filter_by(user_id = user_id, other_user_id = current_user_id).first()
    if their_visibility:
        earliest_clear_time = min(my_visibility.visible_since, their_visibility.visible_since)
        expired_messages = Message.query.filter(((Message.sender_id == current_user_id) & (Message.receiver_id == user_id) | (Message.sender_id == user_id) & (Message.receiver_id == current_user_id)) & (Message.timestamp < earliest_clear_time)).all()
        for message in expired_messages:
            db.session.delete(message) #双方都clear了才真正从数据库删除
    # find all my msg and 标记为deleted for sender/receiver depend on my身份，真正删除在数据库里保留但不展示(soft delete)
    # messages = Message.query.filter(((Message.sender_id == current_user_id) & (Message.receiver_id == user_id)) | ((Message.sender_id == user_id) & (Message.receiver_id == current_user_id))).all()
    # for message in messages:
    #     if message.sender_id == current_user_id:
    #         message.deleted_by_sender = True
    #     if message.receiver_id == current_user_id:
    #         message.deleted_by_receiver = True
    #     if message.deleted_by_sender and message.deleted_by_receiver:
    #         db.session.delete(message) #双方都删除了才真正从数据库删除
        db.session.commit()
    return redirect(url_for("chat", user_id=user_id))
    
@app.route("/message")
@login_required
def get_message():
    current_user_id = session.get("user_id")
    other_user_id = request.args.get("user_id")
    user = db.session.get(User, current_user_id)
    other_user = db.session.get(User, other_user_id)
    if user:
        user.last_seen = dt.datetime.now(dt.UTC).replace(tzinfo=None)
    # find unread msg
    unread_messages = Message.query.filter_by(receiver_id = current_user_id, sender_id = other_user_id, is_read = False).all()
    for message in unread_messages:
        # seen
        message.is_read = True
    db.session.commit()
    visibility = ChatVisibility.query.filter_by(user_id = current_user_id, other_user_id = other_user_id).first()
    if visibility and visibility.is_hidden:
        visibility.is_hidden = False
        db.session.commit()
    visible_time = visibility.visible_since if visibility else dt.datetime.min
    # receiver_id = 2 if current_user_id == 1 else 1
    messages = Message.query.filter((((Message.sender_id == current_user_id) & (Message.receiver_id == other_user_id)) | ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user_id))) & (Message.timestamp >= visible_time)).order_by(Message.timestamp.asc()).all()
    return render_template("message.html", messages = messages, current_user_id = current_user_id, other_user = other_user)

@app.route("/delete_message/<int:message_id>")
@login_required
def delete_message(message_id):

    current_user_id = session.get("user_id")
    message = db.session.get(Message, message_id)

    # if not message:
    #     return redirect(request.referrer)
    if message and message.sender_id == current_user_id:
            message.is_deleted = True
            db.session.commit()
    #         other_user_id = message.receiver_id
    #     else:
    #         other_user_id = message.receiver_id if message.sender_id == current_user_id else message.sender_id
    # else:
    #     return "", 404

    
    # other_user_id = message.receiver_id if message.sender_id == current_user_id else message.sender_id

    # if message.sender_id == current_user_id:
    #     message.deleted_by_sender = True
    # if message.receiver_id == current_user_id:
    #     message.deleted_by_receiver = True
    # if message.deleted_by_sender and message.deleted_by_receiver:
    #     db.session.delete(message)
    # if message.sender_id == current_user_id:
    #     message.is_deleted = True
    #     db.session.commit()

    if request.headers.get("HX-Request"):
        now_str = dt.datetime.now().strftime("%H:%M")
        # other_user_id = message.receiver_id if message.sender_id == current_user_id else message.sender_id
        # other_user = db.session.get(User, other_user_id)
        # visibility = ChatVisibility.query.filter_by(user_id = current_user_id, other_user_id = other_user_id).first()
        # visible_time = visibility.visible_since if visibility else dt.datetime.min
        # messages = Message.query.filter((((Message.sender_id == current_user_id) & (Message.receiver_id == other_user_id)) | ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user_id))) & (Message.timestamp >= visible_time)).order_by(Message.timestamp.asc()).all()
        return render_template("deleted_hint.html", now_str = now_str) #局部更新，前端htmx负责把这个提示替换掉被删除的消息

    return redirect(request.referrer)
# wy - project page -----------------------------------------------------------------------------------
@app.route("/team/<int:team_id>/project")
@login_required
def project_page(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    event = db.session.get(Event, team.event_id)
    current_user = db.session.get(User, session["user_id"])
    is_member = Participation.query.filter_by(team_id = team.id,
                                           user_id = session["user_id"]).first() is not None
    can_edit = is_member
    project = Project.query.filter_by(team_id = team.id).first()
    if not project:
        project = Project(team_id = team.id, title = f"{team.name} Project")
        db.session.add(project)
        db.session.commit()
    screenshots = []
    if project.screenshots_link:
        try:
            screenshots = json.loads(project.screenshots_link)
        except:
            screenshots = []
    return render_template("project_page.html",
                           team = team,
                           project = project,
                           current_user = current_user, 
                           can_edit = can_edit,
                           event = event,
                           screenshots = screenshots)

@app.route("/team/<int:team_id>/project/autosave", methods = ["POST"])
@login_required
def autosave_project(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    is_member = Participation.query.filter_by(team_id = team.id, user_id = session["user_id"]).first()
    if not is_member:
        return "Unauthorized"
    project = Project.query.filter_by(team_id = team.id).first()
    if not project:
        project = Project(team_id = team.id, title = f"{team.name} Project")
        db.session.add(project)
        db.session.commit()
    field = request.form.get("field")
    value = request.form.get("value")
    if field == "title":
        project.title = value
    elif field == "description":
        project.description = value
    elif field == "tech_stack":
        project.tech_stack = value
    elif field == "demo_link":
        project.demo_link = value
    elif field == "github_link":
        project.github_link = value
    elif field == "contributions":
        project.contributions = value
    else:
        return "Invalid field"
    db.session.commit()
    return "Saved"

@app.route("/team/<int:team_id>/project/upload_screenshot", methods = ["POST"])
@login_required
def upload_screenshot(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    is_member = Participation.query.filter_by(team_id = team.id, user_id = session["user_id"]).first()
    if not is_member:
        return "Unauthorized"
    if "screenshot" not in request.files:
        return "No file uploaded"
    file = request.files["screenshot"]
    if file.filename == "":
        return "No file selected"
    allowed_extensions = {"png", "jpg", "jpeg", "webp", "gif"}
    file_ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
    if file_ext not in allowed_extensions:
        return "Invalid file type. Allowed: png, jpg, jpeg, webp, gif"
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = secure_filename(f"team_{team_id}_{timestamp}_{file.filename}") #create unique filename 
    upload_folder = os.path.join("app", "static", "uploads", "projects")
    os.makedirs(upload_folder, exist_ok = True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    project = Project.query.filter_by(team_id = team.id).first()
    if not project:
        project = Project(team_id = team.id, title = f"{team.name} Project")
        db.session.add(project)
    screenshot_url = f"/static/uploads/projects/{filename}"
    if project.screenshots_link:
        try:
            screenshots = json.loads(project.screenshots_link)
        except:
            screenshots = []
    else:
        screenshots = []
    screenshots.append(screenshot_url)
    project.screenshots_link = json.dumps(screenshots)
    db.session.commit()
    return redirect(url_for('project_page', team_id = team.id))

@app.route("/team/<int:team_id>/project/delete_screenshot/<int:screenshot_index>", methods = ["POST"])
@login_required
def delete_screenshot(team_id, screenshot_index):
    team = db.session.get(Team, team_id)
    if not team:
        return "Team not found"
    is_member = Participation.query.filter_by(team_id = team.id, user_id = session["user_id"]).first()
    if not is_member:
        return "Unauthorized"
    project = Project.query.filter_by(team_id = team.id).first()
    if not project or not project.screenshots_link:
        return redirect(url_for('project_page', team_id = team.id))
    try:
        screenshots = json.loads(project.screenshots_link)
    except:
        screenshots = []
    if 0 <= screenshot_index < len(screenshots):
        file_path = os.path.join('app', screenshots[screenshot_index].lstrip('/'))
        if os.path.exists(file_path):
            os.remove(file_path)
        screenshots.pop(screenshot_index)
        project.screenshots_link = json.dumps(screenshots) if screenshots else None
        db.session.commit()
    return redirect(url_for('project_page', team_id = team.id))