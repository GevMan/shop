import os
import os.path as op
from app import app, db, ma, manage, cache, mail
from flask import Flask, render_template, redirect, url_for, request, session, flash, json, make_response, current_app, \
    jsonify, Response, abort
from models import users, posts, comment, Category, Product, images, cart, roles, role_user, StorageModel, \
    Orders, orderItems, ProductSchema, CategorySchema, cartSchema
from sqlalchemy import exc, desc, select
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message
from validate_email import validate_email
import datetime
from datetime import timedelta, datetime
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, login_manager, current_user
from json import JSONEncoder
from flask_admin.contrib import sqla
from flask_admin import Admin, AdminIndexView, form
from flask_admin.contrib.sqla import ModelView
from flask_menu import Menu, register_menu
from flask_admin.menu import MenuLink
from flask_admin.helpers import get_form_data
from flask_admin.babel import gettext
from flask_admin import expose
from flask_user import login_required, UserManager, UserMixin, roles_required, roles_accepted, user_manager
from flask_paginate import Pagination, get_page_parameter, get_page_args, CURRENT_PAGES
import sys
from werkzeug.datastructures import FileStorage, ImmutableMultiDict, MultiDict
from werkzeug.exceptions import Unauthorized
from jinja2 import Markup
import random
from werkzeug.security import generate_password_hash, check_password_hash

manage.create_api(Product)
manage.create_api(Category)
product_schema = ProductSchema(many=True)
category_schema = CategorySchema(many=True)
cart_schema = cartSchema(many=True)


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated


Admin = Admin(app, index_view=MyAdminIndexView())

Admin.add_view(MyModelView(users, db.session))
Admin.add_view(MyModelView(roles, db.session))
Admin.add_view(MyModelView(posts, db.session))
Admin.add_view(MyModelView(comment, db.session))
Admin.add_view(MyModelView(Product, db.session))
Admin.add_view(MyModelView(Category, db.session))
Admin.add_view(MyModelView(images, db.session))
Admin.add_view(MyModelView(cart, db.session))
Admin.add_view(MyModelView(Orders, db.session))
Admin.add_view(MyModelView(orderItems, db.session))
Admin.add_view(MyModelView(role_user, db.session))


class LogoutMenuLink(MenuLink):

    def is_accessible(self):
        return current_user.is_authenticated


Admin.add_link(LogoutMenuLink(name='Log Out', category='', url="/logout"))


