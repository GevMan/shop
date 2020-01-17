import os
from flask import Blueprint
from flask import Flask,render_template,redirect,url_for,request,session,json,make_response,current_app,jsonify
from werkzeug.utils import secure_filename
from models import users
from app import db
import datetime
from datetime import timedelta,datetime
from validate_email import validate_email
links=Blueprint('links',__name__,template_folder='templates')


@links.route('/')
def index():
    
    user = None
    if 'logged_in' in session:
    
        user = users.query.filter(users.id==session['user']['id']).first()
   
    messages = None
    if request.args.get('messages') is not None:
        messages =json.loads(request.args.get('messages'))
    return render_template('links/index.html',user=user, error=messages)

@links.route('/addpicture',methods=['POST'])
def addpicture():
    update_this=users.query.filter(users.id==session['user']['id']).first()
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    file=request.files['picture']  
    filename = secure_filename(str(timestamp)+file.filename)
    update_this.picture = filename
    file.save(os.path.join('static/picture', filename))
    db.session.commit()
    return redirect(url_for('links.index'))

@links.route('/update',methods=['POST'])
def update():
    messages = dict()  
    update=users.query.filter(users.id==session['user']['id']).first()
    if 'username' in request.form:
        if users.query.filter(users.username==request.form['username']).first() is not None:
            messages['username'] = 'Username already exists!'

        if update.username == request.form['username']:
            return ""
        else:
            update.username = request.form['username'] 
        
        if len(request.form['username']) < 1:
                messages['username'] = 'Username is not valid!'        
    
    if 'email' in request.form:
        update.email=request.form['email'] 
        if not validate_email(request.form['email']):
            messages['email'] = 'Email is not valid'
   
    if len(messages) > 0:
        return json.dumps(messages)    
    
    db.session.commit()
    return 'True'
