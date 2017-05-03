from flask_app import db, app
from flask_wtf import FlaskForm
from flask import session
from wtforms import StringField, TextAreaField, SubmitField, validators, \
    ValidationError, PasswordField, SelectField, DateField
from .models import User, Device


class ContactForm(FlaskForm):
    name = StringField("Name", [validators.DataRequired("Please enter your name")])
    email = StringField("Email", [validators.DataRequired("Please enter your email address."),
                                  validators.Email("Please enter your email")])
    subject = StringField("Subject", [validators.DataRequired("Please enter subject")])
    message = TextAreaField("Message", [validators.DataRequired("Please enter message")])
    submit = SubmitField("Send")


class SignupForm(FlaskForm):
    firstname = StringField("First name", [validators.DataRequired("Please enter your first name.")])
    lastname = StringField("Last name", [validators.DataRequired("Please enter your last name.")])
    email = StringField("Email", [validators.DataRequired("Please enter your email address."),
                                validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.DataRequired("Please enter a password.")])
    submit = SubmitField("Create account")

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user:
            self.email.errors.append("That email is already taken")
            return False
        else:
            if "blackberry.com" not in self.email.data.lower():
                self.email.errors.append("Pleae use your blackberry email")
                return False
            return True


class SigninForm(FlaskForm):
    email = StringField("Email", [validators.DataRequired("Please enter your email address."),
                                validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.DataRequired("Please enter a password.")])
    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append("Invalid e-mail or password")
            return False


class ChangePasswordForm(FlaskForm):
    currentPassword = PasswordField('Current Password', [validators.DataRequired("Please enter current password.")])
    newPassword = PasswordField('New Password', [validators.DataRequired("Please enter new password.")])
    confirmPassword = PasswordField('Confirm Password', [validators.DataRequired("Please enter new password.")])
    submit = SubmitField("Change Password")

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        user_email = session['email']
        user = User.query.filter_by(email=user_email.lower()).first()
        if user and user.check_password(self.currentPassword.data):
            if self.newPassword.data == self.confirmPassword.data:
                if self.currentPassword.data == self.newPassword.data or \
                        self.currentPassword.data == self.confirmPassword.data:
                    self.currentPassword.errors.append("New password can't be same as old one")
                    return False
                return True
            else:
                self.currentPassword.errors.append("New Password didn't match")
                return False
        else:
            self.currentPassword.errors.append("Entered password is not correct")
            return False

class AddDeviceForm(FlaskForm):
    variant = StringField('Device Variant', [validators.DataRequired("Please enter Device Variant")])
    name = StringField('Device Name', [validators.DataRequired("Please enter Device Name")])
    is_secure = SelectField('Secure Device ?', choices=[('True', 'True'), ('False', 'False')])
    part_number = StringField('Device Part Number')
    imei_number = StringField('Device IMEI', [validators.DataRequired("Please enter Device Name")])
    country = StringField('Manufactured Country')
    vlId = StringField('VLBB ID', [validators.DataRequired("Please enter Device Name")])
    purpose_group = SelectField('Device Use Purpose',
                                choices=[('Shared Pool', 'Shared Pool'),
                                         ('automation', 'Automation'),
                                         ('development', 'Development'),
                                         ('manual_test', 'Manual Testing')])
    comments = TextAreaField("Comments", [validators.DataRequired("Please enter comments if any")])
    submit = SubmitField("Add New Device To DB")

class SearchDeviceForm(FlaskForm):
    search_using = SelectField('Search For a Device using',
                               choices=[('vlbb_id', 'VL Tag ID'),
                                        ('imei_number', 'IMEI Number'),
                                        ('user_email', 'User Email Address'),
                                        ('device_name', 'Device Name'),
                                        ('device_variant', 'Device Variant')])
    search_string = StringField('Search String', [validators.DataRequired("Please enter a Search String")])
    submit = SubmitField("Search for Devices")


class DeviceAssignForm(FlaskForm):
    vl_id = StringField('VLBB ID', [validators.DataRequired("Please enter Device Name")])
    email_id = StringField('User Email Address', [validators.DataRequired("Please enter your email address."),
                                validators.Email("Please enter your email address.")])
    submit = SubmitField("Assign Device")


class AssignHistoryForm(FlaskForm):
    vlid = StringField('VLBB ID', [validators.DataRequired("Please enter Device Name")])
    submit = SubmitField("Show Assignment History")