class StorageAdminModel(sqla.ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        url = url_for('static', filename=os.path.join('storage/', model.path))

        if model.type in ['jpg', 'jpeg', 'png', 'svg', 'gif']:
            return Markup('<img src="%s" width="100">' % url)

    column_formatters = {
        'path': _list_thumbnail
    }

    form_extra_fields = {
        'file': form.FileUploadField('file', '', app.config['STORAGE'])
    }

    def _change_path_data(self, _form):

        try:
            storage_file = _form.file.data

            if storage_file is not None:
                hash = random.getrandbits(128)
                ext = storage_file.filename.split('.')[-1]
                path = '%s.%s' % (hash, ext)

                storage_file.save(
                    os.path.join(app.config['STORAGE'], path)
                )

                _form.name.data = _form.name.data or storage_file.filename
                _form.path.data = path
                _form.type.data = ext

                del _form.file

        except Exception as ex:
            pass
        return _form

    def edit_form(self, obj=None):
        return self._change_path_data(
            super(StorageAdminModel, self).edit_form(obj)
        )

    def create_form(self, obj=None):
        return self._change_path_data(
            super(StorageAdminModel, self).create_form(obj)
        )


Admin.add_view(StorageAdminModel(StorageModel, db.session))

app.secret_key = 'zzz'
app.config['REMEMBER_COOKIE_DURATION '] = timedelta(days=7)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = ''


@login_manager.user_loader
def load_user(id):
    return users.query.get(int(id))


@app.route('/signup')
# @cache.cached(timeout=50)
def reg():
    messages = None
    if request.args.get('messages') is not None:
        messages = json.loads(request.args.get('messages'))

    return render_template('reg.html', errors=messages)


@app.route('/register', methods=['POST'])
def register():
    messages = dict()
    res = users.query.filter(users.username == request.form['username']).first()
    if not res:
        res = users.query.filter(users.email == request.form['email']).first()

    try:

        if res and res.username == request.form['username']:
            messages['username'] = 'Username already exists!'

        if len(request.form['username']) < 1:
            messages['username'] = 'Username is not valid!'

        if res and res.email == request.form['email']:
            messages['email'] = 'Email already exists!'

        if len(request.form['password']) < 8:
            messages['password'] = 'Password is too short,enter min 8 symbols!'

        if len(request.form['password']) < 1:
            messages['password'] = 'Password is not valid'

        if request.form['password'] != request.form['confpass']:
            messages['confpass'] = 'Passwords must match'

        if not validate_email(request.form['email']):
            messages['email'] = 'Email is not valid'

        if len(messages) > 0:
            return redirect(url_for('reg', messages=json.dumps(messages)))

        user = users(username=request.form['username'], email=request.form['email'], password=request.form['password'])
        # user.set_password('P@ssw0rd')
        db.session.add(user)
        db.session.commit()

        if request.form.get('exampleRadios') == 'Seller':
            user_role = role_user(user_id=user.id, role_id=2)
            db.session.add(user_role)
            db.session.commit()
        elif request.form.get('exampleRadios') == 'Buyer':
            user_role = role_user(user_id=user.id, role_id=3)
            db.session.add(user_role)
            db.session.commit()
        return redirect(url_for('login'))

    except exc.IntegrityError as e:
        db.session().rollback()

        return redirect(url_for('reg', messages=json.dumps(messages)))


@app.route('/login/')
def login():
    return render_template('login.html', error=None)


@app.route('/logoutUser')
def logout():
    session.pop('logged_in')
    session.clear()
    return redirect(url_for('login'))


@app.route('/logout')
def logout_admin():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    # password = request.form['password']
    user = users.query.filter(
        db.and_(users.username == request.form['username'], users.password == request.form['password'])).first()
    # user_role=role_user.query.filter(db.and_(users.id=session['user']['id'],role_user.role_id==1)).first()
    if user == None:
        error = 'Please try again'
        return render_template('login.html', error=error)

    if user != None:

        if user.role_id == 1:
            login_user(user)
            user = users.query.get(user.id)
            return (redirect(url_for('admin.index')))
        else:
            session['logged_in'] = True
            session['user'] = dict()
            session['user']['id'] = user.id
            session['user']['username'] = username

            return (redirect(url_for('links.index')))


@app.route('/test/')
def test():
    msg = Message('Hello', sender='admin@gmail.com', recipients=['gevman97@gmail.com'])
    msg.html = '<b>hi, this is the mail sent by using the flask web application</b>'
    mail.send(msg)
    return "sent"



@app.route('/shop')
@app.route('/shop/page/<int:page_num>')
def shop(page_num):
    messages = []
    if request.args.get('messages') is not None:
        messages = json.loads(request.args.get('messages'))

    shopPage = Product.query.order_by(Product.id.desc()).paginate(page=page_num, per_page=6, error_out=True)
    product = Product.query.order_by(Product.id.desc()).all()
    user = None
    if session is True:
        user = users.query.filter(users.id == session['user']['id']).first()
    categories = Category.query.all()
    allCart = cart.query.all()
    storage = StorageModel.query.all()
    user_perm = users.query.all()
    return render_template('shop.html', shopPage=shopPage, categories=categories, product=product, user_id=user,
                           errors=messages, cart=allCart, storage=storage, user_perm=user_perm)


@app.route('/category_filter', methods=['GET'])
def category_filter():
    category = Product.query.filter(Product.category_id == request.form['category_id']).all()

    output = product_schema.dump(category).data
    return jsonify({"product": output})


@app.route('/product-create', methods=['GET', 'POST'])
def create_product():
    role_id = role_user.query.filter(role_user.user_id == session['user']['id']).all()

    role = []
    for i in role_id:
        role.append(i.role_id)
    if 2 in role:

        if request.method == 'POST':
            product_user = users.query.filter(users.id == session['user']['id']).first()
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            image_file = request.files['image[]']
            file = request.files['product_picture']
            image = secure_filename(str(timestamp) + image_file.filename)
            filename = secure_filename(str(timestamp) + file.filename)
            image_file.save(os.path.join('app/static/product_picture', image))
            file.save(os.path.join('app/static/product_picture', filename))
            product = Product(name=request.form['name'], price=request.form['price'],
                              category_id=request.form['category'], company=request.form['company'],
                              product_picture=filename,
                              description=request.form['description'], product_user=product_user)
            db.session.add(product)
            db.session.commit()
            flash('The product %s has been created' % product.id, 'success')
            img = images(image=image, product_id=product.id)
            db.session.add(img)
            db.session.commit()

            return redirect(url_for('create_product', id=product.id))
    else:
        flash('Please sign in as seller', 'error')
        return redirect(url_for('shop', page_num=1))
    categories = Category.query.all()
    messages = None
    if request.args.get('messages') is not None:
        messages = json.loads(request.args.get('messages'))
    return render_template('product-create.html', categories=categories, errors=messages)


@app.route('/delete-product', methods=['POST'])
def delete_product():
    delete = Product.query.filter(Product.id == request.form.get('id')).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('shop', page_num=1))


