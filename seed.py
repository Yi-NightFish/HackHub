from datetime import datetime, timedelta
import random

from app import app, db
from app.models import User, Event, Team, TeamMember, Task, Announcement, Message, Dashboard
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

    # Create events with varied statuses for UI testing
    event1 = Event(
        title="HackHub Launch Hackathon",
        date=datetime.now(),
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=2),
        deadline=datetime.now() - timedelta(days=7),
        description="A beginner-friendly hackathon to celebrate the HackHub launch.",
        organizer_id=user3.id,
        # status="open"
    )
    event2 = Event(
        title="Spring Innovation Challenge",
        date=datetime.now(),
        start_time=datetime.now(),
        end_time=datetime.now() - timedelta(hours=3),
        deadline=datetime.now() - timedelta(days=10),
        description="A team-based event for solving real-world problems.",
        organizer_id=user1.id,
        # status="completed"
    )
    event3 = Event(
        title="AI Workshop Weekend",
        date=datetime.now(),
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=4),
        deadline=datetime.now() - timedelta(days=5),
        description="An educational event with workshops and demos.",
        organizer_id=user1.id,
        # status="cancelled"
    )
    event4 = Event(
        title="Summer Sprint Hack",
        date=datetime.now(),
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        deadline=datetime.now() - timedelta(days=3),
        description="A fast-paced event for prototyping new apps.",
        organizer_id=user4.id,
        # status="completed"
    )
    event5 = Event(
        title="Open Source Collaboration Day",
        date=datetime.now(),
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=5),
        deadline=datetime.now() - timedelta(days=14),
        description="A community event for contributing to open source projects.",
        organizer_id=user5.id,
        # status="open"
    )
    db.session.add_all([event1, event2, event3, event4, event5])
    db.session.commit()

    # Create teams for events
    team1 = Team(
        name="Team Alpha",
        event_id=event1.id,
        leader_id = user1.id,
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
    team4 = Team(
        name="Team Delta",
        event_id=event4.id,
        team_code="DELTA123",
        max_members=5
    )
    team5 = Team(
        name="Team Epsilon",
        event_id=event5.id,
        team_code="EPS123",
        max_members=5
    )
    db.session.add_all([team1, team2, team3, team4, team5])
    db.session.commit()

    # Simulate users joining multiple events via team memberships
    membership1 = TeamMember(team_id=team1.id, user_id=user3.id)
    membership2 = TeamMember(team_id=team2.id, user_id=user3.id)
    membership3 = TeamMember(team_id=team3.id, user_id=user3.id)
    membership4 = TeamMember(team_id=team2.id, user_id=user1.id)
    membership5 = TeamMember(team_id=team1.id, user_id=user2.id)
    membership6 = TeamMember(team_id=team4.id, user_id=user4.id)
    membership7 = TeamMember(team_id=team5.id, user_id=user5.id)
    db.session.add_all([membership1, membership2, membership3, membership4, membership5, membership6, membership7])
    db.session.commit()

    # Add 10 more users (Users 6-15)
    for i in range(6, 16):
        user = User(
            email=f"user{i}@example.com",
            password=generate_password_hash("password123"),
            is_verified=random.choice([True, False]),
            name=f"User {i}",
            university=f"University {i}",
            skills=f"Skill {i}, Skill {i+1}",
            github_link=f"https://github.com/user{i}"
        )
        db.session.add(user)
    db.session.commit()

    # Get all users
    all_users = User.query.all()

    # Add 10 more events (Events 6-15)
    for i in range(6, 16):
        event = Event(
            title=f"Event {i}",
            date=datetime.now() + timedelta(days=i),
            start_time=datetime.now() + timedelta(days=i),
            end_time=datetime.now() + timedelta(days=i, hours=2),
            deadline=datetime.now() + timedelta(days=i-7),
            description=f"Description for Event {i}",
            organizer_id=random.choice(all_users).id,
            # status=random.choice(["open", "ongoing", "completed", "cancelled"])
        )
        db.session.add(event)
    db.session.commit()

    # Get all events
    all_events = Event.query.all()

    # Add 10 more teams (Teams 6-15)
    for i in range(6, 16):
        team = Team(
            name=f"Team {i}",
            event_id=random.choice(all_events).id,
            team_code=f"CODE{i:03d}",
            max_members=random.randint(3, 10)
        )
        db.session.add(team)
    db.session.commit()

    # Get all teams
    all_teams = Team.query.all()

    # Add 10 more team members (Memberships 8-17) - ensure unique (team_id, user_id) pairs
    existing_memberships = {(tm.team_id, tm.user_id) for tm in TeamMember.query.all()}
    new_memberships = set()
    while len(new_memberships) < 10:
        team_id = random.choice(all_teams).id
        user_id = random.choice(all_users).id
        pair = (team_id, user_id)
        if pair not in existing_memberships and pair not in new_memberships:
            new_memberships.add(pair)
    
    for team_id, user_id in new_memberships:
        team_member = TeamMember(team_id=team_id, user_id=user_id)
        db.session.add(team_member)
    db.session.commit()

    # Add 10 tasks
    for i in range(1, 11):
        task = Task(
            title=f"Task {i}",
            team_id=random.choice(all_teams).id,
            assigned_to=random.choice(all_users).id,
            priority=random.choice(["low", "medium", "high"]),
            description=f"Description for Task {i}",
            deadline=(datetime.now() + timedelta(days=random.randint(1, 30))),
            status=random.choice(["pending", "in_progress", "completed"])
        )
        db.session.add(task)
    db.session.commit()

    # Add 10 announcements
    for i in range(1, 11):
        announcement = Announcement(
            event_id=random.choice(all_events).id,
            title=f"Announcement {i}",
            content=f"Content for Announcement {i}",
            created_by=random.choice(all_users).id
        )
        db.session.add(announcement)
    db.session.commit()

    # Add 10 messages
    for i in range(1, 11):
        sender = random.choice(all_users)
        receiver = random.choice([u for u in all_users if u != sender])
        message = Message(
            sender_id=sender.id,
            receiver_id=receiver.id,
            message=f"Message {i} from {sender.name} to {receiver.name}",
            is_read=random.choice([True, False])
        )
        db.session.add(message)
    db.session.commit()

    # Add 10 dashboards
    for i in range(1, 11):
        dashboard = Dashboard(
            user_id=random.choice(all_users).id,
            event_id=random.choice(all_events).id
        )
        db.session.add(dashboard)
    db.session.commit()

    print("Seeded successfully")