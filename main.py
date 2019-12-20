from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blog_z:password@localhost:8889/blog_z'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "90234890uffds02"


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','home', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog')
def index():
    posts = Blog.query.all()

    if request.args.get('id'):
        post_id = request.args.get('id')
        posts = Blog.query.filter_by(id=post_id).all()

    if request.args.get('userId'):
        user_id = request.args.get('userId')
        posts = Blog.query.filter_by(user_id=user_id).all()

    return render_template('todos.html', posts=posts, page_title="Build A Blog")   


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    missing_title = ""
    missing_body = ""

    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        title = request.form['title']
        body = request.form['body']
        strikes = 0 

        if len(title) == 0:
            strikes += 1
            missing_title = ("Missing Title")
            
        if len(body) == 0:
            strikes += 1
            missing_body = ('Missing Body')
        
        if strikes == 0: 
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_post.id))
           
    return render_template('add_post.html', missing_body=missing_body, missing_title=missing_title)

@app.route('/login', methods=['POST', 'GET'])
def login():

    login_error = ""
    
    if request.method == "POST":
        password = request.form['password']
        username = request.form['username']

        #some validators
        dbUsername = User.query.filter_by(username=username).first()
        dbPassword = User.query.filter_by(password=password).first()
        if dbUsername and dbPassword:
            session['username'] = username
            return redirect('/blog')
        else:
            login_error = "Username or password do not match"

    return render_template('login.html', login_error=login_error)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')
    

@app.route('/signup', methods=['POST','GET'])
def signup():

    pswd_ver = ""
    username_error = ""
    pswd_error = ""

    if request.method == "POST":
        password = request.form['password']
        username = request.form['username']
        verify = request.form['verify']

        strikes = 0 

        if len(password) < 3 or len(password) > 20 or " " in password:
            strikes += 1
            pswd_error = ("Invalid Password")
        
        if verify != password:
            strikes += 1
            pswd_ver = ("Password does not match")
           
        if len(username) < 3 or len(username) > 20 or " " in username:
            strikes += 1
            username_error = ("Username must be between 3 and 20 characters.")
        
        if strikes == 0:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog?')
        
    return render_template('signup.html', pswd_error=pswd_error, username_error=username_error, pswd_ver=pswd_ver)

@app.route("/")
def home(): 
    users = User.query.all()
    return render_template('home.html', users=users, page_title="Users")

if __name__ == '__main__':
    app.run()