@app.route('/product/<id>/edit')
def edit(id):
    update_product = Product.query.filter(Product.id == id).first()
    categories = Category.query.all()
    return render_template('edit_product.html', product=update_product, categories=categories)


@app.route('/edit_product', methods=['POST'])
def edit_product():
    update_product = Product.query.filter(Product.id == request.form['id']).first()
    update_product.name = request.form['name']
    update_product.price = request.form['price']
    update_product.category_id = request.form['category']
    update_product.company = request.form['company']
    update_product.description = request.form['description']

    if request.files['picture']:
        pict = update_product.product_picture
        os.remove('static/product_picture/' + pict)
        file = request.files['picture']
        filename = secure_filename(file.filename)
        update_product.product_picture = filename
        file.save(os.path.join('static/product_picture', filename))
    db.session.commit()
    return redirect(url_for('shop', page_num=1))


@app.route('/category-create', methods=['POST'])
def create_category():
    messages = dict()
    if request.method == 'POST':
        category = Category(name=request.form['category'])
        db.session.add(category)
        db.session.commit()
    messages['addCategory'] = request.form.get('category')
    return jsonify(messages)


@app.route('/categories')
def categories():
    categories = Category.query.all()
    res = {}
    for category in categories:
        res[category.id] = {
            'name': category.name,
        }
    for product in category.products:
        res[category.id]['products'] = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
        }
    return jsonify(res)


