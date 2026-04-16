from flask_wtf import FlaskForm
from wtforms.fields import (SubmitField, StringField, PasswordField, 
                            SelectField, EmailField, TelField, RadioField)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from wtforms import ValidationError
from datetime import datetime

class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=50)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    role = SelectField("Role", choices=[("customer", "Customer"), ("artist", "Artist")], validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=72)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create Account")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=50)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


def validate_expiry_date(form, field):
    try:
         expiry_date = datetime.strptime(field.data, '%m/%y').date()
    except ValueError:      
        raise ValidationError('The expiry date must be in the format MM/YY.')
    if expiry_date < datetime.now().date():
        raise ValidationError('The expiry date must be in the future.')

class CheckoutForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired()])
    email = EmailField("Email", validators=[Optional(), Email()])
    phone = TelField("Phone", validators=[Optional()])
    address = StringField("Delivery address", validators=[Optional()])
    payment_method = RadioField(
        "Payment method",
        choices=[("credit_card", "Credit Card (Demo)"), ("paypal", "PayPal (Demo)")],
        validators=[DataRequired()]
    )
    card_number = StringField("Card number", validators=[Optional(), Length(min=16, max=16)])
    card_expiry = StringField("Expiry (MM/YY)", validators=[Optional(), Length(min=5, max=5), validate_expiry_date])
    card_cvv = StringField("CVV", validators=[Optional(), Length(min=3, max=3)])
    paypal_email = EmailField("PayPal email", validators=[Optional(), Email()])
    paypal_password = StringField("PayPal password", validators=[Optional()])
    submit = SubmitField("Submit order")