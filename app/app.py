import os
from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
from redis import Redis
from flask_marshmallow import Marshmallow
from flask_restless import APIManager
from flask_caching import Cache
from flask_mail import Mail
config = {
    "DEBUG": True,          
    "CACHE_TYPE": "simple", 
    "CACHE_DEFAULT_TIMEOUT": 300
}


app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
cache.init_app(app)
app.config.from_object(Configuration)

app.config['DEBUG']=True
app.config['TESTING']=False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USE_SSL']=False
app.config['MAIL_DEBUG']=True
app.config['MAIL_USERNAME']='gevman97@gmail.com'
app.config['MAIL_PASSWORD']='cnvytaqaywxtfdve'
app.config['MAIL_DEFAULT_SENDER'] = 'admin@gmail.com'
app.config['MAIL_MAX_EMAILS']=None
app.config['MAIL_SUPPRESS_SEND']=False
app.config['MAIL_ASCII_ATTACHMENTS']=False
mail=Mail(app)




db = SQLAlchemy(app)
ma=Marshmallow(app)

migrate = Migrate(app, db)
manager=Manager(app)
manager.add_command('db',MigrateCommand)


manage=APIManager(app,flask_sqlalchemy_db=db)
