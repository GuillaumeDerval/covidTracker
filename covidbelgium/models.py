from collections import OrderedDict
from typing import Dict, List

from flask_babel import lazy_gettext
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
    hash = Column(String(64), nullable=False)
    datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    covid_likely = Column(Enum(LikelyScale), nullable=False)
    covid_since = Column(Date)
    covid_until = Column(Date)

    sex = Column(Enum(Sex), nullable=False)
    age = Column(Integer, nullable=False)  # a multiple of 5
    municipality = Column(Integer, nullable=False)

    symptom_cough = Column(Boolean)
    symptom_shivers = Column(Boolean)
    symptom_headache = Column(Boolean)
    symptom_muscle_pain = Column(Boolean)
    symptom_throat = Column(Boolean)
    symptom_diarrhea = Column(Boolean)
    symptom_vomit = Column(Boolean)
    symptom_nose = Column(Boolean)
    symptom_fever = Column(Boolean)
    symptom_smell = Column(Boolean)
    symptom_breathing = Column(Boolean)
    symptom_tiredness = Column(Boolean)

    def __init__(self, hash, covid_likely, sex, age, municipality, covid_since=None, covid_until=None, symptoms=None):
        self.hash = hash
        self.covid_likely = covid_likely
        if self.covid_likely != LikelyScale.extremely_unlikely:  # Dates if not neutral
            assert covid_since is not None
            self.covid_since = covid_since
            assert covid_until is not None
            self.covid_until = covid_until
        assert age % 5 == 0
        self.sex = sex
        self.age = age
        self.municipality = municipality

        for x in self.all_symptoms:
            self.__setattr__(f"symptom_{x}", False)
        if symptoms is not None:
            if isinstance(symptoms, dict):
                for x in symptoms:
                    self.__setattr__(f"symptom_{x}", symptoms[x])
            else:
                for x in symptoms:
                    self.__setattr__(f"symptom_{x}", True)

    @classmethod
    def find_last_by_hash(cls, hash: str) -> 'Answers':
        out = db_session.query(Answers).filter(Answers.hash == hash).order_by(Answers.datetime.desc()).limit(1).all()
        return out[0] if len(out) == 1 else None

    all_symptoms = OrderedDict([
        ('vomit', lazy_gettext("Vomiting")),
        ('nose', lazy_gettext("Stuffy or runny nose")),
        ('fever', lazy_gettext("High fever (> 38°C)")),
        ('smell', lazy_gettext("Loss of smell or taste")),
        ('breathing', lazy_gettext("Breathing difficulties")),
        ('tiredness', lazy_gettext("Tiredness")),
        ('cough', lazy_gettext('Dry Cough')),
        ('shivers', lazy_gettext("Shivers")),
        ('headache', lazy_gettext("Headache")),
        ('muscle_pain', lazy_gettext("Muscle pain")),
        ('throat', lazy_gettext("Sore throat")),
        ('diarrhea', lazy_gettext("Diarrhea"))
    ])

    def get_active_symptoms(self) -> List[int]:
        out = []
        for symptom in self.all_symptoms.keys():
            if self.__getattribute__(f"symptom_{symptom}"):
                out.append(symptom)
        return out

    def get_active_symptoms_dict(self) -> Dict[str, bool]:
        return {symptom: self.__getattribute__(f"symptom_{symptom}") for symptom in self.all_symptoms.keys()}
