from flask_app import app, db
from flask import render_template, request, flash, session, redirect, url_for
from .forms import ContactForm, SignupForm, SigninForm, ChangePasswordForm, \
                    AddDeviceForm, SearchDeviceForm, DeviceAssignForm, AssignHistoryForm
from flask_mail import Message, Mail
from .models import User, Device, DeviceAssignment
from functools import wraps
from sqlalchemy import desc
import datetime
from threading import Thread

mail = Mail()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session:
            return redirect(url_for('signin', next=request.url))
        return render_template(f.__name__+'.html', *args, **kwargs)
    return decorated_function


def to_bool(value):
    return str(value).lower() == "true"


@app.route('/')
@login_required
def home():
    pass


@app.route('/contact', methods=['GET', "POST"])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        if not form.validate():
            flash('All fields are required.')
            return render_template('contact.html', form=form)
        else:
            msg = Message(form.subject.data, sender='contact@example.com',
                          recipients=['your_email@example.com'])
            msg.body = """
                  From: %s <%s>
                  %s
                  """ % (form.name.data, form.email.data, form.message.data)
            mail.send(msg)
            return render_template('contact.html', success=True)
    elif request.method == 'GET':
        return render_template('contact.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if 'email' in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        if not form.validate():
            return render_template('signup.html', form=form)
        else:
            newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()

            session['email'] = newuser.email
            session['is_admin'] = (newuser.admin == True)
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signup.html', form=form)


@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('signin'))

    user = User.query.filter_by(email=session['email']).first()

    if user is None:
        return redirect(url_for('signin'))
    else:
        devices_list = Device.query.join(User).filter(Device.assignee_id==user.uid).all()
        if not devices_list:
            message = "No devices assigned to your name"
            return render_template('profile.html', success=False, message=message, user=user)

        message = "Following list of devices assigned to your name"
        return render_template('profile.html', success=True, devices=devices_list, message=message, user=user)


@app.route('/device_detail/<vlid>', methods=['GET'])
def device_detail(vlid):
    if 'email' not in session:
        return redirect(url_for('signin'))

    device_info = Device.query.filter_by(vl_tag=vlid).first()
    print(Device.__table__.columns.keys())

    if not device_info:
        message = "Device Information is not found for device with ID {0}".format(vlid)
        return render_template('device_detail.html', success=False, message=message)

    message = "Device information for device with ID {0}".format(vlid)
    user_info = User.query.filter_by(uid=device_info.assignee_id).first()
    return render_template('device_detail.html', success=True, message=message, info=device_info, user=user_info)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()

    if 'email' in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        if not form.validate():
            return render_template('signin.html', form=form)
        else:
            user_info = User.query.filter_by(email=form.email.data).first()
            session['email'] = form.email.data
            session['is_admin'] = (user_info.admin == True)
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signin.html', form=form)


@app.route('/signout')
def signout():
    if 'email' not in session:
        return redirect(url_for('signin'))

    session.pop('email', None)
    return redirect(url_for('home'))


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()

    if 'email' not in session:
        return redirect(url_for('signin'))

    if request.method == 'GET':
        return render_template('change_password.html', form=form)

    elif request.method == 'POST':
        if not form.validate():
            return render_template('change_password.html', form=form)
        else:
            user = User.query.filter_by(email=session['email'].lower()).first()
            user.set_password(form.newPassword.data)
            db.session.commit()
            return render_template('change_password.html', success=True)


