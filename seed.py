from app import app, db, User, Event, Team, Task, Announcement, Messages, TeamMember
from datetime import datetime

def seed_data():
    # Create users
    Ali = User(
        name = "Ali",
        email = "ali@gmail.com",
        password = "123456",
        university = "University",
        skills = "Python",
        github_link = "https://github.com/ali"
    )
    Tan = User(
        name = "Tan",
        email = "tan@gmail.com",
        password = "789456",
        university = "Uni",
        skills = "C++",
        github_link = "https://github.com/tan"
    )

    # Add users to the database
    db.session.add(Ali)
    db.session.add(Tan)
    db.session.commit()

    # Create an event
    event = Event(
        title = "Hackathon",
        description = "A coding competition",
        organizer_id = Ali.id,
        status = "Upcoming"
    )

    db.session.add(event)
    db.session.commit()

    # Create a team
    team = Team(
        name = "Team ABC",
        team_code = "ABC123",
        max_members = 5
    )

    db.session.add(team)
    db.session.commit()

    # Create a task
    task = Task(
        title ="Build a website",
        team_id = team.id,
        assigned_to = Tan.id,
        priority = "High",
        description = "Create a website for the hackathon project",
        deadline = "2026-10-15",
        status = "In Progress"
    )
    db.session.add(task)
    db.session.commit()

    # Create an announcement
    announcement = Announcement(
        title = "Welcome to the Hackathon!",
        content = "Let the coding begin!",
        event_id = event.id,
        created_by = Ali.id
    )
    db.session.add(announcement)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        seed_data()