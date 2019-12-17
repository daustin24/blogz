from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))

    def __init__(self, title, body, username, password):
        self.title = title
        self.body = body
        self.username = username
        self.password = password


@app.route('/blog', methods=['GET', 'POST'])
def index():
    posts = Blog.query.all()

    if request.args.get('id'):
        post_id = request.args.get('id')
        single_post = Blog.query.get(post_id)
        return render_template('view_post.html', post=single_post)
    return render_template('todos.html', posts=posts, page_title="Build A Blog")   


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        strikes = 0 
        missing_title = ""
        missing_body = ""

        if len(title) == 0:
            strikes += 1
            missing_title = ("Missing Title")
            
        if len(body) == 0:
            strikes += 1
            missing_body = ('Missing Body')
        
        if strikes == 0: 
            new_post = Blog(title,body)
            db.session.add(new_post)
            db.session.commit()

            return redirect('/blog?id=' + {{post.id}}) 
        else:            
            return render_template('add_post.html', title=title, body=body, missing_body=missing_body, missing_title=missing_title )
           
    return render_template('add_post.html')


@app.route('/sign_up', methods=['POST','GET'])
def index():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        verify = request.form['verify']

        strikes = 0 
        pswd_ver = ""
        email_error = ""
        username_error = ""
        pswd_error = ""

        if len(password) < 3 or len(password) > 20 or " " in password:
            strikes += 1
            pswd_error = ("Invalid Password")
        
        if verify != password:
            strikes += 1
            pswd_ver = ("Password does not match")
           
        if len(username) < 3 or len(username) > 20 or " " in username:
            strikes += 1
            username_error = ("Username must be between 3 and 20 characters.")
        
        if email:
            if email.count('@') != 1 or email.count('.') != 1 or email.count(" ") > 0:
                strikes += 1
                email_error = ("Invalid Email Address")
        
        if strikes == 0:
            return redirect('/welcome?username=' + username)
        else:
            return render_template('singup.html', pswd_error=pswd_error, username_error=username_error, email_error=email_error, pswd_ver=pswd_ver, verify=verify, username=username, email=email)

    return render_template('signup.html')


@app.route("/welcome")
def welcome(): 
    username = request.args.get('username')
    return render_template('welcome.html', username=username)

app.run()