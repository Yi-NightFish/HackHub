from datetime import datetime

from app import app, db
from app.models import User, Event, Team, TeamMember
from werkzeug.security import generate_password_hash

with app.app_context():
    # Clear existing data (optional - comment out if you want to preserve data)
    db.drop_all()
    db.create_all()
    db.session.commit()

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
    user3 = User(
        email="bailan_jer@gmail.com",
        password=generate_password_hash("789"),
        is_verified=True,
        name="bailan_jer",
        university="university C",
        skills="Python, SQL",
        github_link="https://github.com/bailan_jer"
    )

    user4 = User(
        email="yi07@gmail.com",
        password=generate_password_hash("789"),
        is_verified=True,
        name = "yi"
    )

    user5 = User(
        email="xin@gmail.com",
        password=generate_password_hash("789"),
        is_verified=True,
        name="xin"
    )

    db.session.add_all([user1, user2, user3, user4, user5])
    db.session.commit()

    # Create events
    event1 = Event(
        title="HackHub Launch Hackathon",
        date=datetime.now(),
        description="A beginner-friendly hackathon to celebrate the HackHub launch.",
        organizer_id=user3.id,
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
    membership1 = TeamMember(team_id=team1.id, user_id=user3.id)
    membership2 = TeamMember(team_id=team2.id, user_id=user3.id)
    membership3 = TeamMember(team_id=team3.id, user_id=user3.id)
    membership4 = TeamMember(team_id=team2.id, user_id=user1.id)
    membership5 = TeamMember(team_id=team1.id, user_id=user2.id)
    db.session.add_all([membership1, membership2, membership3, membership4, membership5])
    db.session.commit()

    print("Seeded successfully")