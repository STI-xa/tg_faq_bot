from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from dotenv import load_dotenv
import os

load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')

Base = declarative_base()


class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True)
    question = Column(String(length=255))
    answer = Column(Text)


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, autoflush=False)
ScopedSession = scoped_session(Session)
session = ScopedSession()
