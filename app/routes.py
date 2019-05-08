from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Session, Chargingpoint, Message
from datetime import datetime
import os

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/plus.png')
def plus():
    return send_from_directory(os.path.join(app.root_path, 'static'),'plus.png', mimetype='image/vnd.microsoft.icon')

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = User.query.filter_by(username = current_user.username).first_or_404()
    sessions = Session.query.filter_by(user_id = user.id).order_by(Session.created.desc())
    return render_template('index.html', title='Home', sessions=sessions)

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
       
    
@app.route('/admin/dashboard')
def admin_dashboard():
    chargepoints = Chargingpoint.query.all()
    sessions = Session.query.filter_by(endtime = None)
    users = User.query.all()
    return render_template('dashboard.html', title='Dashboard', chargingpoints=chargepoints, sessions=sessions, users=users)


@app.route('/admin/dashboard_table')
def admin_dashboard_table():
    sessions = Session.query.order_by(Session.created.desc())
    users = User.query.all()
    return render_template('admin_table.html', title='Sessions', sessions=sessions, users=users)


@app.route('/unknown_user', methods=['GET'])
def unknown_user():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('unknown_user.html', title='Unknown User', posts=posts)


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
        user = User(name=form.name.data, username=form.username.data, email=form.email.data,licenseplate=form.licenseplate.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
