import os
from flask import Blueprint
from app import db
from models import posts,comment,users
from flask import redirect,render_template,request,session,url_for,json,jsonify
import datetime
from datetime import timedelta,datetime
from werkzeug.utils import secure_filename
from flask_paginate import Pagination, get_page_parameter,get_page_args

links_blog=Blueprint('links_blog',__name__,template_folder='templates')


@links_blog.route('/blog/')
@links_blog.route('/blog/page/<int:page_num>')
def blog(page_num):
    newpost = posts.query.filter(posts.user.has(posts.user_id))
    blogPage=posts.query.paginate(per_page=6,page=page_num,error_out=True)
    
    return render_template('links/blog.html',blogPage=blogPage,posts=newpost)


@links_blog.route('/blog/<id>')
def singlePage(id):
    post = posts.query.filter(posts.id==id).first()
    comm = comment.query.filter(comment.post_id==post.id).all()
    return render_template('links/singlePage.html',post=post,comm=comm)



@links_blog.route('/addpost')
def addpost():
    messages = None
    if request.args.get('messages') is not None:
        messages =json.loads(request.args.get('messages') )
    return render_template('links/addpost.html',errors=messages)


@links_blog.route('/newpost',methods=['POST'])
def newpost():      
    if len(request.form['title'])<2:
        return redirect(url_for('links_blog.addpost',messages=json.dumps({'title':'Enter longer title'})))
    if not request.files['image']:
        return redirect(url_for('links_blog.addpost',messages=json.dumps({'image':'Please upload a picture'})))

    now = datetime.now()
    timestamp = datetime.timestamp(now)
    file=request.files['image']
    filename = secure_filename(str(timestamp)+file.filename)
    file.save(os.path.join('app/static/images', filename))
    user = users.query.filter(users.id==session['user']['id']).first()
    post=posts(title=request.form['title'],content=request.form['content'],image=filename,user=user)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('links_blog.addpost'))


@links_blog.route('/delete',methods=['POST'])
def delete():
    delete=posts.query.filter(posts.id==request.form['id']).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('links_blog.blog',page_num=1))



@links_blog.route('/search')
def search():
    search=request.args.get('search')
    search_result=posts.query.filter(posts.title.like("%" + search + "%")).all()
    print("-*-*-*-*-*-*-*-*-*-*-*-*")
    print(search_result)
    #return render_template('links/blog.html',posts=search_result)
    return render_template('links/search.html',blogPage=search_result)


@links_blog.route('/post/<id>/edit')
def edit(id):
    update_this=posts.query.filter(posts.id==id).first()
    messages = None
    if request.args.get('messages') is not None:
        messages =json.loads(request.args.get('messages'))
    return render_template('links/editpost.html',post=update_this,errors=messages)


@links_blog.route('/editpost',methods=['POST'])
def editpost():
    #page=request.args.get(str('/page/<int:page_num>'))
    update_this=posts.query.filter(posts.id==request.form['id']).first()
    update_this.title = request.form['title']
    update_this.content=request.form['content']
    if len(request.form['title'])<2:
        return redirect(url_for('edit',id=update_this.id,messages=json.dumps({'title':'Enter longer title'})))
    if request.files['image']:
        pict=update_this.image
        os.remove('static/images/' + pict)  
        file=request.files['image']    
        filename = secure_filename(file.filename)
        update_this.image = filename
        file.save(os.path.join('static/images' , filename))
    db.session.commit()

    return redirect(url_for('links_blog.blog',page_num=1))


@links_blog.route('/addComment',methods=['POST'])
def addComment():
    user_com = users.query.filter(users.id==session['user']['id']).first()
    post_com = posts.query.filter(posts.id==request.form['post_id']).first()
    comm=comment(text=request.form['text'],user_com=user_com,post_com=post_com)
    db.session.add(comm)
    db.session.commit()
    return redirect(url_for('links_blog.singlePage',id=request.form['post_id']))

@links_blog.route('/deleteComment',methods=['POST'])
def delComm():
    delete=comment.query.filter(comment.id==request.form.get('com_id')).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('links_blog.singlePage',id=request.form.get('id')))