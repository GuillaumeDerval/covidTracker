from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Enum
from covidbelgium.database import Base, db_session
import datetime
import enum


class Sex(enum.Enum):
    male = 0
    female = 1

class Answers(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    hash = Column(String(50), nullable=False)
    datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    had_covid = Column(Boolean, nullable=False)
    has_covid = Column(Boolean, nullable=False)
    covid_since = Column(Date)
    covid_until = Column(Date)

    sex = Column(Enum(Sex), nullable=False)
    age = Column(Integer, nullable=False)  # a multiple of 5

    def __init__(self, hash, had_covid, has_covid, sex, age, covid_since=None, covid_until=None):
        self.hash = hash
        self.had_covid = had_covid
        self.has_covid = has_covid
        if self.has_covid or self.had_covid:
            assert covid_since is not None
            self.covid_since = covid_since
        if self.had_covid:
            assert covid_until is not None
            self.covid_until = covid_until
        assert age % 5 == 0
        self.sex = sex
        self.age = age

    @classmethod
    def find_last_by_hash(cls, hash):
        out = db_session.query(Answers).filter(Answers.hash == hash).order_by(Answers.datetime.desc()).limit(1).all()
        return out[0] if len(out) == 1 else None
