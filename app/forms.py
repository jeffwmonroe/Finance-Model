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

import wtforms.widgets


class CheckBoxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


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
    yearly = BooleanField("Yearly")
    sub_categories = CheckBoxField("Sub Categories", choices=[("one", "One")])

    category = SubmitField("Category")
