import os
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

_basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(_basedir, 'shelf.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'Author({self.name})'


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200))
    edition = db.Column(db.String(100))

    def __repr__(self):
        return f'Book({self.title})'



@app.route('/list')
def view_list():
    books = Book.query.all()
    return render_template('list.html', books=books)

@app.route('/book/<int:book_id>')
def view_book(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book.html', book=book)

@app.route('/edit/<int:book_id>')
def view_edit(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('edit.html', book=book)

@app.route('/save', methods=('POST', ))
def do_save():
    if request.method == 'POST':
        id = request.form['book_id']
        book = Book.query.get_or_404(id)
        t = request.form['title']
        st = request.form['subtitle']
        ed = request.form['edition']

        book.title = t
        book.subtitle = st
        book.edition = ed

        db.session.add(book)
        db.session.commit()
        return redirect(url_for('view_book', book_id=id))
