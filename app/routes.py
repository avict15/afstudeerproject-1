# Copyright 2019 Koen Cremers
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, SendMessageForm
from app.models import User, Session, Chargingpoint, Message
from datetime import datetime,timedelta
import sys
import os

@app.route('/logout.png')
def logoutimage():
    return send_from_directory(os.path.join(app.root_path, 'static'),'logout.png', mimetype='image/vnd.microsoft.icon')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/background.png')
def background():
    return send_from_directory(os.path.join(app.root_path, 'static'),'background.png', mimetype='image/vnd.microsoft.icon')

@app.route('/plus.png')
def plus():
    return send_from_directory(os.path.join(app.root_path, 'static'),'plus.png', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    user = User.query.filter_by(username = current_user.username).first_or_404()
    sessions = Session.query.filter_by(user_id = user.id).order_by(Session.created.desc())
    chargepoints = Chargingpoint.query.all()
    timeUsage = timedelta(0)
    totalprice = 0
    amount = 0
    for session in sessions:
        amount += 1
        if session.endtime:
            timeUsage += session.endtime - session.created
            for chargepoint in chargepoints:
                if chargepoint.id is session.chargingpoint_id:
                    totalprice += ((session.endtime - session.created).total_seconds() / 3600 ) * chargepoint.price
    return render_template('index.html', title='Home', sessions=sessions, datetime=datetime, time=timeUsage, price=totalprice, amount=amount)

@app.route('/search/<string:name>')
@login_required
def search_results(name):
    user = User.query.filter_by(name = name).first_or_404()
    sessions = Session.query.filter_by(user_id = user.id).order_by(Session.created.desc())
    return render_template('search.html', title=user.name, sessions=sessions, datetime=datetime)

@app.route('/profile')
@login_required
def profile():
    user = User.query.filter_by(username = current_user.username).first_or_404()
    sessions = Session.query.filter_by(user_id = user.id).order_by(Session.created.desc())
    chargepoints = Chargingpoint.query.all()
    timeUsage = timedelta(0)
    totalprice = 0
    amount = 0
    for session in sessions:
        amount += 1
        if session.endtime:
            timeUsage += session.endtime - session.created
            for chargepoint in chargepoints:
                if chargepoint.id is session.chargingpoint_id:
                    totalprice += ((session.endtime - session.created).total_seconds() / 3600 ) * chargepoint.price
    return render_template('profile.html', user=user, amount=amount, price=totalprice)


@app.route('/settings')
@login_required
def settings():
    chargepoints = Chargingpoint.query.all()
    return render_template('settings.html', title='Settings', chargingpoints=chargepoints)



@app.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    messages = current_user.messages_received.order_by(Message.timestamp.desc())
    return render_template('messages.html', messages=messages)
 
@app.route('/delete_message/<int:message_id>')
@login_required
def delete_message(message_id):
    Message.query.filter_by(id=message_id).delete()
    db.session.commit()
    messages = current_user.messages_received.order_by(Message.timestamp.desc())
    return render_template('messages.html', messages=messages)
       
    
@app.route('/admin/dashboard', methods=['GET','POST'])
@login_required
def admin_dashboard():
    chargepoints = Chargingpoint.query.all()
    sessions = Session.query.filter_by(endtime = None)
    users = User.query.all()
    form = SendMessageForm()
    name = request.form.get('user', None)
    if name is not None:
        user = User.query.filter_by(id = form.user.data).first_or_404()
        print('test', file=sys.stderr)
        message = Message(recipient=user,body=form.text.data)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('dashboard.html', title='Dashboard', chargingpoints=chargepoints, sessions=sessions, users=users, form=form)

@app.route('/admin/dashboard_table')
@login_required
def admin_dashboard_table():
    sessions = Session.query.order_by(Session.created.desc())
    users = User.query.all()
    return render_template('admin_table.html', title='Sessions', sessions=sessions, users=users)


@app.route('/unknown_user', methods=['GET'])
def unknown_user():
    chargepoints = Chargingpoint.query.all()
    return render_template('unknown_user.html', title='Unknown User', chargepoints=chargepoints)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user) #remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, username=form.username.data, email=form.email.data,licenseplate=form.licenseplate.data,last_message_read_time=datetime.utcnow())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
