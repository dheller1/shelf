import os

from . import db
from .written_by import written_by

from shelf.core.constants import UPLOAD_FOLDER

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200), default='')
    edition = db.Column(db.String(100), default='')
    publisher = db.Column(db.String(200), default='')
    published_year = db.Column(db.Integer)

    isbn = db.Column(db.String(13), default='')  # only the digits, which should be either 10 or 13 digits

    full_info = db.Column(db.String(2000), default='')  # the full json info string

    filename = db.Column(db.String(200), default='')  # filename of the PDF
    thumb_filename = db.Column(db.String(200), default='')  # filename of the thumbnail image

    authors = db.relationship('Author', secondary=written_by, lazy='subquery', backref=db.backref('books', lazy=True))


    def __repr__(self):
        return f'Book({self.title})'

    def upload_dir(self):
        return os.path.join(UPLOAD_FOLDER, str(self.id))

    def abs_filepath(self):
        if self.filename:
            return os.path.join(self.upload_dir(), self.filename)
        return ''

    def abs_thumbnail_path(self):
        if self.thumb_filename:
            return os.path.join(self.upload_dir(), self.thumb_filename)
        return ''

    @property
    def is_file_available(self):
        return os.path.isfile(self.abs_filepath())

    @property
    def is_thumbnail_available(self):
        return os.path.isfile(self.abs_thumbnail_path())