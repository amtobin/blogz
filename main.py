from flask import Flask, flash, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = '$J\x85\xc98\xddU\x12\x82k\x96C\x83\\Uy\x819\xed>\xbb\xc86\xf1'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    create_date = db.Column(db.DateTime)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.create_date = datetime.datetime.utcnow()

    def is_valid(self):
        if self.title and self.body and self.create_date:
            return True
        else:
            return False

@app.route("/")
def index():
    return redirect('/blog')

@app.route("/blog")
def display_blog_entries():
    entry_id = request.args.get('id')
    if(entry_id):
        blog = Blog.query.get(entry_id)
        return render_template('ind_entry.html',title = "Blog Entry", blog=blog)

    sort = request.args.get('sort')
    if(sort=="newest"):
        all_entries = Blog.query.order_by(Blog.create_date.desc()).all()
    else:
        all_entries = Blog.query.all()
    return render_template('all_entries.html', title = "All Entries", all_entries=all_entries)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        new_post_title= request.form['new_post']
        new_post_body = request.form['body']
        newpost = Blog(new_post_title, new_post_body)

        body_error = ''
        title_error = ''

        if newpost.is_valid():
            db.session.add(newpost)
            db.session.commit()

            url = '/blog?id=' + str(newpost.id)
            return redirect(url)
        else:
            if not new_post_title:
                title_error = 'Please enter a title'
            if not new_post_body:
                body_error = 'Please enter text'
                return render_template('newpost.html', title = 'Create new blog entry', new_post_title = new_post_title, new_post_body=new_post_body,title_error=title_error, body_error=body_error)
    else:
        return render_template('newpost.html', title = 'Create new blog entry')


if __name__ == '__main__':
    app.run()
