from flask import Flask
from flask_login import LoginManager
import psycopg2


app = Flask(__name__)
app.config.from_object('app.config')

lm = LoginManager()
lm.init_app(app)
db = psycopg2.connect(database="DLS", user="postgres", password="hamster", host="127.0.0.1", port="5432")


from app import views
