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
    submit = SubmitField("Submit", )
    level = SelectField("Level", choices=[(0, "BS IS"),
                                          (1, "Category"),
                                          (2, "Sub Category"),
                                          (3, "Sub Account"),
                                          ]
                        )
