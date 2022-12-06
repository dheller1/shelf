import os

from . import db
from shelf.core.constants import UPLOAD_FOLDER


class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

    name = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), default='')
    thumb_filename = db.Column(db.String(200), default='')  # filename of the thumbnail image

    def __repr__(self):
        return f'Attachment({self.filename})'

    def upload_dir(self):
        return os.path.join(UPLOAD_FOLDER, str(self.book_id))

    def abs_filepath(self):
        if self.filename:
            return os.path.join(self.upload_dir(), self.filename)
        return ''

    def abs_thumbnail_path(self):
        if self.thumb_filename:
            return os.path.join(self.upload_dir(), self.thumb_filename)
        return ''
