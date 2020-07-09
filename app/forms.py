"""Collestion of forms for HiCognition"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Required, NumberRange
from app.models import User


class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Registration form"""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Helper to validate user name."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Helper to validate email."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class AddDatasetForm(FlaskForm):
    """Form to add a new dataset"""
    name = StringField('Dataset name', validators=[DataRequired()])
    filePath = FileField("Data file", validators=[FileRequired()])
    file_type = SelectField("Data type", validators=[Required()],
                            choices=[("bedfile", "bedfile"),
                                     ("cooler", "cooler")])
    submit = SubmitField('Add dataset')


class SelectDatasetForm(FlaskForm):
    """Form to select a dataset."""
    region = SelectField("Region", validators=[Required()], coerce=int)
    cooler = SelectField("Cooler file", validators=[Required()], coerce=int)
    submit_select = SubmitField("Submit")


class DefinePileupRegionsForm(FlaskForm):
    """Form to define the pileup regions before
    commencing pileup."""
    windowsize = IntegerField("Halfwindow", validators=[Required(), NumberRange(min=10000, max=1000000)])
    binsize = SelectField("Binsize", validators=[DataRequired()])
    submit_define = SubmitField("Submit")

    #def validate_windowsize(self, binsize, windowsize):
    #    """Checks whether windowsize is larger than binsize."""
    #    if windowsize < binsize:
    #        raise ValidationError("Windowsize must be larger than binsize!")