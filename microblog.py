from app import app, db
from app.models import User, Session, Chargingpoint, Message



@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,  'Session' : Session, 'Chargingpoint' : Chargingpoint, 'Message': Message}