@app.route('/product/<id>')
def product(id):
    product = Product.query.get_or_404(id)
    user_id = users.query.all()
    return render_template('product.html', product=product, user_id=user_id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.context_processor
def context_processor():
    items = cart.query.all()
    q = 0
    if session.get('logged_in') == True:
        for i in items:
            if i.user_id == session['user']['id']:
                q = q + 1
    return dict(key=q)


@app.route('/shopping_cart')
def shopping_cart():
    items = cart.query.all()
    product = Product.query.order_by(Product.id.desc()).all()
    order = orderItems.query.all()
    order_id = Orders.query.all()
    if cart.product_id == Product.id:
        cart.qty += 1
    return render_template('shopping-cart.html', cart_items=items, product=product, order=order, order_id=order_id)


@app.route('/add_item', methods=['POST'])
def addItem():
    messages = dict()
    role_id = role_user.query.filter(role_user.user_id == session['user']['id']).all()
    role = []
    for i in role_id:
        role.append(i.role_id)
    if 3 in role:
        if not session.get('logged_in'):
            return (redirect(url_for('login')))
        if int(request.form.get('items')) < 1:
            messages[request.form.get('product_id')] = ' Minimum qty must be 1! '
            return redirect(url_for('shop', page_num=1, messages=json.dumps(messages)))
    else:
        flash('Please sign in as buyer', 'error')
        return redirect(url_for('shop', page_num=1))
    productById = cart.query.filter(
        db.and_(cart.product_id == request.form.get('product_id'), cart.user_id == session['user']['id'])).first()
    newItem = cart(qty=request.form.get('items'), priceItem=request.form.get('price'),
                   product_id=request.form.get('product_id'), user_id=session['user']['id'])
    if productById is None:
        db.session.add(newItem)
        db.session.commit()
    else:
        productById.qty += int(newItem.qty)
        db.session.commit()

    return redirect(url_for('shop', page_num=1, messages=json.dumps(messages)))


@app.route('/update_cart', methods=['POST'])
def updateCart():
    cartById = cart.query.filter(cart.id == request.form['id']).first()
    productById = Product.query.filter(Product.id == cartById.product_id).first()
    info = {}
    update_cart = cart.query.filter(
        db.and_(cart.id == request.form['id'], cart.user_id == session['user']['id'])).first()
    update_cart.qty = request.form['qty']
    db.session.commit()
    info['id'] = cartById.id
    info['qty'] = cartById.qty
    info['price'] = productById.price
    info['success'] = True
    return jsonify(info)


@app.route('/delete_cart', methods=['POST'])
def deleteCart():
    delete = cart.query.filter(cart.id == request.form.get('id')).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('shopping_cart'))


@app.route('/orders', methods=['POST'])
def orders():
    orderByUser = cart.query.filter(cart.user_id == session['user']['id']).all()

    user_order = Orders(user_id=session['user']['id'])
    db.session.add(user_order)
    db.session.commit()
    ord = Orders.query.all()
    for newOrder in orderByUser:

        amounts = newOrder.qty * newOrder.priceItem

        delete = cart.query.filter(cart.user_id == session['user']['id']).first()
        db.session.delete(delete)

        for i in ord:
            k = orderItems(product=newOrder.product_id, qty=newOrder.qty, price=newOrder.priceItem, amount=amounts,
                           order_id=i.id)
        db.session.add(k)
        db.session.commit()
    mail_user = users.query.filter(users.id == session['user']['id']).all()
    with mail.connect() as conn:
        for us in mail_user:
            order_id = orderItems.query.filter(Orders.id == orderItems.order_id).order_by(Orders.id.desc()).first()

            orderByus = Orders.query.filter(
                db.and_(Orders.id == orderItems.order_id, Orders.user_id == session['user']['id'])).all()

            prodName = Product.query.filter(Product.id == orderItems.product).first()


            for byUs in orderByus:
                orderItemsByUser = orderItems.query.filter(
                    db.and_(Orders.id == orderItems.order_id, Orders.user_id == session['user']['id'])).all()
                for itemsByuser in orderItemsByUser:
                    message = 'This is your purchase' + '<br>' + 'name: ' + str(byUs.id) + '<br>' \
                                                                                           'qty:' + str(
                        itemsByuser.qty) + '<br>' \
                                           'price:' + str(itemsByuser.price) + '$' + '<br>' \
                                                                                     'Amount:' + str(
                        itemsByuser.amount) + '$' + '<br>'

                    subject = "Your Purchase  %s" % us.username
                    msg = Message(recipients=[us.email],
                                  html=message,
                                  subject=subject)
            conn.send(msg)
    return redirect(url_for('shopping_cart'))
