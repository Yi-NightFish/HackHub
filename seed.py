from datetime import datetime

from app import app, db
from app.models import User, Event, Team, TeamMember
from werkzeug.security import generate_password_hash

with app.app_context():
    db.drop_all()  # Drop all tables to start fresh
    db.create_all()  # Create tables if they don't exist

    # Create users
    user1 = User(
        email="hi@gmail.com",
        password=generate_password_hash("123"),
        is_verified=True,
        name="hi",
        university="university A",
        skills="Python, Flask",
        github_link="https://github.com/hi"
    )
    user2 = User(
        email="bye@gmail.com",
        password=generate_password_hash("456"),
        is_verified=False,
        name="bye",
        university="university B",
        skills="JavaScript, HTML",
        github_link="https://github.com/bye"
    )
    me = User(
        email="tanwanyi007@gmail.com",
        password=generate_password_hash("789"),
        is_verified=True,
        name="tanwanyi007",
        university="university C",
        skills="Python, SQL",
        github_link="https://github.com/tanwanyi007"
    )
    db.session.add_all([user1, user2, me])
    db.session.commit()

    # Create events
    event1 = Event(
        title="HackHub Launch Hackathon",
        date=datetime.now(),
        description="A beginner-friendly hackathon to celebrate the HackHub launch.",
        organizer_id=me.id,
        status="open"
    )
    event2 = Event(
        title="Spring Innovation Challenge",
        date=datetime.now(),
        description="A team-based event for solving real-world problems.",
        organizer_id=user1.id,
        status="open"
    )
    event3 = Event(
        title="AI Workshop Weekend",
        date=datetime.now(),
        description="An educational event with workshops and demos.",
        organizer_id=user1.id,
        status="open"
    )
    db.session.add_all([event1, event2, event3])
    db.session.commit()

    # Create teams for events
    team1 = Team(
        name="Team Alpha",
        event_id=event1.id,
        team_code="ALPHA123",
        max_members=5
    )
    team2 = Team(
        name="Team Beta",
        event_id=event2.id,
        team_code="BETA123",
        max_members=5
    )
    team3 = Team(
        name="Team Gamma",
        event_id=event3.id,
        team_code="GAMMA123",
        max_members=5
    )
    db.session.add_all([team1, team2, team3])
    db.session.commit()

    # Simulate users joining multiple events via team memberships
    membership1 = TeamMember(team_id=team1.id, user_id=me.id)
    membership2 = TeamMember(team_id=team2.id, user_id=me.id)
    membership3 = TeamMember(team_id=team3.id, user_id=me.id)
    membership4 = TeamMember(team_id=team2.id, user_id=user1.id)
    membership5 = TeamMember(team_id=team1.id, user_id=user2.id)
    db.session.add_all([membership1, membership2, membership3, membership4, membership5])
    db.session.commit()

    print("Seeded successfully")
    print(f"User {me.email} joined events: {event1.title}, {event2.title}, {event3.title}")
    print(f"User {user1.email} joined event: {event2.title}")
    print(f"User {user2.email} joined event: {event1.title}")