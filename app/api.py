from app import app, db
from flask import make_response, request, abort, jsonify,  redirect, url_for
from app.models import User, Session, Chargingpoint, Message
from datetime import datetime
import sys

@app.route('/api/create_session/chargingpoint_<int:key>/<string:licenseplate>', methods=["POST"])
def create_session(key, licenseplate):
        chargingpoint = Chargingpoint.query.filter_by(id = key).first_or_404()
        if chargingpoint.availability is 0:
                try:
                        print(db.session.query(User.username).filter_by(licenseplate = licenseplate).scalar(), file=sys.stderr)
                        if db.session.query(User.username).filter_by(licenseplate = licenseplate).scalar() is not None:
                                user = User.query.filter_by(licenseplate = licenseplate).one()
                                msg = Message(recipient=user, body="Would you like to charge here?", chargingpoint_id=key)
                                db.session.add(msg)
                                db.session.commit()
                                return str(msg.id), 201
                        else:
                                return create_session_unknown_user(key, licenseplate)
                except:
                        return create_session_unknown_user(key, licenseplate)
        return "shouldnt be here", 404
        

@app.route('/authorize_session/<int:message_id>')
def authorize_session(message_id):
        message = Message.query.filter_by(id = message_id).first_or_404()
        chargingpoint = Chargingpoint.query.filter_by(id = message.chargingpoint_id).first_or_404()
        if chargingpoint.availability is 1 :
                abort(415)
        chargingpoint.availability=1
        user = User.query.filter_by(id = message.recipient_id).first_or_404()
        session = Session(user_id=user.id, chargingpoint_id=chargingpoint.id, status="Charging")
        db.session.add(session)
        db.session.commit()
        Message.query.filter_by(id=message_id).delete()
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

def create_session_unknown_user(key, licenseplate):
        chargingpoint = Chargingpoint.query.filter_by(id = key).first_or_404()
        # chargingpoint = q.first_or_404()
        if chargingpoint.availability is 1 and chargingpoint.unknown_usage is False:
                abort(415)
        chargingpoint.availability=1
        if db.session.query(User.name).filter_by(licenseplate = licenseplate).scalar() is None:
                user = User(name=licenseplate,licenseplate=licenseplate)
                db.session.add(user)
                db.session.commit()
        else:
                user = User.query.filter_by(licenseplate = licenseplate).first_or_404()
        session = Session(user_id=user.id, chargingpoint_id=key, status="Waiting for payment")
        db.session.add(session)
        db.session.commit()
        return "unknown user is charging", 201


@app.route('/api/unknown_usage/<int:key>', methods=["POST"])
def unknown_usage(key):
        chargingpoint = Chargingpoint.query.filter_by(id = key).first_or_404()
        print(str(chargingpoint.unknown_usage), file=sys.stderr)
        if chargingpoint.unknown_usage:
                chargingpoint.unknown_usage = False
        else:
                chargingpoint.unknown_usage = True
        db.session.commit()
        return str(chargingpoint.unknown_usage), 201

@app.route('/api/stop_session/chargingpoint_<int:key>', methods=["POST"])
def stop_session(key):
        chargingpoint = Chargingpoint.query.filter_by(id = key).first_or_404()
        if chargingpoint.availability is 1:
                session = Session.query.filter_by(chargingpoint_id = key).filter_by(endtime = None).first_or_404()
                if session.endtime is None:
                        chargingpoint.availability=0
                        session.endtime = datetime.now()
                        session.totalprice = session.endtime - session.endtime 
                        db.session.commit()
                        return str(chargingpoint.availability), 201
                else:
                        abort(415)     
        return "shouldnt be here", 404     

@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(415)
def wrong_input(error):
        return make_response(jsonify({'error': 'wrong input'}), 415)
