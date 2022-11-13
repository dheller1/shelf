import subprocess

import flask
from PyPDF2 import PdfReader
import os
import requests

from shelf.core.constants import UPLOAD_FOLDER
from shelf.core.isbn import ISBN
from shelf.db import Book, db, Author


def add_book(db, request, logger=None):
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

    base, ext = os.path.splitext(file.filename)
    if file and ext.lower() == '.pdf':
        new_book = Book(title=base, filename=file.filename)
        db.session.add(new_book)
        db.session.commit()  # commit here to generate ID

        id = new_book.id
        print('added new book with id:', id)
        target_dir = os.path.join(UPLOAD_FOLDER, str(id))
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        fullpath = os.path.join(target_dir, file.filename)
        file.save(fullpath)

        fullbase, _ = os.path.splitext(fullpath)
        thumb_file = fullbase + '.png'
        thumb_success = _generate_thumbnail(fullpath, thumb_file)
        if thumb_success and os.path.isfile(thumb_file):
            new_book.thumb_filename = thumb_file
            db.session.add(new_book)
            db.session.commit()

        isbn = _find_isbn_in_pdf(os.path.join(target_dir, file.filename))
        if isbn:
            new_book.isbn = isbn.digits()
            info_json = _get_book_info(isbn)
            if info_json:
                _fill_book_info_from_json(new_book, info_json, logger)
                db.session.add(new_book)
                db.session.commit()

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


def _get_book_info(isbn):
    url = f'https://openlibrary.org/isbn/{isbn.digits()}.json'
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None


def _get_author_info(url):
    url = f'https://openlibrary.org{url}.json' # e.g. https://openlibrary.org/authors/OL371447A.json
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None


def _generate_thumbnail(source_path, target_path, logger=None):
    """ Generates a .png thumbnail from the first page of the given PDF file. """
    max_size = '240x320'
    cmdline = f'magick convert -adaptive-resize {max_size} {source_path}[0] {target_path}'
    try:
        subprocess.check_call(cmdline)
        return True
    except subprocess.CalledProcessError as e:
        if logger:
            logger.warning('Failed to generate thumbnail: ' + str(e))
        return False


def _fill_book_info_from_json(book, json, logger):
    book.full_info = str(json)
    book.title = json.get('title', '')
    book.subtitle = json.get('subtitle', '')
    pub = json.get('publishers', [])
    if pub:
        book.publisher = pub[0]

    try:
        book.published_year = int(json['publish_date'])
    except:
        book.published_year = None

    try:
        isbn = json['isbn_13'][0]
    except:
        pass
    else:
        if isbn != book.isbn and logger:
            logger.warning(f'Book ISBN does not match: {book.isbn} (from PDF) vs {isbn} (openlibrary)')

    authors = []
    for author in json.get('authors', []):
        # author should be a dict such as follows: {'key': '/authors/OL9082259A'}
        author_url = author['key']
        info = _get_author_info(author_url)
        if info:
            name = info.get('name', '')
            if name:
                authors.append(Author.get_or_create(name))
    book.authors = authors
