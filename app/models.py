from app import db,app,ma
from datetime import datetime
import re
import flask_permissions 
from flask_login import UserMixin
from sqlalchemy import Column, types,FLOAT
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
Base = declarative_base()
engine = create_engine('mysql+mysqlconnector://root:''@localhost/newpyproject', convert_unicode=True)


class users(db.Model,UserMixin):
    __table_args__ = {'extend_existing': True} 
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True)
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(200))
    posts=db.relationship('posts',backref='user')
    comment=db.relationship('comment',backref='user_com')
    picture=db.Column(db.String(1000))
    product=db.relationship('Product',backref='product_user')
    cart_user=db.relationship('cart',backref='cart_user')
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    user_order=db.relationship('Orders',backref='user_order')
    user_role=db.relationship('role_user',backref='username')
   
    def __init__(self,*args,**kwargs):
        super(users,self).__init__(*args,**kwargs)

    #def set_password(self, password):
     #   self.password = generate_password_hash(password)

#    def check_password(self, password):
 #       return check_password_hash(self.password, password)
    
    def __repr__(self):
        return self.username
   
class roles(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True} 
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),unique=True)
    role_id = db.relationship('role_user', backref='role_users')
    user_role = db.relationship('users', backref='user_roles', lazy='dynamic')
    
    def __init3__(self,*args,**kwargs):
        super(roles,self).__init3__(*args,**kwargs)

    def __repr__(self):
        return self.name

class role_user(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __init10__(self,*args,**kwargs):
        super(role_user,self).__init10__(*args,**kwargs)
    
    def __repr__(self):
        return str(self.id)

class posts(db.Model):
    __table_args__ = {'extend_existing': True} 
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100))
    content=db.Column(db.Text())
    image=db.Column(db.String(100))
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    comment=db.relationship('comment',backref='post_com')
        
    def __init1__(self,*args,**kwargs):
        super(posts,self).__init1__(*args,**kwargs)

    def __repr__(self):
        return' {} '.format(self.title)


class comment(db.Model):
    __table_args__ = {'extend_existing': True}
    id=db.Column(db.Integer,primary_key=True)
    text=db.Column(db.String(200))
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))


    def __init2__(self,*args, **kwargs):
        super(comment,self).__init2__(*args,**kwargs)

    def __repr__(self):
        # return'<id:{},text:{} >'.format(self.id,self.text)
        return str({"id":self.id,"text":self.text})


class Product(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(255))
    price=db.Column(db.FLOAT)
    category=db.relationship('Category',backref=db.backref('products',lazy='dynamic'))
    company=db.Column(db.String(100))
    product_picture=db.Column(db.String(100))
    category_id=db.Column(db.Integer,db.ForeignKey('category.id'))
    image=db.relationship('images',backref='prodImages')
    description=db.Column(db.Text())
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    cart=db.relationship('cart',backref='cart_product')
    def __init4__(self,*args, **kwargs):
        super(Product,self).__init4__(*args,**kwargs)

    def __repr__(self):
        return self.name

class Category(db.Model):
    __table_args__ = {'extend_existing': True}
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    
    def __init5__(self,*args, **kwargs):
        super(Category,self).__init5__(*args,**kwargs)

    def __repr__(self):
       # return'<Category id:{},name:{} >'.format(self.id,self.name)
        return self.name



class images(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer,primary_key = True)
    image=db.Column(db.String(200))
    product_id=db.Column(db.Integer,db.ForeignKey('product.id'))
    def __init6__(self,*args, **kwargs):
        super(images,self).__init6__(*args,**kwargs)

    def __repr__(self):
       
        return'<images id:{},image:{},product_id:{} >'.format(self.id,self.image,self.product_id)



class cart(db.Model):
    __table_args__ = {'extend_existing': True}
    id=db.Column(db.Integer,primary_key=True)
    qty=db.Column(db.Integer)
    priceItem=db.Column(db.FLOAT)
    product_id=db.Column(db.Integer,db.ForeignKey('product.id'))
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
   
    def __init7__(self,*args, **kwargs):
        super(cart,self).__init7__(*args,**kwargs)

    def __repr7__(self):
        return'<cart id:{} >'.format(self.id)


class Orders(db.Model):
    __table_args__ = {'extend_existing': True}
    id=db.Column(db.Integer,primary_key=True)
    order=db.relationship('orderItems',backref='order')
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    

    def __init8__(self,*args,**kwargs):
        super(Orders,self).__init8__(*args,**kwargs)

    def __repr__(self):
        return format(self.id)

class orderItems(db.Model):
    __table_args__ = {'extend_existing': True}
    id=db.Column(db.Integer,primary_key=True)
    order_id=db.Column(db.Integer,db.ForeignKey('orders.id'))
    product=db.Column(db.String(100))
    price=db.Column(db.FLOAT)
    qty=db.Column(db.Integer)
    amount=db.Column(db.FLOAT)
    

    def __init9__(self,*args,**kwargs):
        super(orderItems,self).__init9__(*args,**kwargs)
    
    def __repr__(self):
        return'<orderItems id:{} >'.format(self.id)

class StorageModel(db.Model):
    __tablename__ = 'storage'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))
    type = db.Column(db.Unicode(3))
    create_date = db.Column(db.DateTime, default=datetime.now)




db.metadata.reflect(engine)


class ProductSchema(ma.ModelSchema):
    class Meta:
        model=Product

class CategorySchema(ma.ModelSchema):
    class Meta:
        model=Category

class cartSchema(ma.ModelSchema):
    class Meta:
        model=cart