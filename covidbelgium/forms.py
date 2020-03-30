from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, RadioField, DateField
from wtforms.validators import DataRequired

class AnswerForm(FlaskForm):
    hash = StringField('hash', validators=[DataRequired()])
    covid_status = RadioField('Are you currently ill from the Covid-19, or did you in the past?',
                              validators=[DataRequired()], choices={"currently": "I have Covid-19 right now",
                                                                    "past": "I had Covid-19 in the past",
                                                                    "maybe_past": "I'm not sure weither I had Covid-19 in the past (I had symptoms)",
                                                                    "maybe_present": "I'm not sure weither I have Covid-19 now (I have symptoms)",
                                                                    "no": "I do not think I had/have the Covid-19."})
    when_start = DateField("When did the symptoms start?")
    when_end = DateField("When did the symptoms end?")
