from flask import render_template, request, session, redirect, url_for
from app import app, db
from app.models import Announcement, AnnouncementRead, Event, Participation, User
from app.routes import login_required
import datetime as dt


def get_user_announcements(user_id, mark_as_read=False):
    announcements = (
        Announcement.query.join(Event, Announcement.event_id == Event.id)
        .join(Participation, Participation.event_id == Event.id)
        .filter(Participation.user_id == user_id, Event.organizer_id != user_id)
        .order_by(Announcement.date_posted.desc(), Announcement.id.desc())
        .all()
    )

    result = []
    for announcement in announcements:
        is_read = (
            db.session.query(AnnouncementRead.id)
            .filter_by(user_id=user_id, announcement_id=announcement.id)
            .first() is not None
        )
        result.append({"announcement": announcement, "is_read": is_read})

    if mark_as_read:
        for entry in result:
            if not entry["is_read"]:
                db.session.add(AnnouncementRead(user_id=user_id, announcement_id=entry["announcement"].id))
                entry["is_read"] = True
        db.session.commit()

    return result


def get_unread_announcement_count(user_id):
    return sum(1 for entry in get_user_announcements(user_id) if not entry["is_read"])


@app.context_processor
def inject_announcement_context():
    current_user = None
    announcement_count = 0
    if session.get("user_id"):
        current_user = db.session.get(User, session["user_id"])
        if current_user:
            announcement_count = get_unread_announcement_count(current_user.id)
    return {
        "current_user": current_user,
        "announcement_count": announcement_count,
    }


@app.route("/announcements")
@login_required
def announcements():
    current_user = db.session.get(User, session["user_id"])
    announcements_list = get_user_announcements(current_user.id, mark_as_read=True)
    return render_template(
        "announcements.html",
        current_user=current_user,
        announcements=announcements_list,
    )


@app.route("/event/<int:event_id>/announcement", methods=["POST"])
@login_required
def create_event_announcement(event_id):
    event = db.session.get(Event, event_id)
    current_user = db.session.get(User, session["user_id"])

    if not event:
        return "Event not found", 404

    if event.organizer_id != current_user.id:
        return "Only the event organizer can post announcements", 403

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not content:
        return "Title and content are required", 400

    announcement = Announcement(
        event_id=event.id,
        title=title,
        content=content,
        created_by=current_user.id,
        date_posted=dt.datetime.now(dt.UTC),
    )
    db.session.add(announcement)
    db.session.commit()

    next_url = request.form.get("next") or url_for("event_detail", event_id=event.id, tab="overview")
    return redirect(next_url)
