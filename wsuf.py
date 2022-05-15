# from flask import Flask, render_template

import json
from flask import Flask, render_template,request,session
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from flask_mail import Mail

 

local_server=True
app = Flask(__name__)
app.secret_key= 'super-secret-key'

with open('config.json' , 'r') as c:
    prms=json.load(c)["prms"]

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = prms['gmail-user'],
    MAIL_PASSWORD = prms['gmail-password']
)
mail = Mail(app)




if (local_server):

    app.config['SQLALCHEMY_DATABASE_URI'] =prms ['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] =prms ['prod_uri']

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/culturecode'

db = SQLAlchemy(app)



class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    subtitle=db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file= db.Column(db.String(12), nullable=True)




@app.route("/" , methods=['GET'])
def home():
    posts = Posts.query.filter_by(). all()  [0: 4]
    return render_template('index.html', prms=prms,posts=posts )

    # posts = Posts.query.filter_by(). all() [0:prms['no_of_po']]
        # return render_template('index.html' ,prms = prms, posts=posts)

@app.route("/sp/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post= Posts.query.filter_by(slug=post_slug). first()
    return render_template('post.html', prms=prms, post=post)


@app.route("/about")
def about():
    return render_template('about.html', prms=prms)



    
@app.route("/dashboard",methods=['GET' , 'POST'])
def dashboard():
    if "user" in session and session['user']==prms['user_name']:
        # posts = Posts.querry.all()
        return render_template("dasbord.html", prms=prms )

    if request.method=="POST":
        username = request.form.get("uname")
        userpass = request.form.get("upass")
        if username==prms['user_name'] and userpass==prms['user_pass']:
            # set the session variable
            session['user']=username
            # posts = Posts.querry.all()
            return render_template("dasbord.html", prms=prms )
    else:
        return render_template("login.html", prms=prms)

# @app.route("/dashboard" , methods=['GET' ,'POST' ] )
# def dashboard():

#     if "user" in session and session['user']==prms['user_name']:

#         return render_template('dasbord.html',prms=prms)
    

#     if request.method == "POST":
#         user_nm=request.form.get('uname')
#         user_pw=request.form.get('pass')

#         if user_nm==prms['user_name'] and user_pw==prms['user_pass']:
#              session['user']=user_nm
#              return render_template('dasbord.html' ,prms=prms)
#     else:
#         return render_template('login.html', prms=prms)


@app.route("/cnt", methods = ['GET', 'POST'] )
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contact(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,sender=email,
                          recipients = [prms['gmail-user']],
                          body = message + "\n" + phone
                          )
        # engine = create_engine("mysql+pymysql://root:@localhost/culturecode", pool_pre_ping=True)

    return render_template('contact.html' , prms=prms)


app.run(debug=True)
