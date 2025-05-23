from src.routes.main import app, db, create_sample_data

with app.app_context():
    # Create all tables
    db.create_all()
    # Create sample data
    create_sample_data()
    print("Database initialized successfully!") 