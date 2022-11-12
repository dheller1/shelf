import os
from flask import Flask, send_file, redirect, render_template, request, url_for

from shelf.db import db, Author

from . import commands
from shelf.db.book import Book

_basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(_basedir, 'shelf.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/add', methods=('GET', 'POST'))
def view_add():
    if request.method == 'POST':
        b = commands.add_book(db, request, app.logger)
        if b is not None:
            return redirect(url_for('view_edit', book_id=b.id))
        else:
            return render_template('add.html')
    else:
        return render_template('add.html')

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

@app.route('/file/<int:book_id>')
def view_file(book_id):
    book = Book.query.get_or_404(book_id)
    path = book.abs_filepath()
    if path and os.path.isfile(path):
        return send_file(path, download_name=book.filename)
    return render_template('edit.html', book=book)

@app.route('/save', methods=('POST', ))
def do_save():
    if request.method == 'POST':
        id = request.form['book_id']
        book = Book.query.get_or_404(id)
        t = request.form['title']
        st = request.form['subtitle']
        ed = request.form['edition']
        author_str = request.form['authors']

        author_str = author_str.replace(',', '\n')
        author_str = author_str.replace(';', '\n')
        authors = [a.strip() for a in author_str.split('\n')]
        print(authors)
        book.title = t
        book.subtitle = st
        book.edition = ed
        book.authors = [Author.get_or_create(name) for name in authors if name != '']

        db.session.add(book)
        db.session.commit()
        return redirect(url_for('view_book', book_id=id))
