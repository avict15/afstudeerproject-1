# Copyright 2019 Koen Cremers
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
        session = Session(user_id=user.id, chargingpoint_id=chargingpoint.id, status="Charging...")
        db.session.add(session)
        db.session.commit()
        Message.query.filter_by(id=message_id).delete()
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

def create_session_unknown_user(key, licenseplate):
        chargingpoint = Chargingpoint.query.filter_by(id = key).first_or_404()
        # chargingpoint = q.first_or_404()
        if chargingpoint.unknown_usage is False:
                abort(415)
        chargingpoint.availability=1
        if db.session.query(User.name).filter_by(licenseplate = licenseplate).scalar() is None:
                user = User(name=licenseplate,licenseplate=licenseplate)
                db.session.add(user)
                db.session.commit()
        else:
                user = User.query.filter_by(licenseplate = licenseplate).first_or_404()
        session = Session(user_id=user.id, chargingpoint_id=key, status="Waiting for payment.")
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
                        session.status="Finished"
                        db.session.commit()
                        return str(chargingpoint.availability), 201
                else:
                        abort(415)     
        return "shouldnt be here", 404     



@app.route('/api/authorize_session_unknown_user/<int:key>', methods=["POST"])
def authorize_session_unknown_user(key):
        chargingpoint = Chargingpoint.query.filter_by(id = key).first_or_404()
        if chargingpoint.availability is 1:
                session = Session.query.filter_by(chargingpoint_id = key).filter_by(endtime = None).first_or_404()
                if "payment" in session.status:
                        session.status="Charging..."
                        db.session.commit()
                        return redirect(url_for('index')) 
                else:
                        abort(415)
        else:
                abort(415)     
        return "shouldnt be here", 404     


@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(415)
def wrong_input(error):
        return make_response(jsonify({'error': 'wrong input'}), 415)
