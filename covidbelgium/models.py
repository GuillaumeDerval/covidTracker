from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Enum
from covidbelgium.database import Base, db_session
import datetime
import enum


class Sex(enum.Enum):
    male = 0
    female = 1


class LikelyScale(enum.Enum):
    extremely_unlikely = 1
    unlikely = 2
    neutral = 3
    likely = 4
    certain = 5


class Answers(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    hash = Column(String(50), nullable=False)
    datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    covid_likely = Column(Enum(LikelyScale), nullable=False)
    covid_since = Column(Date)
    covid_until = Column(Date)

    sex = Column(Enum(Sex), nullable=False)
    age = Column(Integer, nullable=False)  # a multiple of 5

    symptom_cough = Column(Boolean)
    symptom_fever = Column(Boolean)
    symptom_smell = Column(Boolean)
    symptom_breathing = Column(Boolean)
    symptom_tiredness = Column(Boolean)

    def __init__(self, hash, covid_likely, sex, age, covid_since=None, covid_until=None, symptom_cough=None, symptom_fever=None,
                 symptom_smell=None, symptom_breathing=None, symptom_tiredness=None):
        self.hash = hash
        self.covid_likely = covid_likely
        if self.covid_likely == LikelyScale.likely or self.covid_likely == LikelyScale.certain: #Dates if not neutral
            assert covid_since is not None
            self.covid_since = covid_since
            assert covid_until is not None
            self.covid_until = covid_until
        assert age % 5 == 0
        self.sex = sex
        self.age = age
        self.symptom_cough = symptom_cough
        self.symptom_fever = symptom_fever
        self.symptom_smell = symptom_smell
        self.symptom_breathing = symptom_breathing
        self.symptom_tiredness = symptom_tiredness

    @classmethod
    def find_last_by_hash(cls, hash):
        out = db_session.query(Answers).filter(Answers.hash == hash).order_by(Answers.datetime.desc()).limit(1).all()
        return out[0] if len(out) == 1 else None
