from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean
from covidbelgium.database import Base
import datetime


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

    def __init__(self, hash, had_covid, has_covid, covid_since=None, covid_until=None):
        self.hash = hash
        self.had_covid = had_covid
        self.has_covid = has_covid
        if self.has_covid or self.had_covid:
            assert covid_since is not None
            self.covid_since = covid_since
        if self.had_covid:
            assert covid_until is not None
            self.covid_until = covid_until
