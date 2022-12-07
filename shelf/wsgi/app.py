import os
from flask import Flask, send_file, redirect, render_template, request, url_for

from shelf.db import db, Author, Tag, Attachment
from shelf.db.book import Book
from . import commands


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
    tag_ids = request.args.getlist('tag')
    if tag_ids:
        filter_tags = Tag.get(tag_ids)
        books = set()

        # FIXME: Is there a better way to do this in one query, instead of one query per tag?
        for t in filter_tags:
            tagged_books = Book.query.filter(Book.tags.contains(t)).all()
            books.update(tagged_books)
        books = list(books)
        return render_template('list.html', books=books, tags=filter_tags)
    else:
        books = Book.query.all()
        return render_template('list.html', books=books, tags=[])


@app.route('/tags')
def view_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('tags.html', tags=tags)


@app.route('/book/<int:book_id>')
def view_book(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book.html', book=book)


@app.route('/edit/<int:book_id>')
def view_edit(book_id):
    book = Book.query.get_or_404(book_id)
    all_tags = Tag.query.order_by(Tag.name).all()
    return render_template('edit.html', book=book, all_tags=all_tags)


@app.route('/file/<int:book_id>')
def view_file(book_id):
    book = Book.query.get_or_404(book_id)
    path = book.abs_filepath()
    if path and os.path.isfile(path):
        return send_file(path, download_name=book.filename)
    return render_template('missing_file.html', book=book)


@app.route('/delete/<int:book_id>')
def view_delete(book_id):
    book = Book.query.get_or_404(book_id)
    confirmed = request.args.get('confirm') == 'True'
    if not confirmed:
        return render_template('delete.html', book=book, is_attachment=False)
    else:
        book.delete_files(app.logger)
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('view_list'))


@app.route('/thumbnail/<int:book_id>')
def view_thumbnail(book_id):
    book = Book.query.get_or_404(book_id)
    path = book.abs_thumbnail_path()
    if path and os.path.isfile(path):
        return send_file(path, download_name=book.thumb_filename)


@app.route('/attachment/<int:attachment_id>')
def view_attachment(attachment_id):
    atch = Attachment.query.get_or_404(attachment_id)
    path = atch.abs_filepath()
    if path and os.path.isfile(path):
        return send_file(path, download_name=atch.name)
    return render_template('missing_file.html', book=atch.book)


@app.route('/delete_attachment/<int:attachment_id>')
def delete_attachment(attachment_id):
    atch = Attachment.query.get_or_404(attachment_id)
    confirmed = request.args.get('confirm') == 'True'
    if not confirmed:
        return render_template('delete.html', book=book, is_attachment=True)
    else:
        #atch.delete_files(app.logger)
        db.session.delete(atch)
        db.session.commit()
        return redirect(url_for('view_edit', book_id=atch.book_id))


@app.route('/attachment_thumbnail/<int:attachment_id>')
def view_attachment_thumbnail(attachment_id):
    atch = Attachment.query.get_or_404(attachment_id)
    path = atch.abs_thumbnail_path()
    if path and os.path.isfile(path):
        return send_file(path, download_name=atch.thumb_filename)


@app.route('/save', methods=('POST', ))
def do_save():
    if request.method == 'POST':
        id = request.form['book_id']
        book = Book.query.get_or_404(id)
        t = request.form['title']
        st = request.form['subtitle']
        ed = request.form['edition']
        author_str = request.form['authors']

        new_attachment = request.files['attachment_file']
        if new_attachment and new_attachment.filename:
            commands.add_attachment(book, new_attachment)

        author_str = author_str.replace(',', '\n')
        author_str = author_str.replace(';', '\n')
        authors = [a.strip() for a in author_str.split('\n')]

        tag_ids = { int(tag_id) for tag_id in request.form.getlist('existing_tags') }

        new_tag_names = [t.strip() for t in request.form['new_tags'].splitlines()]
        for name in new_tag_names:
            if name:
                tag = Tag.get_or_create(name)
                tag_ids.add(tag.id)

        book.tags = Tag.get(tag_ids)

        book.title = t
        book.subtitle = st
        book.edition = ed
        book.authors = [Author.get_or_create(name) for name in authors if name != '']

        db.session.add(book)
        db.session.commit()
        return redirect(url_for('view_book', book_id=id))
