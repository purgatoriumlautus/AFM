from src.db import db
from src.app import create_app
from sqlalchemy import text


app = create_app()
from src.db import db
from src.app import create_app

app = create_app()

def drop_all_tables():
    with app.app_context():
        db.drop_all()

if __name__ == "__main__":
    drop_all_tables()
