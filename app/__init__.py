from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap
import urllib.parse 

app = Flask(__name__)
# app.config.from_object(Config)

params = urllib.parse.quote_plus("Driver={ODBC Driver 17 for SQL Server};Server=tcp:afstudeerkoen.database.windows.net,1433;Database=app;Uid=koen@afstudeerkoen;Pwd=Snowroot20;TrustServerCertificate=no;Connection Timeout=30;")


# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLACLHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)

from app import routes, models, api
