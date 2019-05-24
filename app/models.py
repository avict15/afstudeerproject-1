from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Chargingpoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    availability = db.Column(db.Integer)
    unknown_usage = db.Column(db.Boolean)
    def __repr__(self):
        return '<Chargingpoint {}>'.format(self.body)

class Session(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now)
    endtime = db.Column(db.DateTime)
    status = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chargingpoint_id = db.Column(db.Integer, db.ForeignKey('chargingpoint.id'))

    def __repr__(self):
        return '<Session {}>'.format(self.body)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    licenseplate = db.Column(db.String(15), unique=True)
    
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    chargingpoint_id = db.Column(db.Integer, db.ForeignKey('chargingpoint.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))  
    
    def __repr__(self):
        return '<Message {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


