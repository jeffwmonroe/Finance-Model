from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FloatField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    widgets,
    RadioField,
)


class AccountControl(FlaskForm):
    decrease = SubmitField("Decrease")
    chart_number = IntegerField()
    increase = SubmitField("Increase")
