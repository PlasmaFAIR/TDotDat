from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, validators, DateField


class RecordForm(FlaskForm):
    title = StringField("Title", [validators.DataRequired()])
    keywords = StringField("keywords")
    run_date = DateField("Run date")
    contributor_name = StringField("Contributor's name", [validators.DataRequired()])
    software = StringField("Software", [validators.DataRequired()])

    input_file = FileField("Input file")
    output_file = FileField("Output file")
