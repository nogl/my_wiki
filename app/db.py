import os
from sqlalchemy import create_engine
from sqlalchemy.orm import session

engine = create_engine(os.getenv('DATABASE_URL'))
db_session = session.Session(autocommit=False, autoflush=False, bind=engine)
