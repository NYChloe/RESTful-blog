import datetime
import bleach
# from datetime import date
from flask import Flask, render_template, redirect, url_for,request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor, CKEditorField
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    # use CKEditor
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

## strips invalid tags/attributes
def strip_invalid_html(content):
    allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br', 'div', 'dl', 'dt',
                    'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
                    'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike',
                    'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
                    'thead', 'tr', 'tt', 'u', 'ul']

    allowed_attrs = {
        'a': ['href', 'target', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
    }

    cleaned = bleach.clean(content,
                           tags=allowed_tags,
                           attributes=allowed_attrs,
                           strip=True)

    return cleaned




@app.route('/')
def get_all_posts():
    # posts=db.session.query(BlogPost).all()
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


@app.route("/new_post", methods=["GET", "POST"])
def make_post():
    form = CreatePostForm()
    if request.method == "POST":
        new_post = BlogPost(
            title=request.form.get('title'),
            subtitle=request.form.get("subtitle"),
            author=request.form.get("author"),
            img_url=request.form.get("img_url"),
            body=request.form.get("body"),
            date=datetime.datetime.now().strftime("%B %d %Y")
        )
    #if form.validate_on_submit():
    #    new_post = BlogPost(
    #        title=form.title.data,
    #        subtitle=form.subtitle.data,
    #        author=form.author.data,
    #        img_url=form.img_url.data,
    #        body=strip_invalid_html(form.body.data),
    #        date=datetime.datetime.now().strftime("%B %d %Y")
    #    )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form=form)


@app.route("/edit_post/<int:post_id>",methods=["GET","POST"])
def edit_post(post_id):
    post_to_edit=BlogPost.query.get(post_id)
    edit_form=CreatePostForm(
        #title=post_to_edit.title,
        #subtitle=post_to_edit.subtitle,
        #img_url=post_to_edit.img_url,
        #author=post_to_edit.author,
        #body=post_to_edit.body
        obj=post_to_edit
    )
    intention='edit'
    if edit_form.validate_on_submit():
        post_to_edit.title=edit_form.title.data
        post_to_edit.subtitle=edit_form.subtitle.data
        post_to_edit.img_url=edit_form.img_url.data
        post_to_edit.author=edit_form.author.data
        post_to_edit.body=edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post',post_id=post_to_edit.id))
    return render_template("make-post.html",form=edit_form,intention=intention)


@app.route('/delete/<post_id>')
def delete_post(post_id):
    post_to_delete=BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))






@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
