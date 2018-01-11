from flask import Flask, flash, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = '$J\x85\xc98\xddU\x12\x82k\x96C\x83\\Uy\x819\xed>\xbb\xc86\xf1'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    create_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.create_date = datetime.datetime.utcnow()
        self.owner = owner

    def is_valid(self):
        if self.title and self.body:
            return True
        else:
            return False

class User(db.Model):

     id = db.Column(db.Integer, primary_key = True)
     username = db.Column(db.String(20))
     password = db.Column(db.String(20))
     blogs = db.relationship('Blog', backref='owner')

     def __init__(self, username, password):
         self.username = username
         self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'signup', 'all_blog_entries']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/", methods=['POST','GET'])#####DON'T CHANGE!
def index():

    users = User.query.all()
    return render_template('index.html', users=users)


@app.route("/login", methods=['POST', 'GET'])####DON'T CHANGE!!!
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route("/home")
def home():
    blogs= Blog.query.all()
    return render_template('/blog', blogs=blogs)


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

#TODO validate user's data
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/home')
        else:
            return "<h1>Duplicate user</h1>"
    return render_template('signup.html')

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/login')



@app.route("/blog", methods = ['POST', 'GET'])
def all_blog_entries():
    post_entries = User.query.all()
    entry_id = request.args.get('blog.id')
    userId =request.args.get('userId')

    #if entry_id:
    #    blog = Blog.query.get(entry_id)
    #    return render_template('ind_entry.html',title = "Blog Entry", blog=blog)
    if request.args.get('user'):
        username = request.args.get('user')
        user = User.query.filter_by(username=username).first()
        blogs = Blog.query.filter_by(owner_id=user.id)
        return render_template('all_entries.html', blogs=blogs)

    if request.args.get('blog_id'):
        blog_id = request.args.get('blog_id')
        blog = Blog.query.filter_by(id=blog_id).first()
        blog_list = {blog}
        return render_template('all_entries.html', blogs=blog_list)

    blogs = Blog.query.all()
    return render_template('all_entries.html', blogs=blogs)
    #sort = request.args.get('sort')
    #if(sort=="newest"):

        #all_entries = Blog.query.order_by(Blog.create_date.desc()).all()
    #else:
    #    all_entries = Blog.query.order_by(Blog.create_date.desc()).all()
    #    return render_template('all_entries.html', title = "All Entries", all_entries=all_entries)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    blog_owner_id = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        new_post_title= request.form['new_post']
        new_post_body = request.form['body']

        blog = Blog(new_post_title, new_post_body, blog_owner_id)

        body_error = ''
        title_error = ''

        #if blog.is_valid():
        blog=Blog(new_post_title, new_post_body, blog_owner_id)
        db.session.add(blog)
        db.session.commit()
        blog_list={blog}
        return render_template('all_entries.html', blogs=blog_list)

            #url = '/blog?id=' + str(newpost.id)
            #return redirect(url)

        if not new_post_title:
            title_error = 'Please enter a title'
        if not new_post_body:
            body_error = 'Please enter text'
            return render_template('newpost.html', title = 'Create new blog entry', new_post_title = new_post_title, new_post_body=new_post_body,blog_owner_id=blog_owner_id, title_error=title_error, body_error=body_error)
    else:
        return render_template('newpost.html', title = 'Create new blog entry')




if __name__ == '__main__':
    app.run()
