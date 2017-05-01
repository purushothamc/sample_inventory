from flask_sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_app import db


class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(120))
    admin = db.Column(db.Boolean)

    devices = db.relationship('Device', backref='users', lazy='dynamic')

    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.admin = False
        self.email = email.lower()
        self.set_password(password)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def is_admin(self):
        return self.admin

class Device(db.Model):
    __tablename__ = 'devices'
    uid = db.Column(db.Integer, primary_key=True)
    variant = db.Column(db.String(20), unique=False)
    name = db.Column(db.String(20), unique=False)
    security = db.Column(db.Boolean)
    part_number = db.Column(db.String(20), unique=False)
    imei_number = db.Column(db.String(40), unique=True, nullable=False)
    mfg_country = db.Column(db.String(30))
    vl_tag = db.Column(db.String(10), unique=True, nullable=False)
    purpose_group = db.Column(db.String(20))
    assigned_date = db.Column(db.DateTime, nullable=False, index=True)

    assignee_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False, default=1)

    def __init__(self, variant, name, security, part_number, imei, country, vlid, pgrp, assigned_date, assignee=1):
        self.variant = variant.title()
        self.name = name.title().upper()
        self.is_device_secure(str(security).lower())
        self.part_number = part_number.title().upper()
        self.imei_number = imei.title()
        self.mfg_country = country.title().upper()
        self.vl_tag = vlid.title().upper()
        self.purpose_group = pgrp.title()
        self.assigned_date = assigned_date
        if not assignee:
            self.assigned_id = 1
        else:
            self.assignee_id = assignee

    def is_device_secure(self, security):
        self.security = (security == "true")


class DeviceAssignment(db.Model):
    __tablename__ = "device_assignment"

    device_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    device_assigned_date = db.Column(db.DateTime)
    __table_args__ = (
        db.PrimaryKeyConstraint(device_id, user_id, device_assigned_date),
    )


@event.listens_for(Device, "init")
def init(target, args, kwargs):
    target.assignee_id = 1