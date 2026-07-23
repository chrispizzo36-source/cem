from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# MySQL Connection String: mysql+pymysql://username:password@localhost:3306/database_name
# Replace 'root' and 'your_password' with your MySQL Workbench credentials
DATABASE_URL = "mysql+pymysql://root:your_password@localhost:3306/kilifi_cems"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()