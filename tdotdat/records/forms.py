from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, validators, DateField, IntegerField, BooleanField


class RecordForm(FlaskForm):
    title = StringField("Title", [validators.DataRequired()])
    keywords = StringField("Keywords")
    run_date = DateField("Run date")
    contributor_name = StringField("Contributor's name", [validators.DataRequired()])
    software = StringField("Software")
    equilibrium_id = IntegerField("Equilibrium ID")
    converged = BooleanField("Is simulation converged?")

    input_file = FileField("Input file", [validators.DataRequired()])
    output_file = FileField("Output file(s)", render_kw={"multiple": True})
