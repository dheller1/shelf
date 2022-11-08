import flask
from PyPDF2 import PdfReader
import os

from shelf.core.isbn import ISBN
from shelf.db import Book, db


UPLOAD_FOLDER = os.path.join(os.getenv('USERPROFILE'), 'shelf', 'uploads')


def add_book(db, request):
    if 'book_file' not in request.files:
        flask.flash('No file!')
        flask.redirect(request.url)
        return None
    file = request.files['book_file']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flask.flash('No selected file')
        flask.redirect(request.url)
        return None

    ext = os.path.splitext(file.filename)[1].lower()
    if file and ext == '.pdf':
        new_book = Book(title='TEMP_UNKNOWN')
        db.session.add(new_book)
        db.session.commit()

        id = new_book.id
        print('added new book with id:', id)
        target_dir = os.path.join(UPLOAD_FOLDER, str(id))
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)
        file.save(os.path.join(target_dir, file.filename))

        isbn = _find_isbn_in_pdf(os.path.join(target_dir, file.filename))

        return new_book
    return None


def _find_isbn_in_pdf(filename):
    reader = PdfReader(filename)
    for p in reader.pages:
        text = p.extract_text()
        isbn = ISBN.find(text)
        if isbn:
            return isbn
    return None