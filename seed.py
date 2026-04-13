from app import db, app
from app.models import User

app.app_context().push()
db.create_all()
db.session.query(User).delete()
u1 = User(username = "bailan", email = "bailan@example.com")
u2 = User(username = "bleh", email = "bleh@example.com")
db.session.add_all([u1, u2])
db.session.commit()
