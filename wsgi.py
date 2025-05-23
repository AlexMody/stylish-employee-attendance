from src.routes.main import app
from src.models.db import db

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run() 