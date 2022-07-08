from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, validators, FloatField, ValidationError


class EquilibriumForm(FlaskForm):
    title = StringField("Title", [validators.DataRequired()])

    elongation = FloatField("Elongation", [validators.Optional()])
    q = FloatField("Safety factor, q", [validators.Optional()])
    B0 = FloatField("Magnetic field, B0", [validators.Optional()])

    input_file = FileField("Input file")

    def validate_input_file(self, field):
        manual = self.elongation.data or self.q.data or self.B0.data
        if manual and field.data:
            raise ValidationError("Cannot specify both input file and manual data")