@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    form = AddDeviceForm()

    if 'email' not in session or not session['is_admin']:
        return redirect(url_for('signin'))

    if request.method == 'GET':
        return render_template('add_device.html', form=form)

    elif request.method == 'POST':
        if not form.validate():
            return render_template('add_device.html', form=form)
        else:
            secure = to_bool(form.is_secure.data)
            newDevice = Device(variant=form.variant.data, name=form.name.data, security=secure,
                               part_number=form.part_number.data, imei=form.imei_number.data,
                               country=form.country.data, vlid=form.vlId.data,
                               pgrp=form.purpose_group.data,
                               assigned_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            db.session.add(newDevice)
            db.session.commit()

            device_info = Device.query.filter_by(vl_tag=form.vlId.data).first()
            newDeviceAssignment = DeviceAssignment(device_id=device_info.uid,
                                                   user_id=1, device_assigned_date=device_info.assigned_date)
            db.session.add(newDeviceAssignment)
            db.session.commit()

            return render_template('add_device.html', success=True,
                            message="New device {0} is added to database".format(form.vlId.data))


@app.route('/search_device', methods=['GET', 'POST'])
def search_device():
    form = SearchDeviceForm()

    if 'email' not in session:
        return redirect(url_for('signin'))
    if request.method == 'GET':
        return render_template('search_device.html', form=form)

    elif request.method == 'POST':
        if not form.validate():
            return render_template('search_device.html', form=form)
        else:
            message = "Search Results"
            search_string = form.search_string.data
            devices_list = []

            if form.search_using.data == "vlbb_id":
                devices_list = Device.query.filter_by(vl_tag=search_string).all()
                if not devices_list:
                    message = "No Devices found with VLBB ID: {0}".format(search_string)
                    return render_template('search_device.html', form=form, message=message, success=False)

            elif form.search_using.data == "imei_number":
                devices_list = Device.query.filter_by(imei_number=search_string).all()
                if not devices_list:
                    message = "No Devices found with IMEI number {0}".format(search_string)
                    return render_template('search_device.html', form=form, message=message, success=False)

            elif form.search_using.data == "device_name":
                devices_list = Device.query.filter_by(name=search_string.upper()).all()
                if not devices_list:
                    message = "No Devices found with Device Name {0}".format(search_string)
                    return render_template('search_device.html', form=form, message=message, success=False)

            elif form.search_using.data == "device_variant":
                devices_list = Device.query.filter_by(variant=search_string).all()
                if not devices_list:
                    message = "No Devices found with Device Variant {0}".format(search_string)
                    return render_template('search_device.html', form=form, message=message, success=False)

            elif form.search_using.data == "user_email":
                user_info = User.query.filter(User.email.contains(search_string)).first()
                if not user_info:
                    message = "No user found with email address {0}".format(search_string)
                    return render_template('search_device.html', form=form, message=message, success=False)
                devices_list = Device.query.join(User).filter(Device.assignee_id == user_info.uid).all()
                if not devices_list:
                    message = "No devices assigned to user {0}".format(user_info.firstname)
                    return render_template('search_device.html', form=form, message=message, success=False)

            if form.search_using.data == "vlbb_id":
                message += " for device VLBB ID: {0}".format(search_string)
            elif form.search_using.data == "imei_number":
                message += " for device IMEI Number: {0}".format(search_string)
            elif form.search_using.data == "device_name":
                message += " for device name: {0}".format(search_string.upper())
            elif form.search_using.data == "device_variant":
                message += " for device variant: {0}".format(search_string.upper())
            elif form.search_using.data == "user_email":
                message += " for devices assigned to user with email address: {0}@blackberry.com".format(search_string)

            for device in devices_list:
                device.user_info = User.query.filter_by(uid=device.assignee_id).first()

            return render_template('search_device.html', form=form, devices=devices_list, success=True, message=message)


@app.route('/assign_device/<vlid>', methods=['GET'])
def assign_device(vlid):
    if 'email' not in session:
        return redirect(url_for('signin'))

    device_info = Device.query.filter_by(vl_tag=vlid).first()

    if not device_info:
        message = "Device Information is not found for device with ID {0}".format(vlid)
        return render_template('assign_device.html', success=False, message=message)

    user = User.query.filter_by(email=session['email'].lower()).first()
    device = Device.query.filter_by(vl_tag=vlid).update(dict(assignee_id=user.uid))
    db.session.commit()

    device = Device.query.filter_by(vl_tag=vlid).first()
    device.assigned_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.session.commit()

    device = Device.query.filter_by(vl_tag=vlid).first()
    newDeviceAssignment = DeviceAssignment(device_id=device.uid,
                               user_id=user.uid, device_assigned_date=device.assigned_date)
    db.session.add(newDeviceAssignment)
    db.session.commit()

    message = "Hello User, The device with VLBB ID {0} is assigned to your name".format(vlid) + \
              "\n\n Thanks, \n BlackBerry Hyderabad Inventory Team"
    msg = Message('Hello', sender='purush.bb10@gmail.com', recipients=['purushotham.c@gmail.com'])
    msg.body = message
    t = Thread(name="mail-sending-thread", target=mail.send(msg))
    t.start()
    #mail.send(msg)

    message = "Device with VLBB ID {0} is assigned with your name".format(vlid)
    return render_template('search_device.html', success=True, message=message, from_assigned=True)

@app.route('/assign_device_user', methods=['POST', 'GET'])
def assign_device_user():
    form = DeviceAssignForm()
    if 'email' not in session or not session['is_admin']:
        return redirect(url_for('signin'))

    if request.method == 'GET':
        return render_template('assign_device_user.html', form=form)

    elif request.method == 'POST':
        if not form.validate():
            return render_template('assign_device_user.html', form=form)

    user = User.query.filter_by(email=form.email_id.data.lower()).first()
    device = Device.query.filter_by(vl_tag=form.vl_id.data).first()
    if device.assignee_id == user.uid:
        message = "User is already assigned with selected device"
        return render_template('assign_device_user.html', form=form, success=False, message=message)
    else:
        device.assignee_id = user.uid
        device.assigned_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()

        device = Device.query.filter_by(vl_tag=form.vl_id.data).first()
        newDeviceAssignment = DeviceAssignment(device_id=device.uid,
                                           user_id=user.uid, device_assigned_date=device.assigned_date)
        db.session.add(newDeviceAssignment)
        db.session.commit()
        message = "User is assigned with device {0}".format(device.vl_tag)
        return render_template('assign_device_user.html', form=form, success=True, message=message)

@app.route('/assignment_history', methods=['POST', 'GET'])
def assignment_history():
    form = AssignHistoryForm()
    if 'email' not in session or not session['is_admin']:
        return redirect(url_for('signin'))

    if request.method == 'GET':
        return render_template('assignment_history.html', form=form)

    elif request.method == 'POST':
        if not form.validate():
            return render_template('assignment_history.html', form=form)
    d_id = Device.query.filter_by(vl_tag=form.vlid.data).first().uid
    device = DeviceAssignment.query.filter_by(device_id=d_id).\
        order_by(desc(DeviceAssignment.device_assigned_date)).all()
    output = []
    for _d in device:
        temp = []
        temp.append(Device.query.filter_by(uid=_d.device_id).first().vl_tag)
        temp.append(User.query.filter_by(uid=_d.user_id).first().firstname)
        temp.append(_d.device_assigned_date)
        output.append(temp)
    print(output)
    if not device:
        message = "No devices found with selected VLBB ID {0}".format(form.vlid.data)
        return render_template('assignment_history.html', form=form, success=False, message=message)
    message = "Device Assignment History for device with VLBB ID: {0}".format(format(form.vlid.data))
    return render_template('assignment_history.html', form=form, success=True, message=message, data=output)
